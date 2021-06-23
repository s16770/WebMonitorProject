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
    context = {
        'devices': Device.objects.all()
    }
    return render(request, 'WebMonitor/dashboard.html', context)

@login_required(login_url='/login/')
def deviceInfo(request, devicename):
    context = {
        'devicename': Device.objects.get(name=devicename),
        'zones': Zone.objects.all(),
        'sessions': Session.objects.filter(device=Device.objects.get(name=devicename)),
        'services': Service.objects.filter(device=Device.objects.get(name=devicename))
    }
    return render(request, 'WebMonitor/deviceInfo.html', context)

@login_required(login_url='/login/')
class PostDeleteView(DeleteView):
    model = Alert
    success_url = '/alerts/'

@login_required(login_url='/login/')
def alerts(request):

    context = {
        'alerts': Alert.objects.all()
    }
    return render(request, 'WebMonitor/alerts.html', context)
