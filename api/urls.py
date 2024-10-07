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
    path('messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('messages/unread-count/', views.UnreadMessageCountView.as_view(), name='unread-message-count'),
    path('messages/<int:pk>/mark-read/', views.MarkMessageAsReadView.as_view(), name='mark-message-read'),

    # # LeaseAgreement URLs
    # path('lease-agreements/', views.LeaseAgreementList.as_view(), name='leaseagreement-list'),
    # path('lease-agreements/<int:pk>/', views.LeaseAgreementDetail.as_view(), name='leaseagreement-detail'),

    # Review URLs
    path('reviews/', views.ReviewList.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view(), name='review-detail'),


    # Comment URLs
    path('comments/', views.CommentList.as_view(), name='comment-list'),
    path('comments/<int:pk>/', views.CommentDetail.as_view(), name='comment-detail'),
    path('properties/<int:property_id>/comments/', views.PropertyCommentList.as_view(), name='property-comment-list'),

    # Chat URLs
    path('chats/', views.ChatListView.as_view(), name='chat-list'),
    path('chats/<int:user_id>/', views.ChatDetailView.as_view(), name='chat-detail'),
]