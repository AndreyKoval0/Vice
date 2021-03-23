from django.db import models

class Message(models.Model):
    from_message = models.IntegerField("От кого сообщение")
    to_message = models.IntegerField("Кому сообщение")
    message = models.TextField("Сообщение")
    message_for_me = models.TextField("Сообщение")
    type_message = models.TextField("Тип сообщения", default="text")