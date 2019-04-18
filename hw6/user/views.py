from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

from .forms import SignUpForm, SettingsForm


class SignUpView(CreateView):
    """
    Sign up endpoints
    """
    template_name = 'user/signup.html'
    form_class = SignUpForm
    success_url = settings.LOGIN_URL


class SettingsView(LoginRequiredMixin, UpdateView):
    """
    User settings endpoints
    """
    template_name = 'user/settings.html'
    form_class = SettingsForm
    success_url = reverse_lazy('user_settings')

    def get_object(self, queryset=None):
        return self.request.user
