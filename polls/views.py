from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice, VoteRecord

# Create your views here.
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions 
        (not including those set to be published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = context['question']
        
        if question.question_type == 'verification' and question.post:
            # Calculate verification metrics
            choices = question.choice_set.all()
            poll_results = {
                question.question_type: {
                    'positive': sum(
                        c.votes for c in choices 
                        if c.verification_impact == 'positive'
                    ),
                    'negative': sum(
                        c.votes for c in choices 
                        if c.verification_impact == 'negative'
                    )
                }
            }
            
            # Update post verification score
            post = question.post
            # Extract the inner results dictionary before passing
            verification_results = poll_results[question.question_type]
            post.calculate_verification_score(verification_results)
            post.update_author_credibility()
            post.add_verification_history(verification_results)
            
            # Add to context
            context['verification_score'] = post.verification_score
            context['author_credibility'] = post.author.profile.credibility_score
            context['poll_results'] = poll_results
            
        return context


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        if request.user.is_authenticated:
            # Create vote record
            VoteRecord.objects.create(
                user=request.user,
                question=question,
                choice=selected_choice
            )
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        
        # If this is a verification poll, update verification metrics
        if question.question_type == 'verification' and question.post:
            question.refresh_from_db()  # Ensure we have latest vote counts
            choices = question.choice_set.all()
            poll_results = {
                question.question_type: {
                    'positive': sum(
                        c.votes for c in choices 
                        if c.verification_impact == 'positive'
                    ),
                    'negative': sum(
                        c.votes for c in choices 
                        if c.verification_impact == 'negative'
                    )
                }
            }
            
            # Update post verification score
            post = question.post
            # Extract the inner results dictionary before passing
            verification_results = poll_results[question.question_type]
            post.calculate_verification_score(verification_results)
            post.update_author_credibility()
            post.add_verification_history(verification_results)
        
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
