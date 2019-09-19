from django.conf.urls import url


from . import views

urlpatterns = [

    url('login_view',
        views.UserLoginAPIView.as_view(),
        name='login_view'),

    url('register',
        views.UserRegistrationAPIView.as_view(),
        name='register'),

    url(r'^verify/(?P<verification_key>.+)/$',
        views.UserEmailVerificationAPIView.as_view(),
        name='email_verify'),

    url(r'^user-profile/$',
        views.UserProfileAPIView.as_view(),
        name='user_profile'),


]
