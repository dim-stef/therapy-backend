from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers, serializers, viewsets
from . import views

router = routers.DefaultRouter()
router.register(r'user/me', views.UserMeViewSet, basename="user_me")
router.register(r'therapists', views.TherapistsViewSet, basename="therapists")
router.register(r'create_session', views.CreateTherapySessionViewSet, basename="create_session")
router.register(r'user_profiles', views.ProfileViewSet, basename="user_profiles")

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/stripe_publishable_key/', views.get_stripe_publishable_key, name="stripe_key"),
    path('v1/create_checkout_session/<str:stripe_id>/', views.create_checkout_session, name="create_checkout_session"),
    path('v1/create_stripe_account_link/', views.create_stripe_account_link, name="create_stripe_account_link"),
    path('v1/get_stripe_login/', views.get_stripe_login, name="get_stripe_login"),
    path('v1/create_direct_payment/<str:stripe_id>/', views.create_direct_payment, name="create_direct_payment")
]
