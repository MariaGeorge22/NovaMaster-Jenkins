from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from post.models import Tag, Stream, Follow, Post, Likes
from comment.models import Comment
from post.forms import newPostForm
from comment.forms import CommentForm
from userauth.models import Profile


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse


# Create your views here.


@login_required
def home(request):
    """
    View for displaying the home page with user's posts and unfollowed users.

    Retrieves posts from followed users, unfollowed users' profiles, and
    marks posts as liked and favorite for the logged-in user.

    Template: home.html
    """
    user = request.user
    posts = Stream.objects.filter(user=user)
    group_ids = [post.post_id for post in posts]
    post_items = Post.objects.filter(id__in=group_ids).all().order_by("-posted")
    profile = Profile.objects.get(user=user)

    for post in post_items:
        post.liked = Likes.objects.filter(user=user, post=post).exists()
        post.is_favourite = profile.favourite.filter(id=post.id).exists()
        post_user_profile = Profile.objects.get(user=post.user)
        post.profilePicture = post_user_profile.picture

    all_users = User.objects.exclude(id=user.id)
    followed_users = Follow.objects.filter(follower=user).values_list(
        "following", flat=True
    )
    unfollowed_users = all_users.exclude(id__in=followed_users)
    unfollowed_users_profiles = Profile.objects.filter(user__in=unfollowed_users)

    context = {
        "posts": post_items,
        "profile": profile,
        "unfollowed_users_profiles": unfollowed_users_profiles,
    }
    return render(request, "home.html", context)


def newPost(request):
    """
    View for creating a new post.

    Accepts POST request with form data, creates a new post with associated tags,
    and redirects to the home page upon successful creation.

    Template: post.html
    """
    user = request.user.id
    tags_objs = []

    if request.method == "POST":
        form = newPostForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get("picture")
            caption = form.cleaned_data.get("caption")
            tag_form = form.cleaned_data.get("tags")
            tags_list = list(tag_form.split("#"))
            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_objs.append(t)
            p, created = Post.objects.get_or_create(
                picture=picture, caption=caption, user_id=user
            )
            p.tags.set(tags_objs)
            p.save()
            return redirect("home")
    else:
        form = newPostForm()

    context = {
        "form": form,
    }
    return render(request, "post.html", context)


def postDetail(request, post_id):
    """
    View for displaying detailed view of a post.

    Retrieves post details, associated comments, and marks if post is liked
    and favorite for the logged-in user. Allows users to add comments.

    Template: post-detail.html
    """
    post = get_object_or_404(Post, id=post_id)
    post_user_profile = Profile.objects.get(user=post.user)
    user_profile = Profile.objects.get(user=request.user)
    post.liked = Likes.objects.filter(user=request.user, post=post).exists()
    post.is_favourite = user_profile.favourite.filter(id=post.id).exists()

    comments = Comment.objects.filter(post=post).order_by("-date")
    for comment in comments:
        comment.profile = Profile.objects.get(user=comment.user)

    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return HttpResponseRedirect(reverse("post-detail", args=[post_id]))
    else:
        form = CommentForm()

    context = {
        "post": post,
        "user_profile": user_profile,
        "post_user_profile": post_user_profile,
        "comments": comments,
        "form": form,
    }
    return render(request, "post-detail.html", context)


@csrf_protect
@require_POST
def like(request, post_id):
    """
    View for handling like/unlike functionality for a post.

    Accepts POST request to like or unlike a post based on current user.
    Returns JSON response with updated like count and status.

    Requires: @csrf_protect, @require_POST decorators.
    """
    user = request.user
    post = Post.objects.get(id=post_id)
    liked = Likes.objects.filter(user=user, post=post).exists()

    if liked:
        Likes.objects.filter(user=user, post=post).delete()
        post.likes -= 1
        liked = False
    else:
        Likes.objects.create(user=user, post=post)
        post.likes += 1
        liked = True

    post.save()
    return JsonResponse({"likes": post.likes, "liked": liked})


@login_required
def favourite(request, post_id):
    """
    View for marking a post as favorite/unfavorite for the logged-in user.

    Accepts POST request to add or remove a post from user's favorites.
    Returns JSON response with updated favorite status.

    Requires: @login_required decorator.
    """
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)
    is_favourite = False

    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
        is_favourite = False
    else:
        profile.favourite.add(post)
        is_favourite = True

    response = {
        "is_favourite": is_favourite,
    }
    return JsonResponse(response)


@login_required
def bookmark(request):
    """
    View for displaying user's bookmarked posts.

    Retrieves user's favorite posts, marks if liked and favorite,
    and displays in bookmarks template.

    Template: bookmarks.html
    """
    user = request.user
    profile = Profile.objects.get(user=user)
    post_items = profile.favourite.all()

    for post in post_items:
        post.liked = Likes.objects.filter(user=user, post=post).exists()
        post.is_favourite = profile.favourite.filter(id=post.id).exists()
        post_user_profile = Profile.objects.get(user=post.user)
        post.profilePicture = post_user_profile.picture

    context = {
        "posts": post_items,
        "profile": profile,
    }
    return render(request, "bookmarks.html", context)
