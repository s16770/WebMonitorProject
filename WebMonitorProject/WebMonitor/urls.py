from django.urls import path
from . import views
from .models import Device
import threading


urlpatterns = [
    path('', views.dashboard, name='webmonitorhome'),
]

d1 = Device.objects.get(name='ADServer')
d2 = Device.objects.get(name='SW_Internal')

Device.test3(d1)
Device.test3(d2)

#t1 = threading.Thread(target=Device.checkConnection, args=[d1, '.1.3.6.1.2.1.2.2.1.8.12', '.1.3.6.1.2.1.2.2.1.8.13'])
#t2 = threading.Thread(target=Device.checkConnection, args=[d2, '.1.3.6.1.2.1.2.2.1.8.33', '..1.3.6.1.2.1.2.2.1.8.34'])

#t1.start()
#t2.start()

print(Device.getSessions('10.210.134.20'))