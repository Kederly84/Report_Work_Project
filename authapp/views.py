from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from authapp.forms import CustomAuthenticationForm
from authapp.models import User


# Create your views here.

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'authapp/login.html'
    extra_context = {
        'title': 'Вход пользователя'
    }

    def form_valid(self, form):
        ret = super().form_valid(form)

        message = ("Здраствуйте, <br> %(username)s") % {
            "username": self.request.user.get_full_name()
            if self.request.user.get_full_name()
            else self.request.user.get_username()
        }
        messages.add_message(self.request, messages.INFO, mark_safe(message))
        return ret

    def form_invalid(self, form):
        messages.add_message(self.request, messages.WARNING, 'Неправильное имя пользователя или пароль!')
        return self.render_to_response(self.get_context_data(form=form))


class RegisterView(TemplateView):
    template_name = 'authapp/register.html'
    extra_context = {
        'title': 'Регистрация пользователя'
    }

    def post(self, request, *args, **kwargs):
        try:
            if all(
                    (
                            request.POST.get('username'),
                            request.POST.get('password1'),
                            request.POST.get('password2'),
                            request.POST.get('first_name'),
                            request.POST.get('last_name'),
                            request.POST.get('email'),
                            request.POST.get('password1') == request.POST.get('password2'),
                    )
            ):
                new_user = User.objects.create(
                    username=request.POST.get('username'),
                    first_name=request.POST.get('first_name'),
                    last_name=request.POST.get('last_name'),
                    email=request.POST.get('email')
                )
                new_user.set_password(request.POST.get('password1'))
                new_user.save()
                messages.add_message(request, messages.INFO, 'Реистрация успешна')
                return HttpResponseRedirect(reverse('authapp:login'))
            else:
                messages.add_message(request, messages.WARNING, 'Неверно указаны данные')
                return HttpResponseRedirect(reverse('authapp:register'))
        except Exception as ex:
            messages.add_message(request, messages.WARNING, f'Что-то не получилось {ex}')
            return HttpResponseRedirect(reverse('authapp:register'))


class CustomLogoutView(LogoutView):
    template_name = 'authapp/login.html'


class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('authapp:login')
    template_name = 'authapp/password_change_form.html'

    def form_valid(self, form):
        ret = super().form_valid(form)
        message = ("Пароль успешно изменен!")
        messages.add_message(self.request, messages.INFO, mark_safe(message))
        return ret
