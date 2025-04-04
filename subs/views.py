from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.views import generic
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import stripe
from decimal import Decimal, InvalidOperation
from web3 import Web3
import os
import json
import logging
from .models import Subscription

logger = logging.getLogger(__name__)

# Payment system core views
class PaymentMethodListView(generic.ListView):
    model = Subscription
    template_name = 'subs/payment_methods.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_key'] = settings.STRIPE_PUBLIC_KEY
        context['crypto_wallets'] = settings.ACCEPTED_CRYPTO_WALLETS
        return context

def create_subscription(request):
    """Handle subscription creation for both payment types"""
    if request.method == 'POST':
        payment_type = request.POST.get('payment_type')
        
        if payment_type == 'stripe':
            return handle_stripe_subscription(request)
        elif payment_type == 'crypto':
            return handle_crypto_subscription(request)
        return HttpResponse("Invalid payment type", status=400)
    return redirect('payment_methods')

def blockchain_webhook(request):
    """Handle blockchain payment confirmations"""
    if request.method == 'POST':
        payload = json.loads(request.body)
        if validate_blockchain_payment(payload):
            try:
                process_confirmed_payment(payload)
                return HttpResponse(status=200)
            except Exception as e:
                logger.error(f"Blockchain payment processing failed: {str(e)}", exc_info=True)
                return HttpResponse(status=500)
        return HttpResponse(status=400)
    return HttpResponse(status=405)

# Stripe subscription views
def subscribe(request):
    return render(request, 'subs/subscribe.html')

def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    # Validate event type
    if event.type not in [
        'checkout.session.completed',
        'invoice.paid', 
        'customer.subscription.deleted'
    ]:
        logger.warning(f"Unhandled event type: {event.type}")
        return HttpResponse(status=200)

    # Handle events
    try:
        if event.type == 'checkout.session.completed':
            session = event.data.object
            handle_successful_payment(session)
        elif event.type == 'invoice.paid':
            invoice = event.data.object
            handle_recurring_payment(invoice)
        elif event.type == 'customer.subscription.deleted':
            subscription = event.data.object
            handle_subscription_cancellation(subscription)
            
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return HttpResponse(status=500)

    return HttpResponse(status=200)

def handle_stripe_subscription(request):
    """Create Stripe checkout session"""
    try:
        price_id = request.POST.get('price_id')
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )
        return redirect(checkout_session.url)
    except Exception as e:
        logger.error(f"Stripe subscription creation failed: {str(e)}", exc_info=True)
        return render(request, 'subs/payment_error.html', {'error': str(e)})

def handle_successful_payment(session):
    """Handle initial subscription creation"""
    try:
        subscription = stripe.Subscription.retrieve(session.subscription)
        user = User.objects.get(email=session.customer_email)
        
        Subscription.objects.update_or_create(
            user=user,
            stripe_subscription_id=subscription.id,
            defaults={
                'status': subscription.status,
                'payment_method': 'stripe',
                'plan_type': subscription.items.data[0].price.lookup_key,
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end)
            }
        )
        logger.info(f"Created subscription {subscription.id} for {user.email}")
    except Exception as e:
        logger.error(f"Subscription creation failed: {str(e)}", exc_info=True)

def handle_recurring_payment(invoice):
    """Handle recurring subscription payment"""
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=invoice.subscription)
        subscription.current_period_end = datetime.fromtimestamp(invoice.period_end)
        subscription.save()
        logger.info(f"Updated subscription {invoice.subscription} through {invoice.period_end}")
    except Subscription.DoesNotExist:
        logger.error(f"Subscription {invoice.subscription} not found for recurring payment")

def handle_subscription_cancellation(subscription):
    """Handle subscription cancellation"""
    try:
        sub = Subscription.objects.get(stripe_subscription_id=subscription.id)
        sub.status = 'canceled'
        sub.save()
        logger.info(f"Marked subscription {subscription.id} as canceled")
    except Subscription.DoesNotExist:
        logger.error(f"Subscription {subscription.id} not found for cancellation")

# Blockchain payment views
def handle_crypto_subscription(request):
    """Handle cryptocurrency subscription setup"""
    try:
        amount = Decimal(request.POST.get('amount'))
        wallet_address = request.POST.get('wallet_address')
        
        return render(request, 'subs/blockchain_payment.html', {
            'amount': amount,
            'wallet_address': wallet_address,
            'contract_address': settings.PAYMENT_CONTRACT_ADDRESS
        })
    except Exception as e:
        logger.error(f"Crypto subscription setup failed: {str(e)}", exc_info=True)
        return render(request, 'subs/payment_error.html', {'error': str(e)})

def validate_blockchain_payment(payload):
    """Validate blockchain transaction payload"""
    required_fields = ['tx_hash', 'amount', 'currency', 'wallet_address']
    if not all(field in payload for field in required_fields):
        return False
        
    try:
        w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URI')))
        tx = w3.eth.get_transaction(payload['tx_hash'])
        
        # Validate transaction matches payment details
        if tx['to'].lower() != settings.PAYMENT_CONTRACT_ADDRESS.lower():
            return False
            
        if tx['value'] < Web3.to_wei(payload['amount'], 'ether'):
            return False
            
        # Confirm transaction has enough block confirmations
        receipt = w3.eth.get_transaction_receipt(payload['tx_hash'])
        if receipt['blockNumber'] is None or w3.eth.block_number - receipt['blockNumber'] < 12:
            return False
            
        return True
    except Exception as e:
        logger.error(f"Blockchain validation error: {str(e)}", exc_info=True)
        return False

def process_confirmed_payment(payload):
    """Process validated blockchain payment"""
    try:
        user = User.objects.get(wallet_address__iexact=payload['wallet_address'])
        Subscription.objects.update_or_create(
            user=user,
            tx_hash=payload['tx_hash'],
            defaults={
                'status': 'active',
                'payment_method': 'crypto',
                'plan_type': 'custom',
                'amount': payload['amount'],
                'currency': payload['currency'],
                'expiry_date': datetime.now() + timedelta(days=30)
            }
        )
        logger.info(f"Processed crypto payment {payload['tx_hash']} for {user.username}")
    except Exception as e:
        logger.error(f"Payment processing failed: {str(e)}", exc_info=True)
        raise

def blockchain_payment(request):
    """Handle blockchain-based payments"""
    w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URI')))
    
    if request.method == 'POST':
        try:
            # Validate input
            wallet_address = request.POST.get('wallet_address', '').strip()
            amount_str = request.POST.get('amount', '0').strip()
            
            if not wallet_address:
                raise ValueError("Wallet address is required")
            if not amount_str:
                raise ValueError("Payment amount is required")
                
            try:
                amount = Decimal(amount_str)
            except InvalidOperation:
                raise ValueError("Invalid payment amount format")
                
            if amount <= Decimal('0'):
                raise ValueError("Payment amount must be positive")
                
            if not w3.is_checksum_address(wallet_address):
                try:
                    wallet_address = w3.to_checksum_address(wallet_address)
                except ValueError:
                    raise ValueError("Invalid Ethereum address format")
            
            # Convert ETH to Wei
            wei_amount = w3.to_wei(amount, 'ether')
            
            # Get contract instance
            payment_contract = w3.eth.contract(
                address=settings.PAYMENT_CONTRACT_ADDRESS,
                abi=json.loads(settings.PAYMENT_CONTRACT_ABI)
            )
            
            # Build transaction
            nonce = w3.eth.get_transaction_count(settings.PAYMENT_WALLET_ADDRESS)
            transaction = payment_contract.functions.processPayment().build_transaction({
                'chainId': 1,  # Ethereum mainnet
                'gas': 200000,
                'gasPrice': w3.to_wei('50', 'gwei'),
                'nonce': nonce,
                'value': wei_amount
            })
            
            # Sign and send transaction
            signed_txn = w3.eth.account.sign_transaction(
                transaction, 
                private_key=settings.PAYMENT_WALLET_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Processed {amount} ETH payment from {wallet_address} - TX Hash: {tx_hash.hex()}")
            return redirect('payment_success', tx_hash=tx_hash.hex())
            
        except Exception as e:
            logger.error(f"Blockchain payment error: {str(e)}", exc_info=True)
            return render(request, 'subs/blockchain_payment.html', {
                'error': f"Payment failed: {str(e)}",
                'wallet_address': wallet_address,
                'amount': amount_str
            })
    
    return render(request, 'subs/blockchain_payment.html')
