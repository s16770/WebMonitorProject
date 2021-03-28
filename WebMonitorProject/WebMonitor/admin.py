from django.contrib import admin
from .models import Device
from .models import Producent
from .models import Firewall
from .models import Service

admin.site.register(Device)
admin.site.register(Producent)
admin.site.register(Firewall)
admin.site.register(Service)