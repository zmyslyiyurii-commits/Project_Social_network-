from django.urls import path
from users.views import chat_detail
from .views import (
    OpenHomeView, 
    SnapDetailView, 
    CreateSnapView, 
    CreateStoryView, 
    UserStoryDetailView,
    AddFriendsPanelView,
    send_friend_request,
    accept_friend_request,
    reject_friend_request
)

app_name = 'SnapPage'

urlpatterns = [
    path('openhome/', OpenHomeView.as_view(), name='openhome'),
    
    # Чат
    path('chat/<int:friend_id>/', chat_detail, name='chat_detail'),

    # Снапи та історії
    path('snap/<int:pk>/', SnapDetailView.as_view(), name='snap_detail'),
    path('snap/create/', CreateSnapView.as_view(), name='create_snap'),
    path('story/create/', CreateStoryView.as_view(), name='create_story'),
    path('story/user/<int:user_id>/', UserStoryDetailView.as_view(), name='user_story_detail'),
    
    # Маршрути для системи додавання друзів
    path('friends/add/', AddFriendsPanelView.as_view(), name='add_friends_panel'),
    path('friends/send/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('friends/reject/<int:request_id>/', reject_friend_request, name='reject_friend_request'),
]