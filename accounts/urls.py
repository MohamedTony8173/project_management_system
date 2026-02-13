from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy

from .views import (
    ProfileList,
    DashboardView,
    account_login,
    account_logout,
    UserDetailView,
    email_activated,
    register,
    UserEditView
)

app_name = "accounts"


urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("register/", register, name="register"),
    path("activate/<uidb64>/<token>/", email_activated, name="activate"),
    path("login/", account_login, name="login"),
    path("profile/list/", ProfileList.as_view(), name="profile_list"),
    path("profile/detail/<int:pk>/", UserDetailView.as_view(), name="profile_user"),
    path("profile/edit/<int:pk>/", UserEditView.as_view(), name="profile_edit"),
    path("logout/", account_logout, name="logout"),
    # reset password
    path(
        "reset-password/",
        PasswordResetView.as_view(
            template_name="accounts/reset/pws_reset.html",
            email_template_name="accounts/reset/pws_reset_email.html",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "reset-password-done/",
        PasswordResetDoneView.as_view(
            template_name="accounts/reset/pws_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset-password/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="accounts/reset/pws_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        PasswordResetCompleteView.as_view(
            template_name="accounts/reset/pws_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]


