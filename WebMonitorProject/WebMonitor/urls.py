from django.urls import path
from django.contrib import admin
from . import views
from .models import Device
from .models import Zone
from .models import Firewall
import threading
from .views import PostDeleteView

urlpatterns = [
    path('', views.start, name='startingpage'),
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard, name='webmonitorhome'),
    path('device/<devicename>/', views.deviceInfo, name='wmdeviceinfo'),
    path('alerts/', views.alerts, name='wmalerts'),
    path('alerts/<int:pk>/delete/', PostDeleteView.as_view(), name='delete_alert') 
]

t1 = threading.Thread(target=Device.poll)

t1.start()
