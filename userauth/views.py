from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.urls import resolve, reverse
from django.http import HttpResponseRedirect
from post.models import Post, Follow, Stream, Likes
from userauth.models import Profile
from django.core.paginator import Paginator
from django.db import transaction
from userauth.forms import EditProfileForm, UserRegisterForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.db import IntegrityError


# Create your views here.


def userProfile(request, username):
    """
    View for displaying user profile details.

    Retrieves user's profile information, posts, and profile statistics.
    Checks if logged-in user follows the profile owner.

    Template: profile.html
    """
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(user=user).order_by("-posted")
    logged_user_profile = Profile.objects.get(user=request.user)

    for post in posts:
        post.liked = Likes.objects.filter(user=request.user, post=post).exists()
        post.is_favourite = logged_user_profile.favourite.filter(id=post.id).exists()

    post_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists

    context = {
        "posts": posts,
        "profile": profile,
        "post_count": post_count,
        "following_count": following_count,
        "followers_count": followers_count,
        "follow_status": follow_status,
    }
    return render(request, "profile.html", context)


def follow(request, username, option):
    """
    View for following/unfollowing a user.

    Accepts POST request to follow or unfollow a user based on option (0 or 1).
    Updates the follow status and streams for the logged-in user.

    Redirects to the user's profile page after action.

    Requires: @login_required decorator.
    """
    user = request.user
    following = get_object_or_404(User, username=username)
    try:
        f, created = Follow.objects.get_or_create(follower=user, following=following)
        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[0:10]
            with transaction.atomic():
                for post in posts:
                    stream = Stream(
                        post=post, user=user, date=post.posted, following=following
                    )
                    stream.save()
        return HttpResponseRedirect(reverse("profile", args=[username]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("profile", args=[username]))


def editProfile(request):
    """
    View for editing user profile details.

    Retrieves logged-in user's profile details and allows editing of profile fields.
    Updates both user and profile models upon form submission.

    Template: edit-profile.html
    """
    user = request.user
    profile = Profile.objects.get(user__id=user.id)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile.picture = form.cleaned_data.get("picture")
            profile.first_name = form.cleaned_data.get("first_name")
            profile.last_name = form.cleaned_data.get("last_name")
            profile.location = form.cleaned_data.get("location")
            profile.bio = form.cleaned_data.get("bio")
            profile.save()

            user.first_name = form.cleaned_data.get("first_name")
            user.last_name = form.cleaned_data.get("last_name")
            user.save()
            return redirect("profile", profile.user.username)
    else:
        form = EditProfileForm(instance=profile)

    context = {
        "form": form,
    }
    return render(request, "edit-profile.html", context)


def register(request):
    """
    View for user registration.

    Accepts POST request to register a new user.
    Creates a new user and corresponding profile upon successful registration.
    Logs in the user automatically upon registration.

    Template: signup.html
    """
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            try:
                profile = Profile.objects.get(user=new_user)
            except Profile.DoesNotExist:
                # If profile does not exist, create a new one
                profile = Profile(user=new_user)
                profile.save()

            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Account created successfully for {username}. You are now logged in.",
            )

            # Automatically Log In The User
            new_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            if new_user is not None:
                login(request, new_user)
                return redirect(
                    "home"
                )  # Redirect after successful registration and login
            else:
                messages.error(
                    request, "Failed to log in. Please check your credentials."
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            return redirect(
                "sign-up"
            )  # Redirect back to sign-up page if form is invalid

    elif request.user.is_authenticated:
        return redirect("home")  # Redirect logged-in users away from sign-up page
    else:
        form = UserRegisterForm()

    context = {
        "form": form,
    }
    return render(request, "signup.html", context)


def custom_logout(request):
    """
    View for logging out a user.

    Logs out the current user and redirects to the sign-in page.

    """
    logout(request)
    messages.success(
        request, "You have been logged out successfully."
    )  # Optional message
    return redirect("sign-in")
