from django.db import models

class Device(models.Model):
    user = models.CharField("Пользователь", max_length=200)
    name = models.CharField("Имя устройства", max_length=200)
    type_device = models.CharField("Тип устройства", max_length=200)

class Rosette(models.Model):
    user = models.CharField("Пользователь", max_length=200)
    value = models.BooleanField("Состояние розетки")
    device_id = models.IntegerField("ID устройства")

class TempHumSensor(models.Model):
    user = models.CharField("Пользователь", max_length=200)
    value_temp = models.IntegerField("Температура")
    value_hum = models.IntegerField("Влажность")
    device_id = models.IntegerField("ID устройства")