from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm, ProfileForm
from .models import Stream, Post, Comment, Like, Follow, Profile, Tag
from polls.models import Question, VoteRecord, Choice
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.utils.safestring import mark_safe
import logging
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import BlogMessage
from django.http import HttpResponseBadRequest
from chat.models import Message, Room
from notification.models import Notification

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
            post.status = 'published'  # Set status to published
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
    blog_posts = Post.objects.filter(status='published').order_by('-publish_date')
    
    # Add pagination with 10 posts per page for blog index
    paginator = Paginator(blog_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
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
        'posts': page_obj,  # Use paginated page object
        'follow_status': follow_status,
        'profiles': profiles,
        'all_authors': all_authors,
        'blog_posts': page_obj,  # Add pagination context for landing page
    }
    return render(request, 'blog/index.html', context)

def read_blog_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile = Profile.objects.get(user=post.author)
    comments = Comment.objects.filter(post=post)
    is_liked = Like.objects.filter(
        post=post, 
        user=request.user).exists()
    is_following = Follow.objects.filter(
        follower=request.user, 
        following=post.author).exists()
    
    # Get or create poll for this post
    poll, created = Question.objects.get_or_create(
        post=post,
        defaults={
            'question_text': 'Is this post credible?',
            'pub_date': timezone.now(),
            'question_type': 'verification'
        }
    )
    
    # Create default choices if poll was just created
    if created:
        Choice.objects.create(
            question=poll,
            choice_text='Yes',
            votes=0,
            verification_impact='positive'  # Set as positive impact for verification
        )
        Choice.objects.create(
            question=poll,
            choice_text='No',
            votes=0,
            verification_impact='negative'  # Set as negative impact for verification
        )
    
    # Check if user has already voted
    has_voted = False
    if request.user.is_authenticated:
        has_voted = VoteRecord.objects.filter(
            question=poll,
            user=request.user
        ).exists()
    
    # Get verification data
    choices = poll.choice_set.all()
    verification_data = {
        'score': post.verification_score,
        'status': post.verification_status,
        'author_credibility': profile.credibility_score,
        'results': {c.choice_text: c.votes for c in choices},
        'total_votes': sum(c.votes for c in choices),
        'history': profile.verification_history
    }
    
    # Check if post has a valid picture
    if not post.picture or not hasattr(post.picture, 'url'):
        post.use_default_image = True
    
    context = {
        'post': post,
        'profile': profile,
        'comments': comments,
        'is_liked': is_liked,
        'is_following': is_following,
        'poll': poll,
        'has_voted': has_voted,
        'verification_data': verification_data,
    }
    return render(
        request, 'blog/post_detail.html', context
        )

def read_my_posts(request):
    blog_posts = Post.objects.filter(
        author=request.user
        ).order_by('-publish_date')
    
    # Group posts by status
    published_posts = [post for post in blog_posts if post.status == 'published']
    draft_posts = [post for post in blog_posts if post.status == 'draft']
    
    context = {
        'posts': blog_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts
    }
    
    return render(request, 'blog/my_posts.html', context)

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
            
            # Create notification for the post author when someone comments on their post
            # Only create notification if commenter is not the post author
            if request.user != post.author:
                # Create a comment notification
                Notification.objects.create(
                    post=post,
                    sender=request.user,
                    user=post.author,
                    notification_types=2,  # Comment notification type
                    text_preview=content[:90]  # Preview of the comment
                )
            
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
        from django.db import transaction
        
        # Use a transaction to ensure database consistency
        with transaction.atomic():
            post = get_object_or_404(Post, pk=post_id)
            user = request.user
            
            # First, handle removing all related notifications to prevent duplicates
            if user != post.author:
                # Delete ALL existing like notifications from this user to prevent duplicates
                Notification.objects.filter(
                    post=post,
                    sender=user,
                    user=post.author,
                    notification_types=1
                ).delete()
            
            # Process the like action
            liked_post, created = Like.objects.get_or_create(
                post=post, user=user)
            
            # Toggle like
            if not created:
                liked_post.delete() 
                post.likes_count -= 1
                # No need to create a notification when unliking
            else:
                post.likes_count += 1
                # Only create notification if the liker is not the post author
                if user != post.author:
                    # Double-check no notifications exist before creating
                    if not Notification.objects.filter(
                        post=post,
                        sender=user,
                        user=post.author,
                        notification_types=1
                    ).exists():
                        Notification.objects.create(
                            post=post,
                            sender=user,
                            user=post.author,
                            notification_types=1,
                            text_preview="Liked your post"
                        )
        post.save()
        
        # Return JSON response for AJAX
        from django.http import JsonResponse
        return JsonResponse({'likes_count': post.likes_count})
        
    # Fallback to redirect if not AJAX
    return redirect(reverse('blog:post_detail', args=[post_id]))

@login_required
@csrf_exempt
def double_like_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        
        # First, remove any existing notifications to prevent duplicates
        if user != post.author:
            Notification.objects.filter(
                post=post,
                sender=user,
                user=post.author,
                notification_types=1
            ).delete()
        
        # Check if user already liked the post
        liked = Like.objects.filter(post=post, user=user).exists()
        
        if liked:
            # If already liked, add one more like (total becomes 2)
            post.likes_count += 1
        else:
            # If not already liked, add two likes and create the like object
            liked_post = Like.objects.create(post=post, user=user)
            post.likes_count += 2
            
        # Create a notification regardless of previous like status
        if user != post.author:
            Notification.objects.create(
                post=post,
                sender=user,
                user=post.author,
                notification_types=1,
                text_preview="Double liked your post"
            )
            
        post.save()
        
        # Return JSON response for AJAX
        from django.http import JsonResponse
        return JsonResponse({'likes_count': post.likes_count})
        
    # Fallback to redirect if not AJAX
    return redirect(reverse('blog:post_detail', args=[post_id]))

@login_required
@csrf_exempt
def dislike_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        
        # Remove any existing likes
        liked = Like.objects.filter(post=post, user=user).exists()
        if liked:
            Like.objects.filter(post=post, user=user).delete()
            post.likes_count -= 1
            # Remove any like notifications when disliked
            Notification.objects.filter(
                post=post,
                sender=user,
                user=post.author,
                notification_types=1
            ).delete()
        
        # Only create dislike notification if the disliker is not the post author
        if user != post.author:
            # Clear any existing dislike notifications to prevent duplicates
            Notification.objects.filter(
                post=post,
                sender=user,
                user=post.author,
                notification_types=5  # Dislike type
            ).delete()
            
            # Create a new dislike notification
            Notification.objects.create(
                post=post,
                sender=user,
                user=post.author,
                notification_types=5,  # Dislike notification type
                text_preview="Disliked your post"
            )
        
        post.save()
        
        # Return JSON response for AJAX
        from django.http import JsonResponse
        return JsonResponse({'likes_count': post.likes_count})
        
    # Fallback to redirect if not AJAX
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

# Blog Messages
@login_required
def contact_author_form(request, post_id):
    """Allow users to message a blog post author"""
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        if message_text:
            # Create unique room for this conversation
            room, created = Room.objects.get_or_create(
                creator=request.user,
                room_name=f"Blog_{post_id}_{request.user.username}_{post.author.username}"
            )
            
            # Create the message
            message = Message.objects.create(
                room=room,
                sender=request.user, 
                message=message_text
            )
            
            # Create blog message
            blog_message = BlogMessage.objects.create(
                room=room,
                post=post,
                message=message,
                sender=request.user,
                receiver=post.author
            )
            
            # Create notification for post author
            notification = Notification.objects.create(
                post=post,
                sender=request.user,
                user=post.author,
                notification_types=4,  # Message notification type
                text_preview=message_text[:90]  # Preview of the message
            )
            
            return redirect('chat:room', room_name=room.room_name)
    
    return render(request, 'blog/contact_author_form.html', {'post': post})

@login_required
def message_user(request, username):
    """Allow users to send direct messages to other users"""
    receiver = get_object_or_404(User, username=username)
    
    # Prevent messaging yourself
    if request.user == receiver:
        return redirect('blog:profile', username=username)
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '')
        if message_text:
            # Create unique room for this direct message conversation
            room, created = Room.objects.get_or_create(
                creator=request.user,
                room_name=f"Direct_{request.user.username}_{receiver.username}"
            )
            
            # Add both users to the room participants
            room.participant.add(request.user)
            room.participant.add(receiver)
            
            # Create the message
            message = Message.objects.create(
                room=room,
                sender=request.user, 
                receiver=receiver,
                message=message_text
            )
            
            # Create blog message (without post reference)
            blog_message = BlogMessage.objects.create(
                room=room,
                post=None,  # No associated post for direct messages
                message=message,
                sender=request.user,
                receiver=receiver
            )
            
            # Create notification for the receiver
            notification = Notification.objects.create(
                post=None,  # No post for direct messages
                sender=request.user,
                user=receiver,
                notification_types=4,  # Message notification type
                text_preview=message_text[:90]  # Preview of the message
            )
            
            return redirect('chat:room', room_name=room.room_name)
    
    return render(request, 'blog/message_user_form.html', {'receiver': receiver})

@login_required
def blog_messages(request):
    """View all blog-related conversations"""
    # Get all conversations where the user is either sender or receiver
    messages = BlogMessage.objects.filter(
        Q(receiver=request.user) | Q(sender=request.user)
    ).select_related('post', 'sender', 'receiver', 'room').order_by('-timestamp')
    
    # Group by room to show only the latest message from each conversation
    latest_messages = {}
    for message in messages:
        room_id = message.room.id
        if room_id not in latest_messages:
            latest_messages[room_id] = message
    
    # Convert dictionary values back to a list
    grouped_messages = list(latest_messages.values())
    
    # Debug information
    print(f"Blog messages query returned {len(messages)} raw messages")
    print(f"Grouped into {len(grouped_messages)} conversations")
    for msg in grouped_messages:
        print(f"Message ID: {msg.id}, Room: {msg.room}, Post: {msg.post.title}, Sender: {msg.sender.username}")
    
    # If no blog messages, try to create a test message if the user has posts
    if not grouped_messages and Post.objects.filter(author=request.user).exists():
        try:
            post = Post.objects.filter(author=request.user).first()
            test_room, created = Room.objects.get_or_create(
                creator=request.user,
                room_name=f"Test_Blog_{post.id}_{request.user.username}"
            )
            test_message = Message.objects.create(
                room=test_room,
                sender=request.user,
                message="This is a test message to verify messaging functionality."
            )
            test_blog_message = BlogMessage.objects.create(
                room=test_room,
                post=post,
                message=test_message,
                sender=request.user,
                receiver=request.user
            )
            grouped_messages = [test_blog_message]
            print(f"Created test message with ID: {test_blog_message.id}")
        except Exception as e:
            print(f"Error creating test message: {str(e)}")
    
    context = {
        'messages': grouped_messages
    }
    
    return render(request, 'blog/messages.html', context)

@login_required
def delete_blog_conversation(request, message_id):
    """Delete a blog conversation"""
    message = get_object_or_404(BlogMessage, pk=message_id)
    
    # Security check: only allow users to delete conversations they're part of
    if request.user != message.sender and request.user != message.receiver:
        return HttpResponseBadRequest("You don't have permission to delete this conversation.")
    
    if request.method == 'POST':
        # Store the room reference before deleting the message
        room = message.room
        
        # Delete the BlogMessage
        message.delete()
        
        # Check if there are no more BlogMessages for this room
        if not BlogMessage.objects.filter(room=room).exists():
            # Optionally delete the room and all its messages if needed
            pass
            
        return redirect('blog:messages')
        
    return HttpResponseBadRequest("Invalid request method.")
