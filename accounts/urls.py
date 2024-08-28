from django.urls import path, re_path
from .views import CustomProviderAuthView, CustomTokenObtainPairView, CustomTokenRefreshView, CustomTokenVerifyView, LogoutView
from .views import LandlordProfileView, TenantProfileView, LandlordProfileListView, TenantProfileListView





urlpatterns = [
    re_path(
        r'^o/(?P<provider>\S+)/$',
        CustomProviderAuthView.as_view(),
        name='social)'
    ),
    path('jwt/create/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('landlord-profile/', LandlordProfileView.as_view(), name='landlord-profile'),
    path('tenant-profile/', TenantProfileView.as_view(), name='tenant-profile'),
    path('landlords/', LandlordProfileListView.as_view(), name='landlord-list'),
    path('tenants/', TenantProfileListView.as_view(), name='tenant-list'),

]

        