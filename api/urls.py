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

    # New URL pattern for AvailableChatsView
    path('available-chats/', views.AvailableChatsView.as_view(), name='available-chats'),

    # New URL patterns for reviews
    path('properties-reviews/<int:property_id>', views.PropertyReviewList.as_view(), name='property-review-list'),
    path('users-reviews/<int:user_id>', views.UserReviewList.as_view(), name='user-review-list'),

    
    path('current-user/', views.CurrentUserView.as_view(), name='current-user'),

    # Add these to your urlpatterns
    path('comments/<int:pk>/like/', views.CommentLikeView.as_view(), name='comment-like'),
    path('comments/<int:pk>/dislike/', views.CommentDislikeView.as_view(), name='comment-dislike'),

    # Add these to your urlpatterns
    path('rent-payments/', views.RentPaymentListView.as_view(), name='rent-payment-list'),
    path('properties/<int:property_id>/rent-payments/', views.PropertyRentPaymentsView.as_view(), name='property-rent-payments'),
    path('rent-payments/<int:payment_id>/process/', views.ProcessRentPaymentView.as_view(), name='process-rent-payment'),

    # Add this to your urlpatterns
    path('tenant-accessible-properties/', views.TenantAccessibleProperties.as_view(), name='tenant-accessible-properties'),

    # Add this to your urlpatterns
    path('generate-property-description/', views.GeneratePropertyDescriptionView.as_view(), name='generate-property-description'),
]
