from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.urls import path

from . import views


urlpatterns = [
    path('login/', LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=settings.INDEX_URL), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('settings/', views.SettingsView.as_view(), name='user_settings'),
]
