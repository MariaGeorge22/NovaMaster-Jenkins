from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


urlpatterns = [
    path("<username>/", views.userProfile, name="profile"),
    path("<username>/follow/<option>", views.follow, name="follow"),
    path("edit", views.editProfile, name="edit-profile"),
    path("sign-up", views.register, name="sign-up"),
    path(
        "",
        auth_views.LoginView.as_view(
            template_name="login.html", redirect_authenticated_user=True
        ),
        name="sign-in",
    ),
    path("sign-out", views.custom_logout, name="sign-out"),
]
