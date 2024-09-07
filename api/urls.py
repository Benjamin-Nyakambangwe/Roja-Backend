from django.urls import path
from . import views

urlpatterns = [
    # Property URLs
    path('properties-filter/', views.PropertyListCreateView.as_view(), name='property-list-create'),
    path('properties/', views.PropertyList.as_view(), name='property-list'),
    path('own-properties/', views.OwnPropertyList.as_view(), name='own-property-list'),
    path('properties/<int:pk>/', views.PropertyDetail.as_view(), name='property-detail'),

    # PropertyImage URLs
    path('property-images/', views.PropertyImageList.as_view(), name='propertyimage-list'),
    path('property-images/<int:pk>/', views.PropertyImageDetail.as_view(), name='propertyimage-detail'),

    #HouseType and Location URLs
    path('house-types/', views.HouseTypeList.as_view(), name='housetype-list'),
    path('house-types/<int:pk>/', views.HouseTypeDetail.as_view(), name='housetype-detail'),
    path('house-locations/', views.HouseLocationList.as_view(), name='houselocation-list'),
    path('house-locations/<int:pk>/', views.HouseLocationDetail.as_view(), name='houselocation-detail'),


    # Application URLs
    path('applications/', views.ApplicationList.as_view(), name='application-list'),
    path('applications/<int:pk>/', views.ApplicationDetail.as_view(), name='application-detail'),

    # Message URLs
    path('messages/', views.MessageList.as_view(), name='message-list'),
    path('messages/<int:pk>/', views.MessageDetail.as_view(), name='message-detail'),

    # LeaseAgreement URLs
    path('lease-agreements/', views.LeaseAgreementList.as_view(), name='leaseagreement-list'),
    path('lease-agreements/<int:pk>/', views.LeaseAgreementDetail.as_view(), name='leaseagreement-detail'),

    # Review URLs
    path('reviews/', views.ReviewList.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view(), name='review-detail'),
]