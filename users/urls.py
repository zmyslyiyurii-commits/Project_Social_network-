from django.urls import path
from .views import RegisterView, CustomLoginView, ProfileView, SendSnapView, SendSnapAPIView

urlpatterns = [
    # Авторизація та профілі
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Відправка снапів
    path('snaps/send/', SendSnapView.as_view(), name='send_snap'),
    path('snaps/send/<int:receiver_id>/', SendSnapView.as_view(), name='send_snap_to'),
    path('api/snaps/send/', SendSnapAPIView.as_view(), name='api_send_snap'),
]