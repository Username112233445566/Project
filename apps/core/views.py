from rest_framework.response import Response
from rest_framework import generics, status

from .serializers import (
    UserAvatarNickanmeSerializer, 
    UserSerializer, VerifySerializer, 
    UserLoginSerializer, AdminLoginSerializer, 
    UserEmailSerializer, UserListSerializer, 
    UserPutSerializer
)
from .service import AuthService, OTPService
from .models import User

from drf_spectacular.utils import extend_schema

@extend_schema(tags=['UserForgotPassword'])
class UserForgotPasswordView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserEmailSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data, response_status = OTPService.forgot_password(serializer.validated_data)
        return Response(response_data, status=response_status)
    

@extend_schema(tags=['User'])
class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return User.objects.filter(id=pk)
        return User.objects.all()


@extend_schema(tags=['InactiveUser'])
class InactiveUserListView(generics.ListAPIView):
    queryset = User.objects.filter(is_confirmed=False, is_denied=False)
    serializer_class = UserListSerializer


@extend_schema(tags=['Register'])
class UserView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = AuthService.register_user(serializer.validated_data)
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(tags=['ResendOTP'])
class ResendOTPView(generics.GenericAPIView):
    serializer_class = UserEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        response_data = AuthService.resend_otp(email)
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(tags=['Verify'])
class VerifyView(generics.GenericAPIView):
    serializer_class = VerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data, status_code = AuthService.verify_otp(serializer.validated_data)
        return Response(response_data, status=status_code)


@extend_schema(tags=['UserLogin'])
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data, status_code = AuthService.login_user(serializer.validated_data)
        return Response(response_data, status=status_code)


@extend_schema(tags=['AdminLogin'])
class AdminLoginView(generics.GenericAPIView):
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data, status_code = AuthService.login_admin(serializer.validated_data)
        return Response(response_data, status=status_code)


@extend_schema(tags=['UserPut'])
class UserPutView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPutSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_user = AuthService.save_password(instance, serializer.validated_data)
        return Response(self.get_serializer(updated_user).data, status=status.HTTP_200_OK)


@extend_schema(tags=['UserLogout'])
class UserLogoutView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data, status_code = AuthService.logout_user(serializer.validated_data, request)
        return Response(response_data, status=status_code)


@extend_schema(tags=['UserDelete'])
class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserEmailSerializer


@extend_schema(
    tags=['User Nickname'],
    summary='УРЛ для никнейма и аватара юзера'
)
class UserNicknameAvatarAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserAvatarNickanmeSerializer

