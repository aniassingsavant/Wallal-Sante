from django.urls import path
from . import views

urlpatterns = [
    #les routes vers les pages html
    path('', views.chatbot, name='chatbot')
]