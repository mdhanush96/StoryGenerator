
from django.contrib import admin
from django.urls import path,include
from .import views


urlpatterns = [
    path("", views.home, name="home"),  # Renders the frontend (base.html)
    path("get_response/", views.get_response, name="get_response"),  # API for chatbot responses
    path('get_chat_history/', views.get_chat_history, name='get_chat_history'),

]
