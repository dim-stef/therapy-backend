import os
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, mixins, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from accounts.models import User
from therapist.models import Therapist
from . import serializers


class UserMeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)


class TherapistsViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    serializer_class = serializers.TherapistSerializer

    def get_queryset(self):
        return Therapist.objects.all()


@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def get_stripe_publishable_key(request):
    return Response({'key': os.environ.get('STRIPE_PUBLISHABLE_KEY')})


@csrf_exempt
@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def create_checkout_session(request):
    domain_url = request.scheme + '://' + request.get_host() + '/'
    if settings.DEBUG:
        domain_url = domain_url.replace('8000', '3000')

    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - capture the payment later
        # [customer_email] - prefill the email input in the form
        # For full details see https://stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + 'cancelled/',
            payment_method_types=['card'],
            mode='payment',
            line_items=[
                {
                    'name': 'test',
                    'quantity': 1,
                    'currency': 'usd',
                    'amount': '2000',
                }
            ]
        )
        return Response({'sessionId': checkout_session['id']})
    except Exception as e:
        return Response({'error': str(e)})
