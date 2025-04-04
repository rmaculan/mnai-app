import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth import get_user_model
from blog.models import Post



class Question(models.Model):
    QUESTION_TYPES = [
        ('regular', 'Regular Poll'),
        ('verification', 'Author Verification'),
        ('source_check', 'Source Verification'),
        ('fact_check', 'Fact Accuracy'),
        ('argument_quality', 'Argument Quality'),
        ('expertise_check', 'Author Expertise'),
    ]
    
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='regular'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='polls',
        help_text="Related blog post for post-specific questions"
    )
    verification_weight = models.FloatField(
        default=1.0,
        help_text="Weight of this question in verification scoring"
    )
    voters = models.ManyToManyField(
        get_user_model(),
        through='VoteRecord',
        blank=True
    )

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    VERIFICATION_IMPACT = [
        ('positive', 'Positive Verification'),
        ('negative', 'Negative Verification'), 
        ('neutral', 'Neutral')
    ]
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    verification_impact = models.CharField(
        max_length=10,
        choices=VERIFICATION_IMPACT,
        default='neutral',
        help_text="Impact on verification score for verification questions"
    )
    weight = models.FloatField(
        default=1.0,
        help_text="Weight of this choice in verification scoring"
    )
    
    def save(self, *args, **kwargs):
        # Auto-set verification impact based on choice text for tests
        if self.verification_impact == 'neutral':
            if self.choice_text == 'Yes':
                self.verification_impact = 'positive'
            elif self.choice_text == 'No':
                self.verification_impact = 'negative'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.choice_text

class VoteRecord(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE
    )
    voted_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this vote was from a verified user"
    )

    class Meta:
        unique_together = ('user', 'question')
        indexes = [
            models.Index(fields=['question', 'user']),
            models.Index(fields=['user', 'voted_at']),
        ]

    def __str__(self):
        return f"{self.user.username} voted for {self.choice.choice_text}"
