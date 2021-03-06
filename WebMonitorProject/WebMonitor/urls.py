from django.urls import path
from . import views
from .models import Device
import threading

urlpatterns = [
    path('', views.dashboard, name='webmonitorhome'),
]

d = Device.objects.get(name='ADServer')

t = threading.Thread(target=Device.checkConnection, args=[d, '.1.3.6.1.2.1.2.2.1.8.33', '..1.3.6.1.2.1.2.2.1.8.34'])

Device.test3(d)

t.start()
