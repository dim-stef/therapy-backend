from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers, serializers, viewsets
from . import views

router = routers.DefaultRouter()
router.register(r'user/me', views.UserMeViewSet, basename="user_me")
router.register(r'therapists/(?P<surrogate>[\w\-]+)/availability', views.ChangeAvailabilityTimes,
                basename="change_availability")
router.register(r'therapists', views.TherapistsViewSet, basename="therapists")
router.register(r'create_session', views.CreateTherapySessionViewSet, basename="create_session")
router.register(r'therapy_sessions', views.CreateTherapySessionViewSet, basename="therapy_sessions")
router.register(r'my_sessions', views.MySessionsViewSet, basename="therapists_sessions")
router.register(r'user_profiles', views.ProfileViewSet, basename="user_profiles")
router.register(r'update_user_profile', views.UpdateUserProfileViewSet, basename="update_user_profile")
router.register(r'update_therapist_profile', views.UpdateTherapistProfileViewSet, basename="update_therapist_profile")
router.register(r'reviews', views.ReviewSerializer, basename="reviews")

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/stripe_publishable_key/', views.get_stripe_publishable_key, name="stripe_key"),
    path('v1/create_checkout_session/<str:stripe_id>/<str:session_id>/',
         views.create_checkout_session, name="create_checkout_session"),
    path('v1/create_stripe_account_link/', views.create_stripe_account_link, name="create_stripe_account_link"),
    path('v1/get_stripe_login/', views.get_stripe_login, name="get_stripe_login"),
    path('v1/create_direct_payment/<str:stripe_id>/', views.create_direct_payment, name="create_direct_payment"),
    path('v1/stripe_webhook/', views.check_out_success_webhook, name="stripe_webhook")
]
