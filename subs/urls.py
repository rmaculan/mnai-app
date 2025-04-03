from django.urls import path
from . import views

app_name = 'subs'

urlpatterns = [
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment_methods'),
    path('create-subscription/', views.create_subscription, name='create_subscription'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('blockchain-webhook/', views.blockchain_webhook, name='blockchain_webhook'),
    path('subscribe/', views.SubscriptionView.as_view(), name='subscribe'),
    path('success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('crypto-payment/', views.BlockchainPaymentView.as_view(), name='crypto_payment'),
]
