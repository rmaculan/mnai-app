import uuid

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login

from .forms import CommentForm
from .models import Comment


def comments(request):
    root_comments = Comment.objects.filter(parent=None)
    return render(request, "comments.html", {"root_comments": root_comments})

def reply(request, comment_id):
    parent_comment = Comment.objects.get(pk=comment_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.parent = parent_comment

            if request.user.is_authenticated:
                new_comment.author = request.user
            else:
                # Create an anonymous user so that we don't have to be logged in
                # to make comments or replies.
                anonymous_username = f'Anonymous_{uuid.uuid4().hex[:8]}'                
                anonymous_user, created = User.objects.get_or_create(username=anonymous_username)

                if created:
                    anonymous_user.save()
                    login(request, anonymous_user)

                new_comment.author = anonymous_user

            new_comment.save()
            return redirect("comments")
    else:
        form = CommentForm()

    return render(request, "reply.html", {"comment": parent_comment, "form": form})

