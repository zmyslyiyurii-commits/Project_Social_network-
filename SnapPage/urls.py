from django.urls import path
from .views import OpenHomeView, SnapDetailView, CreateStoryView, UserStoryDetailView

app_name = 'SnapPage'

urlpatterns = [
    path('openhome/', OpenHomeView.as_view(), name='openhome'),
    path('snap/<int:pk>/', SnapDetailView.as_view(), name='snap_detail'),
    path('story/create/', CreateStoryView.as_view(), name='create_story'),
    path('story/user/<int:user_id>/', UserStoryDetailView.as_view(), name='user_story_detail'),
]