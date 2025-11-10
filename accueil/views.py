from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

#creons les vues pour chaque page

def accueil(request):
    return render(request, 'accueil/accueil.html')