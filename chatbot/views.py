from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

#creons les vues pour chaque page

def chatbot(request):
    return render(request, 'chatbot/chatbot.html')