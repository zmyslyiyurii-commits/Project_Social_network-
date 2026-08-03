from django.urls import path
from .views import OpenHomeView, SnapDetailView

app_name = 'SnapPage'

urlpatterns = [
    path('openhome/', OpenHomeView.as_view(), name='openhome'),
    path('snap/<int:pk>/', SnapDetailView.as_view(), name='snap_detail'),
]