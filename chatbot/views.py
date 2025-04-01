from django.shortcuts import render, get_object_or_404, redirect
from .models import ChatSession, Chat
from .forms import ChatSessionForm

# CRUD endpoints for ChatSession

def chat_sessions_list(request):
    sessions = ChatSession.objects.all().order_by('-created_at')
    return render(request, 'chatbot/chat_sessions_list.html', {'sessions': sessions})

def chat_session_create(request):
    if request.method == 'POST':
        form = ChatSessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('chatbot:chat_sessions_list')
    else:
        form = ChatSessionForm()
    return render(request, 'chatbot/chat_session_form.html', {'form': form})

def chat_session_delete(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id)
    if request.method == 'POST':
        session.delete()
        return redirect('chatbot:chat_sessions_list')
    return render(request, 'chatbot/chat_session_confirm_delete.html', {'session': session})

# Existing chat view functions can be added below.

from django.contrib import messages
from .forms import PaymentSettingsForm

def payment_settings(request):
    if request.method == 'POST':
        form = PaymentSettingsForm(request.POST)
        if form.is_valid():
            request.session['api_key'] = form.cleaned_data['api_key']
            request.session['payment_plan'] = form.cleaned_data['payment_plan']
            messages.success(request, "Payment settings saved.")
            return redirect('payment_settings')
    else:
        initial = {
            'api_key': request.session.get('api_key', ''),
            'payment_plan': request.session.get('payment_plan', 'payg')
        }
        form = PaymentSettingsForm(initial=initial)
    return render(request, 'chatbot/payment_settings.html', {'form': form})
