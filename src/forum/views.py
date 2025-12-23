from urllib.parse import urlencode

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Comment, Post


def index(request):
    error_message = None

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if not request.user.is_authenticated:
            login_url = (
                f"{reverse('login')}?{urlencode({'next': request.get_full_path()})}"
            )
            return redirect(login_url)

        if not title or not content:
            error_message = "Title and content are required."
        else:
            # ❌ A03:2021 – Injection (VULNERABLE RAW SQL)
            sql = f"""
            INSERT INTO forum_post (title, content, user_id)
            VALUES ('{title}', '{content}', {request.user.id});
            """

            with connection.cursor() as cursor:
                cursor.executescript(sql)

            # ✅ SAFE ORM USAGE
            # Post.objects.create(title=title, content=content, user=request.user)

            return redirect("index")

    posts_list = Post.objects.all()
    context = {
        "posts_list": posts_list,
        "error_message": error_message,
    }
    return render(request, "forum/index.html", context)


def post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    error_message = None

    if request.method == "POST":
        comment_text = request.POST.get("comment_text", "").strip()

        if not request.user.is_authenticated:
            login_url = (
                f"{reverse('login')}?{urlencode({'next': request.get_full_path()})}"
            )
            return redirect(login_url)

        if not comment_text:
            error_message = "Comment text is required."
        else:
            Comment.objects.create(
                post=post, comment_text=comment_text, user=request.user
            )
            return redirect("post", post_id=post_id)

    comments = post.comment_set.all()
    return render(
        request,
        "forum/post.html",
        {"post": post, "comments": comments, "error_message": error_message},
    )


def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "registration/profile.html", {"user": user})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
