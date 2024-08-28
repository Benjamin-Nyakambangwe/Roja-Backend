from django.conf import settings
from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.views import(TokenObtainPairView, TokenRefreshView, TokenVerifyView)
from .serializers import CustomTokenObtainPairSerializer

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import LandlordProfile, TenantProfile
from .serializers import LandlordProfileSerializer, TenantProfileSerializer


class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                settings.AUTH_COOKIE, access_token, max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE, path=settings.AUTH_COOKE_PATH, 
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
                )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKE_PATH, 
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
            )
        
        return response



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                settings.AUTH_COOKIE, access_token, max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE, path=settings.AUTH_COOKE_PATH, 
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
                )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                path=settings.AUTH_COOKE_PATH, 
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
            )
        
        return response
    


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            response.set_cookie(
                settings.AUTH_COOKIE, access_token, max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE, path=settings.AUTH_COOKE_PATH, 
                secure=settings.AUTH_COOKIE_SECURE, httponly=settings.AUTH_COOKIE_HTTP_ONLY, samesite=settings.AUTH_COOKIE_SAMESITE
                )
            
        return response



class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)
    

class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.AUTH_COOKIE)
        response.delete_cookie('refresh')
        return response
    




class LandlordProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = LandlordProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return LandlordProfile.objects.get_or_create(user=self.request.user)[0]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TenantProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = TenantProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return TenantProfile.objects.get_or_create(user=self.request.user)[0]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
# class LandlordListView(generics.ListAPIView):
#     queryset = User.objects.filter(user_type='landlord')
#     serializer_class = CustomUserSerializer
#     permission_classes = [permissions.IsAdminUser]

#     def get_queryset(self):
#         return super().get_queryset().select_related('landlord_profile')

# class TenantListView(generics.ListAPIView):
#     queryset = User.objects.filter(user_type='tenant')
#     serializer_class = CustomUserSerializer
#     permission_classes = [permissions.IsAdminUser]

#     def get_queryset(self):
#         return super().get_queryset().select_related('tenant_profile')

class LandlordProfileListView(generics.ListAPIView):
    queryset = LandlordProfile.objects.all()
    serializer_class = LandlordProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class TenantProfileListView(generics.ListAPIView):
    queryset = TenantProfile.objects.all()
    serializer_class = TenantProfileSerializer
    permission_classes = [permissions.IsAdminUser]

    



    
            
        

