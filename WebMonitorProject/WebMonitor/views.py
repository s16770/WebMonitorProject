from django.shortcuts import render
from django.http import HttpResponse
from .models import Device


def dashboard(request):
    context = {
        'devices': Device.objects.all()
    }
    return render(request, 'WebMonitor/dashboard.html', context)

def deviceInfo(request, devicename):
    context = {
        'devicename': Device.objects.get(name=devicename)
    }
    return render(request, 'WebMonitor/deviceInfo.html', context)
