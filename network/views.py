from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Post, Follow
from django.shortcuts import get_object_or_404



def index(request):
    if request.method == "POST":
        content = request.POST.get("content")
        if content and request.user.is_authenticated:
            Post.objects.create(user=request.user, content=content)
            return redirect("index")

    posts = Post.objects.all().order_by("-timestamp")
    
    return render(request, "network/index.html", {
        "posts": posts
    })


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.all().order_by("-timestamp")
    
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(user=request.user, following_user=profile_user).exists()

    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
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
