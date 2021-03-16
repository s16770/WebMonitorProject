from django.urls import path
from . import views
from .models import Device



urlpatterns = [
    path('', views.dashboard, name='webmonitorhome'),
    path('device/<devicename>', views.deviceInfo, name='wmdeviceinfo'),
]

d1 = Device.objects.get(name='ADServer')
d2 = Device.objects.get(name='SW_Internal')

Device.test3(d1)
Device.test3(d2)

Device.snmp_poll()
Device.api_poll()

#t1 = threading.Thread(target=Device.checkConnection, args=[d1])
#t2 = threading.Thread(target=Device.checkConnection, args=[d2])
#t3 = threading.Thread(target=Device.getSessions, args=[d1])
#t4 = threading.Thread(target=Device.getSessions, args=[d2])

#t1.start()
#t2.start()
#t3.start()
#t4.start()