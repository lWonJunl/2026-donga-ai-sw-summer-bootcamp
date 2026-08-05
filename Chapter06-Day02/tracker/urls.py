from django.urls import path

from . import views


urlpatterns = [
    path("sw.js", views.service_worker, name="service_worker"),
    path(
        "accounts/verify/<str:token>/",
        views.verify_email,
        name="verify_email",
    ),
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("courses/", views.courses, name="courses"),
    path("guide/", views.guide, name="guide"),
    path("mypage/", views.my_page, name="my_page"),
    path("mypage/delete/", views.delete_account, name="delete_account"),
    path("push/subscribe/", views.save_push_subscription, name="push_subscribe"),
    path(
        "push/unsubscribe/",
        views.delete_push_subscription,
        name="push_unsubscribe",
    ),
    path("push/test/", views.send_test_push, name="push_test"),
    path("groups/new/", views.create_group, name="create_group"),
    path("groups/join/", views.join_group, name="join_group"),
    path("groups/<int:group_id>/", views.group_detail, name="group_detail"),
    path(
        "groups/<int:group_id>/manage/",
        views.group_manage,
        name="group_manage",
    ),
    path(
        "groups/<int:group_id>/leave/",
        views.leave_group,
        name="leave_group",
    ),
    path(
        "groups/<int:group_id>/edit/",
        views.edit_group,
        name="edit_group",
    ),
    path(
        "groups/<int:group_id>/delete/",
        views.delete_group,
        name="delete_group",
    ),
    path(
        "groups/<int:group_id>/assignments/new/",
        views.create_assignment,
        name="create_assignment",
    ),
    path(
        "assignments/<int:assignment_id>/edit/",
        views.edit_assignment,
        name="edit_assignment",
    ),
    path(
        "assignments/<int:assignment_id>/delete/",
        views.delete_assignment,
        name="delete_assignment",
    ),
    path(
        "memberships/<int:membership_id>/manage/",
        views.manage_member,
        name="manage_member",
    ),
    path(
        "assignments/<int:assignment_id>/progress/",
        views.update_progress,
        name="update_progress",
    ),
]
