from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from .forms import PostForm, CommentForm
from django.core.files.storage import default_storage
from PIL import Image
from .models import Post, Comment, Likes, Follow
from authy.models import Profile
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect

import logging

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

def profile(request):
    return render(request, 'blog/profile.html')

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

def update_blog_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:index') 
    else:
        form = PostForm(instance=post) 

    return render(request, 'blog/update_blog_post.html', {'form': form, 'post_id': post_id})

def delete_blog_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('blog:index')

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




