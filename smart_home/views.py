from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from smart_home.models import Device, Rosette, TempHumSensor
from main.views import sign_in_bot
import json

def smart_home(request):
    context = {"devices": []}
    devices = Device.objects.filter(user=request.session["login"])
    ind = 0
    for device in devices:
        context["devices"].append({})
        context["devices"][ind]["name"] = device.name
        context["devices"][ind]["type"] = device.type_device
        if device.type_device == "rosette":
            rosette = Rosette.objects.filter(device_id=device.id)[0]
            context["devices"][ind]["value"] = rosette.value
        if device.type_device == "sensor":
            sensor = TempHumSensor.objects.filter(device_id=device.id)[0]
            context["devices"][ind]["value_temp"] = sensor.value_temp
            context["devices"][ind]["value_hum"] = sensor.value_hum
        ind += 1
    return render(request, "smart_home.html", context)

@csrf_exempt
def set_devices(request):
    device = Device()
    login = request.POST["login"]
    password = request.POST["password"]
    name = request.POST["name"]
    type_device = request.POST["type"]
    private_key = sign_in_bot(login, password)
    if private_key != None:
        device.user = login
        device.name = name
        device.type_device = type_device
        device.save()
        if type_device == "rosette":
            rosette = Rosette()
            rosette.user = login
            rosette.value = False
            rosette.device_id = device.id
            rosette.save()
        elif type_device == "sensor":
            sensor = TempHumSensor()
            sensor.user = login
            sensor.value_temp = 0
            sensor.value_hum = 0
            sensor.device_id = device.id
            sensor.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "failed", "error": "Username or password is incorrect"})

@csrf_exempt
def get_values(request):
    values = {}
    private_key = sign_in_bot(request.POST["login"], request.POST["password"])
    if private_key != None:
        devices = Device.objects.filter(user=request.POST["login"])
        for device in devices:
            if device.type_device == 'rosette':
                rosette = Rosette.objects.filter(device_id=device.id)[0]
                value = rosette.value
                values[device.name] = value
        data = json.dumps({"status": "ok", "values": values}, ensure_ascii=False, indent=4)
        return HttpResponse(data)
    return JsonResponse({"status": "failed", "error": "Username or password is incorrect"})

@csrf_exempt
def set_value(request):
    if "login" in request.GET or request.POST:
        login = request.POST["login"] if request.POST else request.GET["login"]
        password = request.POST["password"] if request.POST else request.GET["password"]
        private_key = sign_in_bot(login, password)
        if private_key != None:
            devices = Device.objects.filter(user=login)
        else:
            return JsonResponse({"status": "failed", "error": "Username or password is incorrect"})
    else:
        devices = Device.objects.filter(user=request.session["login"])
    for device in devices:
        if device.type_device == "rosette" and not("login" in request.GET) and not(request.POST):
            rosette = Rosette.objects.filter(device_id=device.id)[0]
            if device.name in request.GET:
                rosette.value = True
            else:
                rosette.value = False
            rosette.save()
        elif device.type_device == "rosette" and request.POST:
            rosette = Rosette.objects.filter(device_id=device.id)[0]
            if device.name in request.POST:
                rosette.value = request.POST[device.name] == "on"
            rosette.save()
        elif device.type_device == "sensor" and "login" in request.GET:
            if request.GET["name"] == device.name:
                sensor = TempHumSensor.objects.filter(device_id=device.id)[0]
                sensor.value_temp = request.GET["temperature"]
                sensor.value_hum  = request.GET["humidity"]
                sensor.save()
    if "login" in request.GET or request.POST:
        return JsonResponse({"status": "ok"})
    return redirect("smart_home")
