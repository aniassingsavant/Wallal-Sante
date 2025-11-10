from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def conseils(request):
    return render(request, 'conseils/conseils.html')

def admin_required(user):
    return user.is_staff or user.is_superuser

@user_passes_test(admin_required)
def backoffice_dashboard(request):
    return render(request, 'conseils/backoffice_dashboard.html')

@user_passes_test(admin_required)
def manage_establishments(request):
    return render(request, 'conseils/manage_establishments.html')

def conseils_view(request):
    """Page de conseils avec médecins traditionnels"""
    return render(request, 'conseils/conseils.html')