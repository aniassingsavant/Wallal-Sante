from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.index, name='accueil'),
    path('a-propos/', views.about, name='about'),
    path('actualites/', views.actualites, name='actualites'),
    
    # Authentification
    path('s-inscrire/', views.register, name='register'),
    path('se-connecter/', views.user_login, name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(next_page='accueil'), name='deconnexion'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Backoffice
    path('backoffice/dashboard/', views.backoffice_dashboard, name='backoffice_dashboard'),
    path('backoffice/establishments/', views.manage_establishments, name='manage_establishments'),

    # Voice
    path('api/voice-query/', views.process_voice_query, name='process_voice_query'),
path('api/health-centers/', views.get_health_centers, name='get_health_centers'),
]