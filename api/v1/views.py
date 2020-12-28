import os
import stripe
from django.contrib.sites.models import Site
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, mixins, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from accounts.models import User, UserProfile
from therapist.models import Therapist, TherapySession, AvailableTimeRange
from . import serializers


class UserMeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)


class TherapistsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = serializers.TherapistWithSessionsSerializer

    def get_queryset(self):
        return Therapist.objects.all()


class CreateTherapySessionViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = serializers.CreateTherapySessionSerializer
    queryset = TherapySession.objects.all()

    def get_serializer_context(self):
        return {
            'user': self.request.user,
        }


class MySessionsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = serializers.TherapySessionSerializer
    lookup_field = 'surrogate'

    def get_queryset(self):
        sessions = self.request.user.sessions.all()
        if self.request.user.profile.is_therapist:
            sessions |= self.request.user.therapist.sessions.all()
        return sessions.order_by('-created')

    def get_object(self):
        return TherapySession.objects.get(surrogate=self.kwargs['surrogate'])


class ProfileViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    serializer_class = serializers.UpdateUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = UserProfile.objects.all()
    lookup_field = 'surrogate'


class UpdateUserProfileViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    serializer_class = serializers.UpdateUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        return self.request.user.profile


class UpdateTherapistProfileViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    serializer_class = serializers.UpdateTherapistProfileSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        return self.request.user.therapist


class ChangeAvailabilityTimes(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.ChangeAvailableTimesSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_queryset(self):
        return Therapist.objects.filter(surrogate=self.kwargs['surrogate'])

    def get_serializer_context(self):
        return {
            'therapist': self.kwargs['surrogate'],
        }


@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def create_direct_payment(request, stripe_id):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    domain_url = request.scheme + '://' + request.get_host() + '/'
    if settings.DEBUG:
        domain_url = domain_url.replace('8000', '3000')
    payment_intent = stripe.PaymentIntent.create(
        payment_method_types=['card'],
        amount=3000,
        currency='eur',
        application_fee_amount=600,
        transfer_data={
            'destination': stripe_id,
        }
    )

    url = payment_intent.charges.url
    return Response({'url': url})


@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def get_stripe_login(request):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    login = stripe.Account.create_login_link(f'{request.user.profile.stripe_id}')
    return Response({'url': login.url})


@api_view(http_method_names=['POST'])
@permission_classes((permissions.IsAuthenticated,))
def create_stripe_account_link(request):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    user_profile = request.user.profile

    if settings.DEBUG:
        redirect = 'http://localhost:3000/users/oauth/callback'
        refresh_url = "http://localhost:3000/reauth"

    else:
        redirect = 'https://%s%s' % (Site.objects.get_current().domain, '/users/oauth/callback')
        refresh_url = 'https://%s%s' % (Site.objects.get_current().domain, '/reauth')

    account_link = stripe.AccountLink.create(
        account=request.user.profile.stripe_id,
        refresh_url=refresh_url,
        return_url=redirect,
        type="account_onboarding",
    )

    user_profile.stripe_account_link = account_link.url
    user_profile.created = account_link.created
    user_profile.expires_at = account_link.expires_at
    user_profile.save()
    return Response({'url': account_link.url})


@api_view(http_method_names=['GET'])
@permission_classes((permissions.AllowAny,))
def get_stripe_publishable_key(request):
    return Response({'key': os.environ.get('STRIPE_PUBLISHABLE_KEY')})


@csrf_exempt
@api_view(http_method_names=['POST'])
def connect_stripe_account(request):
    account = stripe.AccountLink.create(
        account="acct_1Hx0mAIOSAQCOqoS",
        refresh_url="https://example.com/reauth",
        return_url="https://example.com/return",
        type="account_onboarding",
    )
    return Response({'uri': account.url})


@csrf_exempt
@api_view(http_method_names=['POST'])
@permission_classes((permissions.AllowAny,))
def create_checkout_session(request, stripe_id, session_id):
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
            cancel_url=domain_url,
            mode="payment",
            payment_method_types=['card'],
            line_items=[
                {
                    "amount": 3000,
                    "currency": 'eur',
                    "name": 'session',
                    "quantity": 1,

                },
            ],
            metadata={
                "session_id": session_id
            },
            payment_intent_data={
                'application_fee_amount': 600,
                'on_behalf_of': stripe_id,
                'transfer_data': {
                    #'amount': 3000,
                    'destination': stripe_id,
                },
                'metadata': {
                    "session_id": session_id
                }
            },
        )
        return Response({'sessionId': checkout_session['id']})
    except Exception as e:
        return Response({'error': str(e)})


@csrf_exempt
def check_out_success_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
          payload, sig_header, os.environ.get('STRIPE_ENDPOINT_SECRET')
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object # contains a stripe.PaymentIntent
        session_id = payment_intent.get('metadata', {}).get('session_id')
        session = TherapySession.objects.get(surrogate=session_id)
        session.status = TherapySession.PAYMENT_COMPLETED
        session.save()
        print('PaymentIntent was successful!', payment_intent, session_id)
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object # contains a stripe.PaymentMethod
        print('PaymentMethod was attached to a Customer!')
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))
    return HttpResponse(status=200)
