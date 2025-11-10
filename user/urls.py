from django.urls import path
from . import views

urlpatterns = [
    #les routes vers les pages html
    path('connexion', views.connexion, name='connexion'),
     path('inscription', views.inscription, name='inscription'),


]