from django.shortcuts import render
from django.http import HttpResponse
from .models import Device
from .models import Zone
from .models import Session
from .models import Service

def dashboard(request):
    context = {
        'devices': Device.objects.all()
    }
    return render(request, 'WebMonitor/dashboard.html', context)

def deviceInfo(request, devicename):
    context = {
        'devicename': Device.objects.get(name=devicename),
        'zones': Zone.objects.all(),
        'sessions': Session.objects.all(),
        'services': Service.objects.filter(device=Device.objects.get(name=devicename))
    }
    return render(request, 'WebMonitor/deviceInfo.html', context)
