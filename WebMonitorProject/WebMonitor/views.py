from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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

def alerts(request):
    context = {
        'alerts': Alert.objects.all()
    }
    return render(request, 'WebMonitor/alerts.html', context)

def alertDelete(request, alert_id): 
    object = Alert.objects.get(id=alert_id) 
    object.delete() 
    
    return HttpResponseRedirect(request.GET.get('/alerts/'))
