# Stripe Payment Gateway Integration
import stripe
import os
from django.conf import settings
from decimal import Decimal

# Initialize Stripe with API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class StripePaymentService:
    """Service for handling Stripe payments and subscriptions"""
    
    @staticmethod
    def create_customer(email, name):
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                description=f'Video Streaming Platform - {name}'
            )
            return customer
        except stripe.error.StripeError as e:
            raise Exception(f'Failed to create customer: {str(e)}')
    
    @staticmethod
    def create_subscription(customer_id, price_id):
        """Create a new subscription for a customer"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent']
            )
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f'Failed to create subscription: {str(e)}')
    
    @staticmethod
    def cancel_subscription(subscription_id):
        """Cancel an active subscription"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f'Failed to cancel subscription: {str(e)}')
    
    @staticmethod
    def create_payment_intent(amount, currency='usd', customer_id=None):
        """Create a one-time payment intent"""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                customer=customer_id,
                automatic_payment_methods={'enabled': True}
            )
            return payment_intent
        except stripe.error.StripeError as e:
            raise Exception(f'Failed to create payment intent: {str(e)}')
    
    @staticmethod
    def retrieve_subscription(subscription_id):
        """Retrieve subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f'Failed to retrieve subscription: {str(e)}')
    
    @staticmethod
    def list_products():
        """List all available subscription products"""
        try:
            products = stripe.Product.list(active=True)
            return products
        except stripe.error.StripeError as e:
            raise Exception(f'Failed to list products: {str(e)}')
    
    @staticmethod
    def create_checkout_session(customer_id, price_id, success_url, cancel_url):
        """Create a Stripe Checkout session for subscription"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{'price': price_id, 'quantity': 1}],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url
            )
            return session
        except stripe.error.StripeError as e:
            raise Exception(f'Failed to create checkout session: {str(e)}')
    
    @staticmethod
    def construct_webhook_event(payload, sig_header):
        """Verify and construct webhook event from Stripe"""
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f'Invalid signature: {str(e)}')

# Subscription Plan Templates
SUBSCRIPTION_PLANS = {
    'basic': {
        'name': 'Basic Plan',
        'price': 9.99,
        'features': ['SD Quality', 'Limited Content', '1 Device']
    },
    'standard': {
        'name': 'Standard Plan',
        'price': 14.99,
        'features': ['HD Quality', 'Full Content', '2 Devices']
    },
    'premium': {
        'name': 'Premium Plan',
        'price': 19.99,
        'features': ['4K Quality', 'Full Content + Exclusives', '4 Devices']
    }
}
