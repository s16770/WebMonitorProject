from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DeleteView
from django.http import HttpResponse
from .models import Device
from .models import Zone
from .models import Session
from .models import Service
from .models import Alert

def dashboard(request):
    context = {
        'devices': Device.objects.all()
    }
    return render(request, 'WebMonitor/dashboard.html', context)

def deviceInfo(request, devicename):
    context = {
        'devicename': Device.objects.get(name=devicename),
        'zones': Zone.objects.all(),
        'sessions': Session.objects.filter(device=Device.objects.get(name=devicename)),
        'services': Service.objects.filter(device=Device.objects.get(name=devicename))
    }
    return render(request, 'WebMonitor/deviceInfo.html', context)


class PostDeleteView(DeleteView):
    model = Alert
    success_url = '/alerts/'

def alerts(request):

    context = {
        'alerts': Alert.objects.all()
    }
    return render(request, 'WebMonitor/alerts.html', context)
