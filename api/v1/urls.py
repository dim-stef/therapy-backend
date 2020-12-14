from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers, serializers, viewsets
from . import views

router = routers.DefaultRouter()
router.register(r'user/me', views.UserMeViewSet, basename="user_me")
router.register(r'therapists', views.TherapistsViewSet, basename="therapists")

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/stripe_publishable_key/', views.get_stripe_publishable_key, name="stripe_key"),
    path('v1/create_checkout_session/', views.create_checkout_session, name="create_checkout_session"),
]
