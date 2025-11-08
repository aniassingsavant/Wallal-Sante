from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

#creons les vues pour chaque page
def accueil(request):
    """
    Render the home page.
    """
    return render(request, 'accueil/index.html')

def a_propos(request):
    """
    Render the 'about' page.
    """
    return render(request, 'accueil/a_propos.html')
def accueil(request):
    return render(request, 'accueil/accueil.html')