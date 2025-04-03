from django.contrib import admin
from .models import Payment, PaymentMethod, Subscription

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'payment_method', 'status')
    list_filter = ('payment_method', 'status')
    search_fields = ('user__email', 'stripe_payment_intent', 'transaction_hash')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'current_period_end', 'payment_method')
    search_fields = ('user__email', 'stripe_subscription_id')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'method_type', 'stripe_customer_id', 'blockchain_wallet')
    search_fields = ('user__email', 'stripe_customer_id', 'blockchain_wallet')
