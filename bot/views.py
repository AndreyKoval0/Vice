from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from vice_auth.models import User
from main.views import get_user_data, decrypt_messages, sign_in_bot
from messages.models import Message
from scripts import Auth
from scripts import Crypto
import base64
import secrets
import json

def get_messages(login):
    messages = Message.objects.all()
    data = get_user_data(User.objects.all())
    messages_encrypted = []
    type_messages = []
    from_messages = []
    for message in messages:
        if message.to_message == (data["Logins"].index(login)+1):
            from_message = data["Logins"][message.from_message-1]
            messages_encrypted.append(from_message+": "+message.message)
            type_messages.append(message.type_message)
            from_messages.append(from_message)
    return messages_encrypted, type_messages, from_messages


@csrf_exempt
def generate_key(request):
    api_key = base64.b64encode(secrets.token_urlsafe(16).encode("utf-8")).decode("utf-8")
    if request.POST:
        login = request.POST["login"]
        password = api_key
        auth = Auth(login, password)
        data = get_user_data(User.objects.all())
        user = User()
        if not(len(login) >= 2) or login in data["Logins"]:
            data = '{"status": "failed"}'
            return HttpResponse(str(data))
        publickey, privatekey, salt, password = auth.sign_up()
        user.login = login
        user.password = password
        user.salt = salt
        user.pub_key = publickey
        user.priv_key = privatekey
        user.type_user = "bot"
        user.save()
        data = '{"status": "ok", "api_key": "'  + str(api_key) + '"}'
        return HttpResponse(str(data))
    data = '{"status": "failed"}'
    return HttpResponse(str(data))

@csrf_exempt
def send_message_bot(request):
    if request.POST:
        people = request.POST["to_user"]
        login = request.POST["login"]
        api_key = request.POST["api_key"]
        privatekey = sign_in_bot(login, api_key)
        if privatekey != None:
            data = get_user_data(User.objects.all())
            publickey = data["Public keys"][data["Logins"].index(login)].encode("utf-8")   
            privatekey = base64.b64encode(privatekey.encode("utf-8")) 
            crypto_for_me = Crypto(publickey, privatekey) 
            crypto_for_him = Crypto(data["Public keys"][data["Logins"].index(people)].encode("utf-8"))
            message = request.POST["message"]
            messages = Message()
            messages.from_message = data["Logins"].index(login)+1
            messages.to_message = data["Logins"].index(people)+1
            messages.message = crypto_for_him.encrypt(message.encode("utf-8"), "public")
            messages.message_for_me = crypto_for_me.encrypt(message.encode("utf-8"), "public")
            messages.save()
            data = '{"status": "ok"}'
            return HttpResponse(str(data))
    data = '{"status": "failed"}'
    return HttpResponse(str(data))

@csrf_exempt
def get_messages_bot(request):
    login = request.POST["login"]
    password = request.POST["api_key"]
    data = get_user_data(User.objects.all())
    publickey = data["Public keys"][data["Logins"].index(login)].encode("utf-8")   
    privatekey = sign_in_bot(login, password)
    privatekey = base64.b64encode(privatekey.encode("utf-8"))
    crypto = Crypto(publickey, privatekey)
    messages_encrypted, type_messages, from_messages = get_messages(login)
    from_messages = from_messages[(len(from_messages)-50)*(len(from_messages)-50 > 0):]
    messages = decrypt_messages(request, messages_encrypted, type_messages, crypto)
    messages = messages[(len(messages)-50)*(len(messages)-50 > 0):]
    #ensure_ascii=False,

    data = {
        "status": "ok",
        "messages": messages,
        "from_messages": from_messages
    }
    return HttpResponse(str(json.dumps(data, ensure_ascii=False)))
