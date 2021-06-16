from django.shortcuts import render
from django.views.generic import DeleteView
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from .models import Device
from .models import Zone
from .models import Session
from .models import Service
from .models import Alert

def start(request):

    return render(request, auth_views.LoginView.as_view(template_name='Users/login.html'))

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
