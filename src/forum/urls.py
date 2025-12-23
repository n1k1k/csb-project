from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("post/<int:post_id>/", views.post, name="post"),
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("signup/", views.signup, name="signup"),
]
