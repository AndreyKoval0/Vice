from django.db import models

class User(models.Model):
    login = models.CharField("Логин", max_length=200)
    password = models.CharField("Пароль", max_length=200)
    salt = models.TextField("Соль")
    pub_key = models.TextField("Публичный ключ")
    priv_key = models.TextField("Приватный ключ")
    type_user = models.CharField("Тип пользователя", max_length=200, default="user")