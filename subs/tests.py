from django.test import TestCase
from decimal import Decimal
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from .models import Payment, PaymentMethod, Subscription
from django.core.exceptions import ValidationError

User = get_user_model()

class PaymentSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create payment methods
        self.stripe_pm = PaymentMethod.objects.create(
            user=self.user,
            method_type='stripe',
            stripe_customer_id='cus_test123'
        )
        
        self.blockchain_pm = PaymentMethod.objects.create(
            user=self.user,
            method_type='blockchain',
            blockchain_wallet='0x1234567890abcdef'
        )

    def test_create_stripe_payment(self):
        payment = Payment.objects.create(
            user=self.user,
            amount=29.99,
            currency='USD',
            payment_method=self.stripe_pm,
            stripe_payment_intent='pi_test123',
            status='completed'
        )
        
        self.assertEqual(payment.payment_method.method_type, 'stripe')
        self.assertEqual(payment.payment_method.stripe_customer_id, 'cus_test123')
        self.assertIsNone(payment.transaction_hash)

    def test_create_blockchain_payment(self):
        payment = Payment.objects.create(
            user=self.user,
            amount=0.5,
            currency='ETH',
            payment_method=self.blockchain_pm,
            transaction_hash='0x123abc',
            blockchain_network='Ethereum',
            wallet_address='0x1234567890abcdef',
            confirmation_count=12,
            status='completed'
        )
        
        self.assertEqual(payment.payment_method.method_type, 'blockchain')
        self.assertEqual(payment.blockchain_network, 'Ethereum')
        self.assertEqual(payment.confirmation_count, 12)

    def test_transaction_hash_uniqueness(self):
        Payment.objects.create(
            user=self.user,
            amount=1.0,
            currency='BTC',
            payment_method=self.blockchain_pm,
            transaction_hash='0xunique123',
            blockchain_network='Bitcoin',
            status='completed'
        )
        
        with self.assertRaises(IntegrityError):
            Payment.objects.create(
                user=self.user,
                amount=2.0,
                currency='BTC',
                payment_method=self.blockchain_pm,
                transaction_hash='0xunique123',
                blockchain_network='Bitcoin',
                status='completed'
            )

    def test_subscription_creation(self):
        subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_test123',
            status='active',
            current_period_end='2025-05-03T15:04:54Z',
            plan_type='monthly',
            payment_method=self.stripe_pm
        )
        
        self.assertEqual(subscription.plan_type, 'monthly')
        self.assertEqual(subscription.payment_method, self.stripe_pm)
        
    def test_payment_method_validation(self):
        # Test invalid payment method combination
        with self.assertRaises(ValidationError):
            invalid_pm = PaymentMethod(
                user=self.user,
                method_type='blockchain',
                stripe_customer_id='invalid_stripe_id'
            )
            invalid_pm.full_clean()

    def test_payment_status_flow(self):
        payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('19.99'),
            currency='USD',
            payment_method=self.stripe_pm,
            status='pending'
        )
        
        # Test status transition
        payment.status = 'completed'
        payment.full_clean()
        payment.save()
        
        self.assertEqual(payment.status, 'completed')

    def test_pay_as_you_go_subscription(self):
        subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='payg_test123',
            status='active',
            current_period_end='2025-05-03T15:04:54Z',
            plan_type='pay_as_you_go',
            payment_method=self.stripe_pm
        )
        
        self.assertEqual(subscription.plan_type, 'pay_as_you_go')
        self.assertTrue(subscription.payment_method.stripe_customer_id)
