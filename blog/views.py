from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm, ProfileForm
from .models import Stream, Post, Comment, Likes, Follow, Profile, Tag
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.utils.safestring import mark_safe
import logging
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

logger = logging.getLogger(__name__)
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index') 
    else:
        form = UserCreationForm()
    return render(
        request, 'blog/register.html', {'form': form}
        )

def login_view(request):
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('blog:index')
        else:
            form = AuthenticationForm()
        return render(
            request, 'blog/login.html', {'form': form}
            )

def logout_view(request):
    logger.info("Logout view accessed")
    logout(request)
    return redirect('blog:index')

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.content = mark_safe(post.content)
            post.save()
            return redirect('blog:index')
    else:
        form = PostForm()
    return render(
        request, 'blog/create_blog_post.html', {'form': form}
        )

def read_blog_posts(request):
    author = request.user
    all_authors = User.objects.all()
    blog_posts = Post.objects.all().order_by('-publish_date')
    profiles = Profile.objects.all()
    
    if request.user.is_authenticated:
        follow_status = Follow.objects.filter(
            follower=request.user, 
            following=author
        ).exists()
    else:
        follow_status = False
    
    posts = Stream.objects.filter(
        user=request.user
    ).order_by('-date') if request.user.is_authenticated else []
    
    group_ids = []
    for post in posts:
        group_ids.append(post.post_id)
    
    query = request.GET.get('q')
    if query:
        authors = User.objects.filter(
            Q(username__icontains=query)
            )
        paginator = Paginator(authors, 5)
        page_number = request.GET.get('page')
    
    context = {
        'posts': blog_posts,
        'follow_status': follow_status,
        'profiles': profiles,
        'all_authors': all_authors,
    }
    return render(request, 'blog/index.html', context)

def read_blog_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile = Profile.objects.get(user=post.author)
    comments = Comment.objects.filter(post=post)
    is_liked = Likes.objects.filter(
        post=post, 
        user=request.user).exists()
    is_following = Follow.objects.filter(
        follower=request.user, 
        following=post.author).exists()
    
    context = {
        'post': post,
        'profile': profile,
        'comments': comments,
        'is_liked': is_liked,
        'is_following': is_following,
    }
    return render(
        request, 'blog/post_detail.html', context
        )

def read_my_posts(request):
    blog_posts = Post.objects.filter(
        author=request.user
        ).order_by('-publish_date')
    return render(
        request, 'blog/my_posts.html', {'posts': blog_posts}
        )

def delete_blog_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        if request.POST.get('confirm_delete'):
            post.delete()
            return redirect('blog:index')
    
    return render(request, 'blog/delete_confirmation.html', {
        'post': post,
        'post_id': post_id
    })

# tags
def tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-publish_date')

    context = {
        'tag': tag,
        'posts': posts,
    }

    return render(request, 'blog/tag.html', context)

# comming soon
def search_posts(request):
    query = request.GET.get('query')
    blog_posts = Post.objects.filter(title__icontains=query)
    return render(request, 'blog/index.html', {'posts': blog_posts})

def search_posts_by_author(request):
    query = request.GET.get('query')
    blog_posts = Post.objects.filter(
        author__username__icontains=query
        )
    return render(request, 'blog/index.html', {'posts': blog_posts})

# view profile
def profile_view(request, username):
    if request.user.is_authenticated:
        user = get_object_or_404(
            User, 
            username=username
            )
        profile = Profile.objects.get(user=user)
        is_current_user = is_current_user_profile(
            request, 
            username
            )
        # url_name = resolve(request.path).url_name
        posts = Post.objects.filter(
            author=user).order_by('-publish_date')
        posts_count = Post.objects.filter(author=user).count()
        followers_count = Follow.objects.filter(following=user).count()
        following_count = Follow.objects.filter(follower=user).count()
        follow_status = Follow.objects.filter(
            follower=request.user, 
            following=user
            ).exists()

        context = {
            'user': user,
            'profile': profile,
            'is_current_user': is_current_user,
            'posts': posts,
            'posts_count': posts_count,
            'followers_count': followers_count,
            'following_count': following_count,
            'follow_status': follow_status,  
        }
        return render(request, 'blog/profile.html', context)
    else:
        return HttpResponseForbidden(
            "<h1>You must log in to view profiles.</h1>"
            "<p>Please <a href='/blog/login'>log in</a> or "
            "<a href='/blog/register'>register</a> to continue.</p>",
            content_type="text/html"
            )
    
def is_current_user_profile(request, username):
    return request.user.username == username

# edit profile
@login_required
def edit_profile(request):
    user = request.user.id
    profile = Profile.objects.get(user_id=user)

    if request.method == 'POST':
        form = ProfileForm(
            request.POST, 
            request.FILES, 
            instance=profile
            )
        if form.is_valid():
            profile.image = form.cleaned_data['image']
            profile.first_name = form.cleaned_data['first_name']
            profile.last_name = form.cleaned_data['last_name']
            profile.bio = form.cleaned_data['bio']
            profile.url = form.cleaned_data['url']
            profile.location = form.cleaned_data['location']
            profile.save()
            return redirect('blog:profile', 
                            profile.user.username
                            )
    else:
        form = ProfileForm(instance=request.user.profile)

    context = {
        'form': form,
        'profile': profile,
    }

    return render(request, 'blog/edit_profile.html', context)

# delete profile
@login_required
def delete_profile(request, username):
    if request.user.username != username:
        return HttpResponseForbidden(
            "You don't have permission to delete this profile."
            )

    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        if request.POST.get('confirm_delete'):
            profile.delete()
            
            # Log out the user
            logout(request)

            # Delete the user account
            user.delete()
            return redirect('blog:index')
        else:
            return render(
                    request, 
                    'blog/delete_profile_confirmation.html', 
                    {'profile': profile
                     })
    else:
        return render(request, 
                      'blog/delete_profile_confirmation.html', 
                      {'profile': profile
                       })

# Create a comment
@login_required
def create_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        content = request.POST.get('comment')
        if not content:
            print("Content is missing or empty.")
            return redirect('blog:post_detail', post_id=post_id)
        
        comment = Comment(
            post=post, 
            author=request.user, 
            content=content
            )
        
        # Attempt to assign the parent comment
        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                parent_comment = Comment.objects.get(pk=parent_id)
                comment.parent = parent_comment
            except Comment.DoesNotExist:
                print(
                    f"Parent comment with ID {parent_id} does not exist."
                    )
                return redirect('blog:post_detail', post_id=post_id)
        
        if len(content.strip()) > 0:
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)
    
    return render(request, 'blog/post_detail.html', {'post': post})

# read comments
def read_comments(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)

    context = {
        'post': post,
        'comments': comments,
    }
    return render(
        request, 
        'blog/post_detail.html', 
        context
        )

@login_required
def update_comment(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(
            post=post_id, 
            id=comment_id
            )
    except Comment.DoesNotExist:
        return HttpResponseServerError(
            "Comment does not exist.", content_type='text/plain'
            )
    
    if request.method == 'POST':
        if comment.author != request.user:
            return HttpResponseForbidden(
                "You do not have permission to edit this comment."
                )
        
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
        else:
            return render(
                request, 
                'blog/update_comment.html', 
                {'form': form}
                )
    else:
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)
        
        form = CommentForm(instance=comment)
        return render(
            request, 
            'blog/update_comment.html', 
            {'form': form}
            )

@login_required
def delete_comment(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(
            post=post_id, 
            id=comment_id
            )
    except Comment.DoesNotExist:
        return HttpResponseServerError(
            "Comment does not exist.", 
            content_type='text/plain'
            )
    
    if comment.author != request.user:
        return HttpResponseForbidden(
            "You do not have permission to delete this comment."
            )
    
    comment.delete()
    return redirect('blog:post_detail', post_id=post_id)

@login_required
@csrf_exempt
def like_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        liked_post, created = Likes.objects.get_or_create(
            post=post, user=user)
        
        # Toggle like
        if not created:
            liked_post.delete() 
            post.likes_count -= 1  
        else:
            liked_post.save()  
            post.likes_count += 1  
        post.save()
        
        return redirect(reverse('blog:post_detail', args=[post_id]))

@login_required
@csrf_exempt
def dislike_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        if Likes.objects.filter(
            post=post, 
            user=request.user).exists():
            Likes.objects.filter(
                post=post, 
                user=request.user).delete()
            post.likes_count -= 1
            post.save()
        
        return redirect(reverse('blog:post_detail', args=[post_id]))

# Follow a user
@login_required
def follow_user(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    
    # Check if the user is already following the user
    if not Follow.objects.filter(
        follower=follower, 
        following=following).exists():
        Follow.objects.create(
            follower=follower, 
            following=following)
    
    return redirect(reverse('blog:profile', args=[username]))
    
# Unfollow a user
@login_required
def unfollow_user(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    
    # Check if the user is already following the user
    if Follow.objects.filter(
        follower=follower, 
        following=following).exists():
        Follow.objects.filter(
            follower=follower, 
            following=following).delete()
    
    return redirect(reverse('blog:profile', args=[username]))

# view followers
def view_followers(request):
    followers = Follow.objects.filter(
        following=request.user
        )
    return render(
        request, 
        'blog/followers.html', 
        {'followers': followers}
        )

# view following
def view_following(request):
    following = Follow.objects.filter(
        follower=request.user
        )
    return render(
        request, 
        'blog/following.html', 
        {'following': following}
        )




