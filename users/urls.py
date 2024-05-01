from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from . import views

app_name = "users"

urlpatterns = [
    path('login/', views.ulogin, name='login'),

    path('logout/', views.ulogout, name='logout'),

    # path('password-change/', views.UserPasswordChange.as_view(), name="password_change"),

    path('register/', views.register, name='register'),

    path('profile/', views.profile, name='profile'),
    
    path('<int:user_id>/', views.user_page, name='user'),

]
