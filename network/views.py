from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Post, Follow
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import json
from django.views.decorators.csrf import csrf_exempt

@login_required
def edit_post(request, post_id):
    if request.method == "PUT":
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        if post.user != request.user:
            return JsonResponse({"error": "Permission denied."}, status=403)

        data = json.loads(request.body)
        new_content = data.get("content", "").strip()

        if not new_content:
            return JsonResponse({"error": "Content cannot be empty."}, status=400)

        post.content = new_content
        post.save()

        return JsonResponse({"message": "Post updated successfully.", "content": post.content})

    return JsonResponse({"error": "Invalid request method."}, status=400)


def index(request):
    if request.method == "POST":
        content = request.POST.get("content")
        if content and request.user.is_authenticated:
            Post.objects.create(user=request.user, content=content)
            return redirect("index")

    posts_list = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts_list = profile_user.posts.all().order_by("-timestamp")
    
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(user=request.user, following_user=profile_user).exists()

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "page_obj": page_obj,
        "followers_count": profile_user.followers.count(),
        "following_count": profile_user.following.count(),
        "is_following": is_following,
    })


def toggle_follow(request, username):
    if request.method == "POST" and request.user.is_authenticated:
        target_user = get_object_or_404(User, username=username)
        
        if request.user != target_user:
            follow_relation = Follow.objects.filter(user=request.user, following_user=target_user)
            if follow_relation.exists():
                follow_relation.delete()
            else:
                Follow.objects.create(user=request.user, following_user=target_user)

    return redirect("profile", username=username)


@login_required
def following(request):
    followed_users = Follow.objects.filter(user=request.user).values_list('following_user', flat=True)
    posts_list = Post.objects.filter(user__in=followed_users).order_by("-timestamp")

    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


@login_required
def toggle_like(request, post_id):
    if request.method == "POST":
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

        return JsonResponse({
            "liked": liked,
            "likes_count": post.likes.count()
        })

    return JsonResponse({"error": "Invalid request method."}, status=400)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
