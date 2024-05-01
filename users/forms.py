from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import User

class LoginUserForm(forms.Form):
    username = forms.CharField(label="Логин",
                    widget=forms.TextInput(attrs={'class': 'form-input form-control item form-control item'}))
    password = forms.CharField(label="Пароль",
                    widget=forms.PasswordInput(attrs={'class': 'form-input form-control item form-control item'}))
    class Meta:
        model = User
        fields = ['username', 'password']

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': 'Логин',
            'email': 'E-mail',
            'password': 'Пароль',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input form-control item form-control item'}),
            'email': forms.TextInput(attrs={'class': 'form-input form-control item'}),
            'password': forms.PasswordInput(attrs={'class': 'form-input form-control item form-control item'}),
        }

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input form-control item'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input form-control item'}))
    new_password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput(attrs={'class': 'form-input form-control item'}))
