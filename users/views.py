from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib.auth import login as dj_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.template.loader import render_to_string
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.conf import settings

from .forms import LoginUserForm, UserPasswordChangeForm, RegisterForm
from .models import User

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4
import smtplib

def send_mail(subject: str, message: str,recipient_list: list[str],) -> int:
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.ehlo()
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    for recipient in recipient_list:
        msg = MIMEMultipart()
        msg['Subject'] = str(subject)
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = str(recipient)
        msg.attach(MIMEText(message, 'html'))
        server.sendmail(settings.EMAIL_HOST_USER, recipient, msg.as_string())
    server.quit()

def ulogin(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = LoginUserForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                user = User.objects.filter(username=username).first()
                if user and user.check_password(password):
                    dj_login(request, user)
                    # if user.email_activated:
                    #     dj_login(request, user)
                    # else:
                    #     return HttpResponseRedirect(reverse('users:confirm-email', args=["1"]))
                    # return HttpResponseRedirect(reverse('users:profile'))
        else:
            form = LoginUserForm()
        context = {"form": form, "errors": form.errors}
        return render(request, "users/login.html", context=context)
    else:
        return HttpResponseRedirect(reverse('users:profile'))

def register(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = RegisterForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]
                email = form.cleaned_data["email"]
                password = form.cleaned_data["password"]
                user = User.objects.create(username=username, email=email, confirm_key=str(uuid4()))
                user.set_password(password)
                user.save()
                context = {"user": user, "url": request.get_host()}
                # send_mail("Quizz - Подтверждение почты", message=render_to_string("users/activate.html", context=context), recipient_list=[email])
                return render(request, "users/activate-page.html")
        else:
            form = RegisterForm()
        context = {"form": form}
        return render(request, "users/register.html", context=context)
    else:
        return HttpResponseRedirect(reverse('users:profile'))

def send_email(request, act_key):
    print(request.get_host())
    user = User.objects.filter(confirm_key=act_key).first()
    if user:
        user.email_activated = True
        user.save()
        return HttpResponseRedirect(reverse('users:login'))
    else:
        if not request.user.is_authenticated:
            context = {"user": user, "url": request.get_host()}
            send_mail("Quizz - Подтверждение почты", message=render_to_string("users/activate.html", context=context), recipient_list=[user.email])
    context = {"user": user}
    return render(request, "users/activate-page.html", context=context)

def ulogout(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:login'))


@login_required(login_url="users:login")
def profile(request):
    created_quizes = eval(str(request.user.created_quizes))
    completed_quizes = eval(str(request.user.completed_quizes))
    context = {'created_quizes': created_quizes, 'completed_quizes': completed_quizes, 'max_len': max([len(created_quizes), len(completed_quizes)])}
    return render(request, 'users/profile.html', context=context)

def user_page(request, user_id):
    user = User.objects.get(id=user_id)
    created_quizes = eval(str(user.created_quizes))
    completed_quizes = eval(str(user.completed_quizes))
    context = {'user': request.user, "user_page": user, 'created_quizes': created_quizes, 'completed_quizes': completed_quizes, 'max_len': max([len(created_quizes), len(completed_quizes)])}
    return render(request, 'users/user.html', context=context)

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:profile")
    template_name = "users/password_change_form.html"
