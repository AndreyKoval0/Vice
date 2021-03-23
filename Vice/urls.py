"""Vice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from main.views import index, sign_in, sign_up, search_people, vice, get_file
from vice_auth.views import sign
from bot.views import generate_key, send_message_bot, get_messages_bot
from smart_home.views import smart_home, set_value, set_devices, get_values

urlpatterns = [
    path('', index),
    path('sign_in/', sign_in, name="sign_in"),
    path('sign_up/', sign_up, name="sign_up"),
    path('sign/<int:is_reg>', sign, name="sign"),
    path('feed/<str:people>', vice, name="vice"),
    path('search_people/', search_people, name="search_people"),
    path('api/bot/gen_key/', generate_key, name="generate_key_for_bot"),
    path('api/bot/send_message/', send_message_bot, name="send_message_for_bot"),
    path('api/bot/get_messages/', get_messages_bot, name="get_messages_for_bot"),
    path('files/<str:name_file>', get_file, name="get_file"),
    path('smart_home', smart_home, name="smart_home"),
    path('smart_home/set_value', set_value, name="smart_home_set_value"),
    path('smart_home/set_value/', set_value, name="smart_home_set_value"),
    path('api/smart_home/set_devices/', set_devices, name="smart_home_set_devices"),
    path('api/smart_home/get_values/', get_values, name="smart_home_get_values"),
]
