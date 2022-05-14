from django.urls import path
from authentication import views
from rest_framework_simplejwt import views as jwt_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path(
        "authenticate/", views.CustomTokenObtainPairView.as_view(), name="token_create"
    ),
    path("refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.LogoutView.as_view()),
    path("register/", views.RegisterView.as_view()),
    path("getuser/", views.GetUserData.as_view()),
    path("google/", views.GoogleSocialAuthView.as_view()),
    path("github/", views.GithubSocialAuthView.as_view()),
    path("existUsername/", views.UserNameExisits.as_view()),
    path("existEmail/", views.EmailExisits.as_view()),
    path("verifyUser/", views.VerifyUser.as_view()),
    path("changepassmail/", views.ChangePasswordMail.as_view()),
    path("resetPass/", views.ResetPassword.as_view()),
    path("hasAccess/", views.HasAccess.as_view()),
    path("isAdmin/", views.VerifyAdminStatus.as_view()),
    path("incScore/", views.UpdateUserProfile.as_view()),
    # path("setFixedData/", views.SetFixedData.as_view()),
    path("getProfile/", views.GetUserProfile.as_view()),
    path("getStaticData/", views.GetStaticData.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
