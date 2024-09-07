from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from .forms import PostForm, CommentForm, ProfileForm
from django.core.files.storage import default_storage
from PIL import Image
from .models import Post, Comment, Likes, Follow, Profile
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from .forms import UserRegisterForm
from django.core.exceptions import ValidationError
from django.db import transaction

from django.db.utils import IntegrityError
import logging

from django.core.paginator import Paginator
from django.urls import resolve
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json



logger = logging.getLogger(__name__)

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'index.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data['thumbnail']:
            # Process the thumbnail here
            # Example: Resizing the image
            try:
                with default_storage.open(
                    form.instance.thumbnail.name, 'rb+') as img_file:
                    img = Image.open(img_file)
                    img = img.resize((300, 300))  # Example resize
                    img.save(img_file)
            except IOError:
                pass  # Handle error
        return response
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect to a success page.
            return redirect('blog:index') 
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

def login_view(request):
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('blog:index')
        else:
            form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logger.info("Logout view accessed")
    
    logout(request)
    
    return redirect('blog:index')

# view profile
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    
    is_current_user = is_current_user_profile(request, username)

    url_name = resolve(request.path).url_name
    

    posts = Post.objects.filter(author=user).order_by('-publish_date')

    context = {
        'posts': posts,
        'profile': profile,
        'user': user,
        'is_current_user': is_current_user,
    }

    return render(request, 'blog/profile.html', context)

def is_current_user_profile(request, username):
    return request.user.username == username

# edit profile
@login_required
def edit_profile(request):
    user = request.user.id
    profile = Profile.objects.get(user_id=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile.image = form.cleaned_data['image']
            profile.first_name = form.cleaned_data['first_name']
            profile.last_name = form.cleaned_data['last_name']
            profile.bio = form.cleaned_data['bio']
            profile.url = form.cleaned_data['url']
            profile.location = form.cleaned_data['location']
            profile.save()
            return redirect('blog:profile', profile.user.username)
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
        return HttpResponseForbidden("You don't have permission to delete this profile.")

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
            return render(request, 'blog/delete_profile_confirmation.html', {'profile': profile})
    else:
        return render(request, 'blog/delete_profile_confirmation.html', {'profile': profile})

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:index')
    else:
        form = PostForm()
    return render(request, 'blog/create_blog_post.html', {'form': form})

def read_blog_posts(request):
    blog_posts = Post.objects.all().order_by('-publish_date')
    return render(
        request, 
        'blog/index.html', 
        {'posts': blog_posts,
         })

def read_my_posts(request):
    blog_posts = Post.objects.filter(author=request.user).order_by('-publish_date')
    return render(request, 'blog/my_posts.html', {'posts': blog_posts})

def read_blog_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})

# region: removed ability to update blog post permanently for blog authenticity. Blogs will be treated as news articles ###

# def update_blog_post(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
    
#     if request.method == 'POST':
#         form = PostForm(request.POST, instance=post)
#         if form.is_valid():
#             form.save()
#             return redirect('blog:index') 
#     else:
#         form = PostForm(instance=post) 

#     return render(request, 'blog/update_blog_post.html', {'form': form, 'post_id': post_id})

# endregion

def delete_blog_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        # If the POST request comes from the confirmation button, proceed with deletion
        if request.POST.get('confirm_delete'):
            post.delete()
            return redirect('blog:index')
    
    # Render the page with a confirmation dialog
    return render(request, 'blog/delete_confirmation.html', {
        'post': post,
        'post_id': post_id
    })


# comming soon
def search_posts(request):
    query = request.GET.get('query')
    blog_posts = Post.objects.filter(title__icontains=query)
    return render(request, 'blog/index.html', {'posts': blog_posts})

def search_posts_by_author(request):
    query = request.GET.get('query')
    blog_posts = Post.objects.filter(author__username__icontains=query)
    return render(request, 'blog/index.html', {'posts': blog_posts})


# Create a comment
@login_required
def create_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        content = request.POST.get('comment')
        if not content:
            print("Content is missing or empty.")
            return redirect('blog:post_detail', post_id=post_id)
        
        comment = Comment(post=post, author=request.user, content=content)
        
        # Attempt to assign the parent comment
        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                parent_comment = Comment.objects.get(pk=parent_id)
                comment.parent = parent_comment
            except Comment.DoesNotExist:
                print(f"Parent comment with ID {parent_id} does not exist.")
                return redirect('blog:post_detail', post_id=post_id)
        
        if len(content.strip()) > 0:
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)
        else:
            return redirect('blog:post_detail', post_id=post_id)
    
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def update_comment(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(post=post_id, id=comment_id)
    except Comment.DoesNotExist:
        return HttpResponseServerError("Comment does not exist.", content_type='text/plain')
    
    if request.method == 'POST':
        if comment.author != request.user:
            return HttpResponseForbidden("You do not have permission to edit this comment.")
        
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
        else:
            return render(request, 'blog/update_comment.html', {'form': form})
    else:
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)
        
        form = CommentForm(instance=comment)
        return render(request, 'blog/update_comment.html', {'form': form})

@login_required
def delete_comment(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(post=post_id, id=comment_id)
    except Comment.DoesNotExist:
        return HttpResponseServerError("Comment does not exist.", content_type='text/plain')
    
    if comment.author != request.user:
        return HttpResponseForbidden("You do not have permission to delete this comment.")
    
    comment.delete()
    return redirect('blog:post_detail', post_id=post_id)

@login_required
@csrf_exempt
def like_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        liked_post, created = Likes.objects.get_or_create(post=post, user=user)
        
        # Toggle like
        if not created:
            liked_post.delete()  # Dislike if already liked
            post.likes_count -= 1  # Decrement likes_count
        else:
            liked_post.save()  # Like the post
            post.likes_count += 1  # Increment likes_count
        post.save()  # Save the post to update likes_count in the database
        
        return redirect(reverse('blog:post_detail', args=[post_id]))

@login_required
@csrf_exempt
def dislike_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        if Likes.objects.filter(post=post, user=request.user).exists():
            Likes.objects.filter(post=post, user=request.user).delete()
            post.likes_count -= 1  # Decrement likes_count
            post.save()  # Save the post to update likes_count in the database
        
        return redirect(reverse('blog:post_detail', args=[post_id]))




