from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

#creons les vues pour chaque page
def connexion(request):
    """
    Render the home page.
    """
    return render(request, 'user/connexion.html')
def inscription(request):
    """
    Render the home page.
    """
    return render(request, 'user/inscription.html')
