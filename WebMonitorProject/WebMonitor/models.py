from django.db import models
from bs4 import BeautifulSoup as BS
import subprocess
import time
import random
import requests

class Producent(models.Model):
    
    producent_id = models.IntegerField()
    name = models.CharField(max_length=50)
    status_osOID = models.CharField(max_length=50)
    status_opOID = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Device(models.Model):
    name = models.CharField(max_length=50)
    community_name = models.CharField(max_length=50)
    type = models.CharField(max_length=30)
    producent = models.ForeignKey(Producent, on_delete=models.PROTECT, null=True, blank=True, default=None)
    model = models.CharField(max_length=50)
    macaddress = models.CharField(max_length=20)
    ipaddress = models.GenericIPAddressField()
    sessions = models.PositiveIntegerField(editable=False)
    status = models.NullBooleanField()

    def __str__(self):
        return self.name

    def checkConnection(device):
        time.sleep(5)
        command = "SnmpWalk -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.producent.status_osOID + " -op:" + device.producent.status_opOID + " -q"
        val = 3
        while(True):
            val = subprocess.run(command, shell=True, capture_output=True)
            if val.stdout.decode() == "":
                device.status = None
            elif val.stdout.decode()[0] == "1":
                device.status = True
            elif val.stdout.decode()[0] == '2':
                device.status = False
            else:
                device.status = None
            device.save()
            time.sleep(10)

    def test3(dev):
        dev.status = False
        dev.save()

    def getSessions(device):
        time.sleep(5)
        while(True):
            payload = {'key': 'LUFRPT1DTWoySUdJRnNmRTlUd1I1MXFBc3V0T2VxN0U9eWVhNm5ONk5RaXFwZEJvRG15NkNERTV3SzZQZG9TYlZDcDJSYk56eDZLWXBDSituRmVpbjdySUI5aUVrU21mRA==', 
                       'type': 'op', 
                       'cmd': '<show><session><all><filter><destination>' + device.ipaddress + '</destination><count>yes</count></filter></all></session></show>'
                       }
            r = requests.get(url='https://10.210.41.170/api/', params=payload, verify=False)

            response = r.text
            parsed_response = BS(response, features="html.parser")

            result = parsed_response.find('result').find('member').text

            device.sessions = result
            device.save()
            time.sleep(10)

