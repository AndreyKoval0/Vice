from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, Http404
from django.urls import reverse
from messages.models import Message
from vice_auth.models import User
from scripts import Crypto
from Crypto.Cipher import AES
from scripts import Auth
import random
import base64

def get_user_data(users):
    data = {"Logins":[],
            "Passwords": [],
            "Salts": [],
            "Public keys": [],
            "Private keys": [],
            "Type": []}
    for i in range(len(users)):
        data["Logins"].append(users[i].login)
        data["Passwords"].append(users[i].password)
        data["Salts"].append(users[i].salt)
        data["Public keys"].append(users[i].pub_key)
        data["Private keys"].append(users[i].priv_key)
        data["Type"].append(users[i].type_user)
    return data

def get_messages(request, data, login, password, people):
    messages = Message.objects.all()
    peoples = []
    messages_encrypted = []
    type_messages = []
    for i in range(len(messages)):
        from_message = data["Logins"][messages[i].from_message-1]
        to_message = data["Logins"][messages[i].to_message-1]
        if (to_message == login or from_message == login) and password == data["Passwords"][data["Logins"].index(login)]:
            if from_message != login: peoples.append(from_message)
            elif to_message != login: peoples.append(to_message)
            if to_message == people or from_message == people:
                if to_message == login:
                    messages_encrypted.append(from_message+": "+messages[i].message)
                    type_messages.append(messages[i].type_message)
                else:
                    messages_encrypted.append(from_message+": "+messages[i].message_for_me)
                    type_messages.append(messages[i].type_message)
    return messages_encrypted, peoples, type_messages

def decrypt_message(message, crypto):
    return crypto.decrypt(message, "private")

def decrypt_messages(request, messages_encrypted, type_messages, crypto):
    messages_decrypted = []
    for i in range(len(messages_encrypted)):
        splited = messages_encrypted[i].split(" ")
        data_message = decrypt_message(" ".join(splited[1:]), crypto)
        if type_messages[i] == "file":
            messages_decrypted.append(f'<p>{splited[0]} <a href="/{data_message}">Скачать файл</a></p>')
        elif type_messages[i] == "text":
            messages_decrypted.append(f'<p>{splited[0]} {data_message}</p>')
    return messages_decrypted

def pad(text):
    while len(text) % 16 != 0:
        text += b' '
    return text

def sign_in_bot(login, api_key):
    password = api_key
    auth = Auth(login, password)
    data = get_user_data(User.objects.all())
    index = auth.sign_in(data["Logins"], data["Passwords"], data["Salts"])
    if not(index is None):
        aes = AES.new(pad(password.encode("utf-8")), AES.MODE_ECB)
        private_key = aes.decrypt(base64.b64decode(data["Private keys"][index])).decode("utf-8")
        return private_key


def index(request):
    return render(request, "index.html")

def sign_in(request):
    return render(request, "sign_in.html")

def sign_up(request):
    return render(request, "sign_up.html")

def vice(request, people):    
    login = request.session["login"]
    password = request.session["password"]

    data = get_user_data(User.objects.all())
    messages_encrypted, peoples, type_messages = get_messages(request, data, login, password, people)

    publickey = data["Public keys"][data["Logins"].index(login)].encode("utf-8")   
    privatekey = base64.b64encode(request.session["private_key"].encode("utf-8"))
    crypto = Crypto(publickey, privatekey)
    request.session["messages"] = decrypt_messages(request, messages_encrypted, type_messages, crypto)

    chat = sorted([login, people])
    request.session["chat_name"] = f"{chat[0]}_{chat[1]}"
    request.session["to_user"] = people

    peoples = sorted(list(set(peoples)))
    return render(request, "main.html", {"peoples": peoples, "p": people, "messages": request.session["messages"]})

def search_people(request):
    users = User.objects.all()
    login = request.session["login"]
    logins = []
    if request.POST:
        people = request.POST["people"]
        for i in range(len(users)):
            if people.lower() in str(users[i].login).lower():
                logins.append(str(users[i].login))
    else:
        for i in range(len(users)):
            if users[i].login != login:
                logins.append(str(users[i].login))
    return render(request, "search.html", {"peoples": logins})

def get_file(request, name_file):
    if request.POST:
        login = request.POST["login"]
        privatekey = sign_in_bot(login, request.POST["api_key"])
        chat_name = request.POST["chat_name"]
        if (privatekey != None) and (login in chat_name):
            request.session["chat_name"] = chat_name
        else:
            return HttpResponse('{"status": "failed"}')
            
    chat_name = request.session["chat_name"]
    if (chat_name != None) and (chat_name in name_file):
        return FileResponse(open(f"files/{name_file}", "rb"), as_attachment=True, filename=name_file)
    else:
        raise Http404("Файл не найден")