import json
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from pywebpush import WebPushException, webpush

from .forms import (
    AssignmentForm,
    ClassGroupForm,
    JoinGroupForm,
    ProgressForm,
    AccountDeleteForm,
    SignupForm,
)
from .models import (
    Assignment,
    AssignmentProgress,
    ClassGroup,
    GroupMembership,
    EmailVerification,
    PushSubscription,
)
from .services import calculate_risk, remaining_text


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "tracker/landing.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            verification = EmailVerification.objects.create(user=user)
        verification_path = reverse("verify_email", args=[verification.token])
        verification_url = (
            f"{settings.SITE_URL}{verification_path}"
            if settings.SITE_URL
            else request.build_absolute_uri(verification_path)
        )
        send_mail(
            "[과제신호등] 이메일을 인증해 주세요",
            f"아래 링크를 열어 이메일 인증을 완료하세요.\n\n{verification_url}",
            None,
            [user.email],
        )
        return render(
            request,
            "registration/verification_sent.html",
            {"email": user.email},
        )
    return render(request, "registration/signup.html", {"form": form})


def verify_email(request, token):
    verification = get_object_or_404(
        EmailVerification.objects.select_related("user"), token=token
    )
    expires_at = verification.created_at + timedelta(
        seconds=settings.EMAIL_VERIFICATION_MAX_AGE_SECONDS
    )
    if timezone.now() > expires_at:
        user = verification.user
        with transaction.atomic():
            verification.delete()
            if not user.is_active:
                user.delete()
        messages.error(request, "인증 링크가 만료되었습니다. 다시 회원가입해 주세요.")
        return redirect("signup")

    with transaction.atomic():
        user = verification.user
        user.is_active = True
        user.save(update_fields=["is_active"])
        verification.delete()
    messages.success(request, "이메일 인증이 완료되었습니다. 로그인해 주세요.")
    return redirect("login")


def assignment_rows(assignments, user):
    progress_by_assignment = {
        progress.assignment_id: progress
        for progress in AssignmentProgress.objects.filter(
            user=user, assignment__in=assignments
        )
    }
    rows = []
    for assignment in assignments:
        progress = progress_by_assignment.get(assignment.id)
        status = progress.status if progress else AssignmentProgress.Status.TODO
        rows.append(
            {
                "assignment": assignment,
                "status": status,
                "status_label": AssignmentProgress.Status(status).label,
                "risk": calculate_risk(assignment.due_at, status),
                "remaining": remaining_text(assignment.due_at),
            }
        )
    return rows


def require_group_owner(group, user):
    if not GroupMembership.objects.filter(
        group=group, user=user, role=GroupMembership.Role.OWNER
    ).exists():
        raise PermissionDenied("그룹 관리자만 사용할 수 있습니다.")


@login_required
def dashboard(request):
    membership_count = GroupMembership.objects.filter(user=request.user).count()
    assignments = list(
        Assignment.objects.filter(group__memberships__user=request.user)
        .select_related("group", "created_by")
        .distinct()
    )
    rows = assignment_rows(assignments, request.user)
    completed_count = sum(
        row["status"] == AssignmentProgress.Status.DONE for row in rows
    )
    rows = [
        row
        for row in rows
        if row["status"] != AssignmentProgress.Status.DONE
    ]
    rows.sort(key=lambda row: (row["risk"].rank, row["assignment"].due_at))
    summary = {
        level: sum(row["risk"].level == level for row in rows)
        for level in ("overdue", "danger", "warning", "safe")
    }
    return render(
        request,
        "tracker/dashboard.html",
        {
            "membership_count": membership_count,
            "assignment_rows": rows,
            "summary": summary,
            "completed_count": completed_count,
            "vapid_public_key": settings.WEBPUSH_VAPID_PUBLIC_KEY,
        },
    )


@login_required
def courses(request):
    memberships = GroupMembership.objects.filter(user=request.user).select_related(
        "group"
    )
    return render(
        request,
        "tracker/courses.html",
        {"memberships": memberships},
    )


@login_required
def guide(request):
    return render(request, "tracker/guide.html")


@login_required
def my_page(request):
    return render(
        request,
        "tracker/my_page.html",
        {
            "course_count": GroupMembership.objects.filter(user=request.user).count(),
            "active_assignment_count": Assignment.objects.filter(
                group__memberships__user=request.user
            )
            .exclude(
                progress_records__in=AssignmentProgress.objects.filter(
                    user=request.user,
                    status=AssignmentProgress.Status.DONE,
                )
            )
            .distinct()
            .count(),
            "push_count": request.user.push_subscriptions.count(),
            "vapid_public_key": settings.WEBPUSH_VAPID_PUBLIC_KEY,
        },
    )


@login_required
def delete_account(request):
    form = AccountDeleteForm(request.POST or None)
    sole_owner_groups = GroupMembership.objects.filter(
        user=request.user, role=GroupMembership.Role.OWNER
    ).annotate(
        owner_count=Count(
            "group__memberships",
            filter=Q(group__memberships__role=GroupMembership.Role.OWNER),
        )
    ).filter(owner_count=1)

    if request.method == "POST" and form.is_valid():
        if not request.user.check_password(form.cleaned_data["password"]):
            form.add_error("password", "비밀번호가 올바르지 않습니다.")
        elif sole_owner_groups.exists():
            form.add_error(
                None,
                "단독 관리자인 그룹이 있습니다. 다른 관리자를 지정하거나 그룹을 삭제한 뒤 다시 시도해 주세요.",
            )
        else:
            user = request.user
            with transaction.atomic():
                user.class_memberships.all().delete()
                user.assignment_progress.all().delete()
                user.push_subscriptions.all().delete()
                EmailVerification.objects.filter(user=user).delete()
                user.username = f"deleted-user-{user.id}"
                user.email = ""
                user.first_name = ""
                user.last_name = ""
                user.is_active = False
                user.set_unusable_password()
                user.save()
            logout(request)
            messages.success(request, "회원 탈퇴가 완료되었습니다.")
            return redirect("landing")

    return render(
        request,
        "tracker/account_delete.html",
        {"form": form, "sole_owner_groups": sole_owner_groups},
    )


def service_worker(request):
    response = FileResponse(
        open(settings.BASE_DIR / "static" / "tracker" / "sw.js", "rb"),
        content_type="application/javascript",
    )
    response["Service-Worker-Allowed"] = "/"
    return response


@login_required
@require_POST
def save_push_subscription(request):
    try:
        payload = json.loads(request.body)
        endpoint = payload["endpoint"]
        keys = payload["keys"]
        p256dh = keys["p256dh"]
        auth = keys["auth"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return JsonResponse({"error": "올바르지 않은 구독 정보입니다."}, status=400)

    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={"user": request.user, "p256dh": p256dh, "auth": auth},
    )
    return JsonResponse({"ok": True})


@login_required
@require_POST
def delete_push_subscription(request):
    try:
        endpoint = json.loads(request.body)["endpoint"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return JsonResponse({"error": "올바르지 않은 구독 정보입니다."}, status=400)
    request.user.push_subscriptions.filter(endpoint=endpoint).delete()
    return JsonResponse({"ok": True})


@login_required
@require_POST
def send_test_push(request):
    if not settings.WEBPUSH_VAPID_PRIVATE_KEY or not settings.WEBPUSH_VAPID_PUBLIC_KEY:
        return JsonResponse(
            {"error": "서버에 VAPID 키가 설정되지 않았습니다."}, status=503
        )

    payload = json.dumps(
        {
            "title": "과제신호등 알림",
            "body": "푸시 알림이 정상적으로 연결되었습니다.",
            "url": "/dashboard/",
        },
        ensure_ascii=False,
    )
    sent = 0
    for subscription in request.user.push_subscriptions.all():
        try:
            webpush(
                subscription_info=subscription.as_webpush_info(),
                data=payload,
                vapid_private_key=settings.WEBPUSH_VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.WEBPUSH_VAPID_SUBJECT},
            )
            sent += 1
        except WebPushException as exc:
            if exc.response is not None and exc.response.status_code in {404, 410}:
                subscription.delete()
            else:
                return JsonResponse({"error": "푸시 발송에 실패했습니다."}, status=502)

    if not sent:
        return JsonResponse({"error": "등록된 브라우저가 없습니다."}, status=400)
    return JsonResponse({"ok": True, "sent": sent})


@login_required
def create_group(request):
    form = ClassGroupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            GroupMembership.objects.create(
                group=group, user=request.user, role=GroupMembership.Role.OWNER
            )
        messages.success(request, "과목 그룹을 만들었습니다.")
        return redirect("group_detail", group_id=group.id)
    return render(request, "tracker/group_form.html", {"form": form})


@login_required
def join_group(request):
    form = JoinGroupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["invite_code"]
        group = ClassGroup.objects.filter(invite_code=code).first()
        if group is None:
            form.add_error("invite_code", "해당 초대 코드의 그룹을 찾지 못했습니다.")
        else:
            _, created = GroupMembership.objects.get_or_create(
                group=group, user=request.user
            )
            if created:
                messages.success(request, f"{group.course_name} 그룹에 참여했습니다.")
            else:
                messages.info(request, "이미 참여 중인 그룹입니다.")
            return redirect("group_detail", group_id=group.id)
    return render(request, "tracker/join_group.html", {"form": form})


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(
        ClassGroup.objects.prefetch_related("memberships__user"),
        id=group_id,
        memberships__user=request.user,
    )
    assignments = list(group.assignments.select_related("created_by"))
    membership = GroupMembership.objects.get(group=group, user=request.user)
    return render(
        request,
        "tracker/group_detail.html",
        {
            "group": group,
            "assignment_rows": assignment_rows(assignments, request.user),
            "status_choices": AssignmentProgress.Status.choices,
            "is_owner": membership.role == GroupMembership.Role.OWNER,
        },
    )


@login_required
def group_manage(request, group_id):
    group = get_object_or_404(
        ClassGroup.objects.prefetch_related("memberships__user"), id=group_id
    )
    require_group_owner(group, request.user)
    return render(request, "tracker/group_manage.html", {"group": group})


@login_required
@require_POST
def leave_group(request, group_id):
    membership = get_object_or_404(
        GroupMembership.objects.select_related("group"),
        group_id=group_id,
        user=request.user,
    )
    if membership.role == GroupMembership.Role.OWNER:
        owner_count = membership.group.memberships.filter(
            role=GroupMembership.Role.OWNER
        ).count()
        if owner_count <= 1:
            messages.error(
                request,
                "단독 관리자는 그룹을 나갈 수 없습니다. 다른 관리자를 지정하거나 그룹을 삭제해 주세요.",
            )
            return redirect("group_detail", group_id=group_id)
    course_name = membership.group.course_name
    AssignmentProgress.objects.filter(
        user=request.user, assignment__group=membership.group
    ).delete()
    membership.delete()
    messages.success(request, f"{course_name} 그룹에서 나왔습니다.")
    return redirect("courses")


@login_required
def edit_group(request, group_id):
    group = get_object_or_404(ClassGroup, id=group_id)
    require_group_owner(group, request.user)
    form = ClassGroupForm(request.POST or None, instance=group)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "그룹 정보를 수정했습니다.")
        return redirect("group_manage", group_id=group.id)
    return render(
        request,
        "tracker/group_form.html",
        {"form": form, "group": group, "editing": True},
    )


@login_required
def create_assignment(request, group_id):
    group = get_object_or_404(
        ClassGroup, id=group_id, memberships__user=request.user
    )
    form = AssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        assignment = form.save(commit=False)
        assignment.group = group
        assignment.created_by = request.user
        assignment.save()
        messages.success(request, "그룹에 과제를 등록했습니다.")
        return redirect("group_detail", group_id=group.id)
    return render(
        request, "tracker/assignment_form.html", {"form": form, "group": group}
    )


@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(
        Assignment.objects.select_related("group"), id=assignment_id
    )
    membership = GroupMembership.objects.filter(
        group=assignment.group, user=request.user
    ).first()
    if membership is None or (
        membership.role != GroupMembership.Role.OWNER
        and assignment.created_by_id != request.user.id
    ):
        raise PermissionDenied("과제 등록자 또는 그룹 관리자만 수정할 수 있습니다.")
    form = AssignmentForm(request.POST or None, instance=assignment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "과제 정보를 수정했습니다.")
        return redirect("group_detail", group_id=assignment.group_id)
    return render(
        request,
        "tracker/assignment_form.html",
        {"form": form, "group": assignment.group, "assignment": assignment},
    )


@login_required
@require_POST
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(
        Assignment.objects.select_related("group"), id=assignment_id
    )
    membership = GroupMembership.objects.filter(
        group=assignment.group, user=request.user
    ).first()
    if membership is None or (
        membership.role != GroupMembership.Role.OWNER
        and assignment.created_by_id != request.user.id
    ):
        raise PermissionDenied("과제 등록자 또는 그룹 관리자만 삭제할 수 있습니다.")
    group_id = assignment.group_id
    assignment.delete()
    messages.success(request, "과제를 삭제했습니다.")
    return redirect("group_detail", group_id=group_id)


@login_required
@require_POST
def manage_member(request, membership_id):
    membership = get_object_or_404(
        GroupMembership.objects.select_related("group", "user"), id=membership_id
    )
    require_group_owner(membership.group, request.user)
    action = request.POST.get("action")
    owner_count = membership.group.memberships.filter(
        role=GroupMembership.Role.OWNER
    ).count()

    if action in {"remove", "make_member"} and (
        membership.role == GroupMembership.Role.OWNER and owner_count <= 1
    ):
        messages.error(request, "그룹에는 최소 한 명의 관리자가 필요합니다.")
    elif action == "remove":
        membership.delete()
        messages.success(request, "구성원을 그룹에서 내보냈습니다.")
    elif action == "make_owner":
        membership.role = GroupMembership.Role.OWNER
        membership.save(update_fields=["role"])
        messages.success(request, "구성원을 관리자로 지정했습니다.")
    elif action == "make_member":
        membership.role = GroupMembership.Role.MEMBER
        membership.save(update_fields=["role"])
        messages.success(request, "관리자 권한을 해제했습니다.")
    else:
        messages.error(request, "올바르지 않은 관리 요청입니다.")
    return redirect("group_manage", group_id=membership.group_id)


@login_required
@require_POST
def delete_group(request, group_id):
    group = get_object_or_404(ClassGroup, id=group_id)
    require_group_owner(group, request.user)
    if request.POST.get("confirmation") != group.course_name:
        messages.error(request, "과목명이 일치하지 않아 그룹을 삭제하지 않았습니다.")
        return redirect("group_manage", group_id=group.id)
    course_name = group.course_name
    group.delete()
    messages.success(request, f"{course_name} 그룹을 삭제했습니다.")
    return redirect("courses")


@login_required
@require_POST
def update_progress(request, assignment_id):
    assignment = get_object_or_404(
        Assignment, id=assignment_id, group__memberships__user=request.user
    )
    progress, _ = AssignmentProgress.objects.get_or_create(
        assignment=assignment, user=request.user
    )
    form = ProgressForm(request.POST, instance=progress)
    if form.is_valid():
        form.save()
        messages.success(request, "내 진행 상태를 변경했습니다.")
    else:
        messages.error(request, "진행 상태를 변경하지 못했습니다.")
    next_url = request.POST.get("next")
    if next_url == "dashboard":
        return redirect("dashboard")
    return redirect("group_detail", group_id=assignment.group_id)
