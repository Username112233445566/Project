from django.urls import path
from .views import AdminLoginView, UserView, VerifyView, UserLoginView, UserDeleteView, UserListView, UserPutView, InactiveUserListView, ResendOTPView, UserLogoutView, UserForgotPasswordView, UserNicknameAvatarAPIView

urlpatterns = [
    path('list-user/', UserListView.as_view(), name='user-list'),
    path('inactive-users/', InactiveUserListView.as_view(), name='inactive-users-list'),
    path('list-user/<int:pk>/', UserListView.as_view(), name='user-list-id'), 
    path('register-user/', UserView.as_view(), name='register-user'),
    path('verify-user/', VerifyView.as_view(), name='verify-user'),
    path('login-user/', UserLoginView.as_view(), name='login-user'),
    path('logout-user/', UserLogoutView.as_view(), name='logout-user'),
    path('login-manager/', AdminLoginView.as_view(), name='login-manager'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('forgot-password/', UserForgotPasswordView.as_view(), name='forgot-password'),
    path('put-request/<int:pk>/', UserPutView.as_view(), name='put-request'),
    path('delete-user/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
    path('avatar-nickname/<int:pk>/', UserNicknameAvatarAPIView.as_view(), name='user-nickaname-avatar'),
]
