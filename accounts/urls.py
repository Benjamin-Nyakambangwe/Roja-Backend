from django.urls import path, re_path
from .views import CustomProviderAuthView, CustomTokenObtainPairView, CustomTokenRefreshView, CustomTokenVerifyView, LogoutView
from .views import LandlordProfileView, TenantProfileView, LandlordProfileListView, TenantProfileListView, InitiatePaymentView, PaymentResultView, PaymentStatusView
from .views import TenantProfileLimitedView, LandlordProfileLimitedView, getTenantProfileView
from .views import AddTenantAccessView

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

    path('initiate/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('result/', PaymentResultView.as_view(), name='payment_result'),
    path('status/', PaymentStatusView.as_view(), name='payment_status'),

    path('tenant-profile-limited/', TenantProfileLimitedView.as_view(), name='tenant-profile-limited'),
    path('landlord-profile-limited/<int:pk>/', LandlordProfileLimitedView.as_view(), name='landlord-profile-limited'),
    path('add-tenant-access/<int:property_id>/', AddTenantAccessView.as_view(), name='add-tenant-access'),

    path('custom-tenant-profile/<int:pk>/', getTenantProfileView.as_view(), name='get-tenant-profile'),
]

        