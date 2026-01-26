from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='blog-home'), 
    path('post/new/', views.post_create, name='post-create'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
    path('post/<int:pk>/update/', views.post_update, name='post-update'),
    path('post/<int:pk>/delete/', views.post_delete, name='post-delete'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment-delete'),
    path('comment/<int:pk>/edit/', views.comment_edit, name='comment-edit'),
    path('post/<int:pk>/like/', views.post_like, name='post-like'),
    path('about/', views.about, name='blog-about'),
    path('contact/', views.contact, name='blog-contact'),
    path('privacy-policy/', views.privacy_policy, name='blog-privacy'),
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<str:username>/', views.chat_room, name='chat-room'),
]