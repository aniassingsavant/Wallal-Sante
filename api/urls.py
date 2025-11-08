from django.urls import path
from .views import (
    RegisterView,
    EtablissementsLiveOSMView,
    translate,  
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Authentification
    path('register/', RegisterView.as_view(), name='register'),
    path('login/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Géolocalisation live OSM
    path('etablissements/live-osm/', EtablissementsLiveOSMView.as_view(), name='etablissements_live_osm'),

    # Traduction via IA
    path('translate/', translate, name='translate'), 
]
