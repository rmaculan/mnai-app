from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('stripe', 'Stripe'),
        ('blockchain', 'Blockchain'),
        ('crypto', 'Cryptocurrency'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.ForeignKey(
        'PaymentMethod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Stripe-specific fields
    stripe_payment_intent = models.CharField(max_length=100, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Blockchain-specific fields
    transaction_hash = models.CharField(max_length=100, null=True, blank=True, unique=True)
    wallet_address = models.CharField(max_length=100, null=True, blank=True)
    blockchain_network = models.CharField(max_length=50, null=True, blank=True)
    confirmation_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} ({self.status})"

class PaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method_type = models.CharField(max_length=20, choices=[
        ('stripe', 'Stripe'), 
        ('blockchain', 'Blockchain')
    ])
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)
    blockchain_wallet = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.method_type}"

    def clean(self):
        if self.method_type == 'stripe' and not self.stripe_customer_id:
            raise ValidationError('Stripe customer ID is required for Stripe payment method')
        if self.method_type == 'blockchain' and not self.blockchain_wallet:
            raise ValidationError('Blockchain wallet address is required for Blockchain payment method')
        if self.method_type != 'stripe' and self.stripe_customer_id:
            raise ValidationError('Stripe customer ID should only be set for Stripe payment method')
        if self.method_type != 'blockchain' and self.blockchain_wallet:
            raise ValidationError('Blockchain wallet should only be set for Blockchain payment method')

class Subscription(models.Model):
    PLAN_TYPES = [
        ('monthly', 'Monthly'),
        ('pay_as_you_go', 'Pay As You Go'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    current_period_end = models.DateTimeField()
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default='monthly')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} Subscription"
