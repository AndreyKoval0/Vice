from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message
from main.views import get_user_data
from vice_auth.models import User
from scripts import Crypto
import base64
import random
import json

def encrypt_file(chat_name, data, type_file):
    path = f"files/{chat_name}__{str(random.randint(1, 10000000000000000))}.{type_file}"
    f = open(path, "wb")
    f.write(data)
    f.close()
    return path

def encrypt_message(session, message, login, people, type_message):
    data = get_user_data(User.objects.all())
    publickey = data["Public keys"][data["Logins"].index(login)].encode("utf-8")   
    privatekey = base64.b64encode(session["private_key"].encode("utf-8")) 
    crypto_for_me = Crypto(publickey, privatekey) 
    crypto_for_him = Crypto(data["Public keys"][data["Logins"].index(people)].encode("utf-8"))
    if message != "":
        messages = Message()
        messages.from_message = data["Logins"].index(login)+1
        messages.to_message = data["Logins"].index(people)+1
        answer = message.encode("utf-8")
        messages.message = crypto_for_him.encrypt(answer, "public")
        messages.message_for_me = crypto_for_me.encrypt(answer, "public")
        messages.type_message = type_message
        messages.save()

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["session"]["chat_name"]
        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        people = self.scope["session"]["to_user"]
        login = self.scope["session"]["login"]

        encrypt_message(self.scope['session'], message, login, people, "text")

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{login}: {message}"
            }
        )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'message': message
        }))

class ChatFileConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["session"]["chat_name"]
        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, bytes_data):
        people = self.scope["session"]["to_user"]
        login = self.scope["session"]["login"]

        data_file = bytes_data[32:]
        type_file = bytes_data[:32].decode("utf-8").replace(" ", "")

        message = encrypt_file(self.room_name, data_file, type_file)
        encrypt_message(self.scope['session'], message, login, people, "file")

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'{login}: <a href="/{message}"> Скачать файл </a>'
            }
        )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'message': message
        }))