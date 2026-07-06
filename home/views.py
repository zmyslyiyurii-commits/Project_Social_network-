from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')

def openhome_view(request):
    return render(request, 'openhome.html')
