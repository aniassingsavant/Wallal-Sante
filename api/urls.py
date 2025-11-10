from django.urls import path
from . import views

urlpatterns = [
    path('analyse/', views.analyse, name='analyse'),
    path('translate/', views.translate, name='translate'),
    path('status/', views.status, name='status'),
    path('hospitals/', views.find_hospitals_osm, name='hospitals_osm'),
    path('profile/', views.user_profile, name='user_profile'),
]
