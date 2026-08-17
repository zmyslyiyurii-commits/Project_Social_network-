"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home.views import HomeView
from users.views import RegisterView, CustomLoginView, ProfileView, send_message, get_messages, mark_messages_as_read, chat_detail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Головна сторінка сайту
    path('', HomeView.as_view(), name='home'),
    # Маршрути додатка SnapPage з явно вказаним namespace
    path('', include(('SnapPage.urls', 'SnapPage'), namespace='SnapPage')),
    # Авторизація та профілі
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Маршрути для роботи з повідомленнями та чатом
    path('chat/<int:friend_id>/', chat_detail, name='chat_detail'),
    path('messages/send/<int:recipient_id>/', send_message, name='send_message'),
    path('messages/get/<int:user_id>/', get_messages, name='get_messages'),
    path('messages/read/<int:sender_id>/', mark_messages_as_read, name='mark_messages_as_read'),
]
# Обслуговування медіафайлів локально під час розробки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)