from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
<<<<<<< HEAD
        fields = ['title', 'subtitle', 'job_title','content', 'picture', 'caption']
=======
        fields = ['title', 'subtitle', 'job_title','content', 'picture', 'caption', 'video']
>>>>>>> origin/main

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']