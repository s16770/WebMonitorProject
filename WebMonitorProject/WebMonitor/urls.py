from django.urls import path
from . import views
from .models import Device
import threading

urlpatterns = [
    path('', views.dashboard, name='webmonitorhome'),
    path('device/<devicename>', views.deviceInfo, name='wmdeviceinfo'),
]

t1 = threading.Thread(target=Device.poll)

t1.start()
