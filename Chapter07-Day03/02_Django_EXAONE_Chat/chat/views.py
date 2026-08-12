import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PreferenceForm, SignUpForm
from .models import Conversation, Message, UserPreference
from .ollama import ask_ollama, generate_title, stream_ollama

CONTEXT_INSTRUCTION = """당신은 이전 대화를 이어서 답하는 대화형 AI입니다.
대화 기록을 시간 순서대로 읽고 사용자의 마지막 메시지를 반드시 앞선 맥락과 연결해 해석하세요.
마지막 메시지가 짧거나 주어와 목적어가 생략되어 있으면 직전 질문과 답변을 바탕으로 자연스럽게 의미를 복원하세요.
이미 대화에서 확인할 수 있는 내용을 다시 묻지 말고, 합리적으로 추론할 수 있으면 바로 요청을 수행하세요.
앞선 맥락만으로 여러 해석이 가능할 때에만 짧게 확인 질문을 하세요."""


def signup(request):
    if request.user.is_authenticated:
        return redirect("chat")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserPreference.objects.create(user=user)
            login(request, user)
            return redirect("chat")
    else:
        form = SignUpForm()
    return render(request, "chat/signup.html", {"form": form})


def _current_conversation(user, conversation_id=None):
    orphans = user.chat_messages.filter(conversation__isnull=True)
    if orphans.exists():
        previous = Conversation.objects.create(user=user, title="이전 대화")
        orphans.update(conversation=previous)
    if conversation_id is not None:
        conversation = get_object_or_404(
            Conversation, id=conversation_id, user=user
        )
    else:
        conversation = user.conversations.first() or Conversation.objects.create(
            user=user
        )

    # 새 채팅을 여러 번 눌러 생긴 다른 빈 대화는 남기지 않습니다.
    user.conversations.filter(messages__isnull=True).exclude(
        id=conversation.id
    ).delete()
    return conversation


def _save_prompt(user, conversation, prompt):
    Message.objects.create(
        user=user, conversation=conversation, role="user", content=prompt
    )
    # 스트리밍이 중단되거나 브라우저가 닫혀도 최소한의 제목은 남깁니다.
    if not conversation.title_is_custom and conversation.title == "새 대화":
        conversation.title = prompt[:40]
    conversation.save()


def _ollama_messages(conversation, preference):
    # 생성 시간이 가까운 메시지도 기본키를 기준으로 확실하게 정렬합니다.
    recent = list(conversation.messages.order_by("-created_at", "-id")[:12])
    recent.reverse()
    return [
        {
            "role": "system",
            "content": f"{CONTEXT_INSTRUCTION}\n\n사용자 개인 설정:\n{preference.system_prompt}",
        },
        *[{"role": item.role, "content": item.content} for item in recent],
    ]


def _update_auto_title(conversation):
    conversation.refresh_from_db(fields=["title", "title_is_custom"])
    first_user = conversation.messages.filter(role="user").first()
    old_auto_title = first_user.content[:40] if first_user else ""
    if conversation.title_is_custom or conversation.title not in {
        "새 대화",
        "이전 대화",
        old_auto_title,
    }:
        return conversation.title
    recent = list(conversation.messages.order_by("-created_at", "-id")[:6])
    recent.reverse()
    try:
        title = generate_title(
            [{"role": item.role, "content": item.content} for item in recent]
        )
    except RuntimeError:
        title = old_auto_title or "새 대화"
    conversation.title = title
    conversation.save(update_fields=["title", "updated_at"])
    return title


def _streaming_response(user, conversation, request_messages, temperature):
    def generate():
        chunks = []
        saved = False
        try:
            for chunk in stream_ollama(request_messages, temperature):
                chunks.append(chunk)
                yield json.dumps(
                    {"type": "chunk", "content": chunk}, ensure_ascii=False
                ) + "\n"
            answer = "".join(chunks)
            if answer:
                Message.objects.create(
                    user=user,
                    conversation=conversation,
                    role="assistant",
                    content=answer,
                )
                saved = True
            yield json.dumps(
                {"type": "done", "title": conversation.title}, ensure_ascii=False
            ) + "\n"
        except RuntimeError as error:
            yield json.dumps(
                {"type": "error", "message": str(error)}, ensure_ascii=False
            ) + "\n"
        finally:
            # 브라우저에서 생성을 중지해도 이미 생성된 부분은 보존합니다.
            if chunks and not saved:
                Message.objects.create(
                    user=user,
                    conversation=conversation,
                    role="assistant",
                    content="".join(chunks),
                )

    response = StreamingHttpResponse(
        generate(), content_type="application/x-ndjson; charset=utf-8"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@login_required
def chat(request, conversation_id=None):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    conversation = _current_conversation(request.user, conversation_id)

    # JavaScript를 사용할 수 없는 브라우저를 위한 일반 전송 방식입니다.
    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        if prompt:
            _save_prompt(request.user, conversation, prompt)
            try:
                request_messages = _ollama_messages(conversation, preference)
                answer = ask_ollama(request_messages, preference.temperature)
                Message.objects.create(
                    user=request.user,
                    conversation=conversation,
                    role="assistant",
                    content=answer,
                )
                _update_auto_title(conversation)
            except (RuntimeError, KeyError, ValueError) as error:
                messages.error(request, str(error))
        return redirect("conversation", conversation_id=conversation.id)

    return render(
        request,
        "chat/chat.html",
        {
            "chat_messages": conversation.messages.all(),
            "conversation": conversation,
            "conversations": request.user.conversations.annotate(
                message_count=Count("messages")
            ).filter(message_count__gt=0),
            "preference": preference,
        },
    )


@login_required
def stream_chat(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)
    prompt = request.POST.get("prompt", "").strip()
    if not prompt:
        return JsonResponse({"error": "메시지를 입력하세요."}, status=400)

    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    _save_prompt(request.user, conversation, prompt)
    request_messages = _ollama_messages(conversation, preference)
    return _streaming_response(
        request.user,
        conversation,
        request_messages,
        preference.temperature,
    )


@login_required
def regenerate_chat(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)

    last_message = conversation.messages.order_by("-created_at", "-id").first()
    if not last_message or last_message.role != "assistant":
        return JsonResponse({"error": "다시 생성할 답변이 없습니다."}, status=400)

    last_message.delete()
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    return _streaming_response(
        request.user,
        conversation,
        _ollama_messages(conversation, preference),
        preference.temperature,
    )


@login_required
def generate_chat_title(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)
    return JsonResponse({"title": _update_auto_title(conversation)})


@login_required
def new_chat(request):
    if request.method != "POST":
        return redirect("chat")
    request.user.conversations.filter(messages__isnull=True).delete()
    conversation = Conversation.objects.create(user=request.user)
    return redirect("conversation", conversation_id=conversation.id)


@login_required
def rename_chat(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)
    title = request.POST.get("title", "").strip()[:80]
    if title:
        conversation.title = title
        conversation.title_is_custom = True
        conversation.save(update_fields=["title", "title_is_custom", "updated_at"])
        messages.success(request, "대화 이름을 수정했습니다.")
    else:
        messages.error(request, "대화 이름을 입력하세요.")
    return redirect("conversation", conversation_id=conversation.id)


@login_required
def delete_chat(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, user=request.user
    )
    if request.method != "POST":
        return redirect("conversation", conversation_id=conversation.id)
    conversation.delete()
    messages.success(request, "대화를 삭제했습니다.")
    next_conversation = request.user.conversations.first()
    if next_conversation:
        return redirect("conversation", conversation_id=next_conversation.id)
    return redirect("chat")


@login_required
def settings_view(request):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = PreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, "개인 설정을 저장했습니다.")
            return redirect("settings")
    else:
        form = PreferenceForm(instance=preference)
    return render(request, "chat/settings.html", {"form": form})


@login_required
def update_temperature(request):
    if request.method != "POST":
        return redirect("chat")
    try:
        temperature = round(float(request.POST.get("temperature", "")), 1)
    except (TypeError, ValueError):
        return JsonResponse({"error": "올바른 창의성 값을 선택하세요."}, status=400)
    if not 0.0 <= temperature <= 1.5:
        return JsonResponse({"error": "창의성 값은 0.0에서 1.5 사이여야 합니다."}, status=400)

    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    preference.temperature = temperature
    preference.save(update_fields=["temperature"])
    return JsonResponse({"temperature": temperature})
