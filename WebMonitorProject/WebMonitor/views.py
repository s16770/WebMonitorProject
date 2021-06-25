from django.shortcuts import render
from django.views.generic import DeleteView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Device
from .models import Zone
from .models import Session
from .models import Service
from .models import Alert

@login_required(login_url='/login/')
def dashboard(request):
    """funkcja obslugujaca prezentacje panelu glownego aplikacji"""
    context = {
        'devices': Device.objects.all()
    }
    return render(request, 'WebMonitor/dashboard.html', context)

@login_required(login_url='/login/')
def deviceInfo(request, devicename):
    """funkcja obslugujaca prezentacje panelu szczegolowych informacji o urzadzeniu """
    context = {
        'devicename': Device.objects.get(name=devicename),
        'zones': Zone.objects.all(),
        'sessions': Session.objects.filter(device=Device.objects.get(name=devicename)),
        'services': Service.objects.filter(device=Device.objects.get(name=devicename))
    }
    return render(request, 'WebMonitor/deviceInfo.html', context)

class PostDeleteView(DeleteView):
    """funkcja obslugujaca usuniecie alertu oraz prezentacje panelu potwierdzenia usuniecia"""
    model = Alert
    success_url = '/alerts/'

@login_required(login_url='/login/')
def alerts(request):
    """funkcja obslugujaca prezentacje panelu alertow"""

    context = {
        'alerts': Alert.objects.all()
    }
    return render(request, 'WebMonitor/alerts.html', context)
