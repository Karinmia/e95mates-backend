from django.urls import path

from accounts.views import (
    SignInRequestView, SignInVerifyView, UserProfileView
)


urlpatterns = [
    path('sign-in-request', SignInRequestView.as_view(), name='signInRequest'),
    path('sign-in-verify', SignInVerifyView.as_view(), name='signInVerify'),

    path('profile', UserProfileView.as_view(), name='getOrUpdateUserProfile'),

    # path('profile/photo', UpdateProfilePhotoView.as_view(), name='updatePhoto'),
    # path('profile/phone', UserUpdatePhoneView.as_view(), name='updatePhone'),
    # path('profile/phone/verify', UserVerifyPhoneView.as_view(), name='verifyPhone'),
]
