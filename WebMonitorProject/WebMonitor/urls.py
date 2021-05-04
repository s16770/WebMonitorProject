from django.urls import path
from django.contrib import admin
from . import views
from .models import Device
from .models import Zone
from .models import Firewall
import threading


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='webmonitorhome'),
    path('device/<devicename>', views.deviceInfo, name='wmdeviceinfo'),
    path('alerts/', views.alerts, name='wmalerts'),
    path('alerts/<object_id>', views.alertDelete, name='delete_alert') 
]

t1 = threading.Thread(target=Device.poll)

t1.start()
