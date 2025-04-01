from django import forms
from .models import ChatSession

class ChatSessionForm(forms.ModelForm):
    class Meta:
        model = ChatSession
        fields = ['name']

class PaymentSettingsForm(forms.Form):
    api_key = forms.CharField(
        label='API Key',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your API key'})
    )
    PAYMENT_CHOICES = [
       ('payg', 'Pay As You Go'),
       ('monthly', 'Monthly Subscription'),
    ]
    payment_plan = forms.ChoiceField(
        label='Payment Plan',
        choices=PAYMENT_CHOICES,
        required=False
    )
