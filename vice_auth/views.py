from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from Crypto.Cipher import AES
from .models import User
from main.views import get_user_data
from scripts import Auth
import base64

def pad(text):
    while len(text) % 16 != 0:
        text += b' '
    return text

def sign(request, is_reg):
    if request.POST:
        login = request.POST["login"]
        password = request.POST["password"]
        auth = Auth(login, password)
        if bool(is_reg):
            data = get_user_data(User.objects.all())
            users = User()
            repeat_password = request.POST["repeat_password"]
            if not(len(login) >= 2) or login in data["Logins"]:
                raise Http404("Придумайте другой логин")
            elif password == repeat_password and len(password) < 8:
                raise Http404("Слишком лёгкий пароль")
            elif password != repeat_password:
                raise Http404("Вы неправильно повторили пароль, зарегистрируйтесь заново")
            publickey, privatekey, salt, password = auth.sign_up()
            users.login = login
            users.password = password
            users.salt = salt
            users.pub_key = publickey
            users.priv_key = privatekey
            users.type_user = "user"
            users.save()
            return HttpResponseRedirect(reverse("sign_in"))
        else:
            data = get_user_data(User.objects.filter(type_user="user"))
            index = auth.sign_in(data["Logins"], data["Passwords"], data["Salts"])
            if not(index is None):
                aes = AES.new(pad(password.encode("utf-8")), AES.MODE_ECB)
                request.session["login"] = data["Logins"][index]
                request.session["password"] = data["Passwords"][index]
                request.session["private_key"] = aes.decrypt(base64.b64decode(data["Private keys"][index])).decode("utf-8")
                return HttpResponseRedirect(reverse("vice", args=("admin", )))
            else:
                raise Http404("Неправильный логин или пароль")