from django.db import models
from bs4 import BeautifulSoup as BS
import subprocess
import time
import random
import requests
import threading

api_key = 'LUFRPT1DTWoySUdJRnNmRTlUd1I1MXFBc3V0T2VxN0U9eWVhNm5ONk5RaXFwZEJvRG15NkNERTV3SzZQZG9TYlZDcDJSYk56eDZLWXBDSituRmVpbjdySUI5aUVrU21mRA=='

class Zone(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Firewall(models.Model):

    domain_name = models.CharField(max_length=50)
    ipaddress = models.GenericIPAddressField()
    zones = models.ManyToManyField(Zone, null=True, blank=True)

    def __str__(self):
        return self.domain_name

    def getZones(firewall):
            
            payload = {'key': api_key, 
                       'type': 'config',
                       'action': 'get',
                       'xpath': "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/zone"
                       }
            
            r = requests.get(url='https://' + firewall.ipaddress + '/api/', params=payload, verify=False)

            response = r.content
            soup = BS(response, features='lxml')

            result = soup.find('zone').find_all('entry')

            for elem in result:
                if not Zone.objects.filter(name = elem.get('name')):
                   new_zone = Zone(name = elem.get('name'))
                   new_zone.save()

            #<show><session><all><filter><from>Trust</from><destination>10.210.134.60</destination></filter></all></session></show>


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
    ipaddress = models.GenericIPAddressField()
    nat_ipaddress = models.GenericIPAddressField(null=True)
    sessions = models.PositiveIntegerField(editable=False, null=True)
    status = models.BooleanField(editable=False, null=True)

    def __str__(self):
        return self.name

    def poll():

        Firewall.getZones(Firewall.objects.get(domain_name='pa-vm.wmproject.com'))

        while(True):
            devices = Device.objects.all()
            
            for d in devices:
                t1 = threading.Thread(target=Device.checkConnection, args=[d])
                t2 = threading.Thread(target=Device.getSessions, args=[d])

                t1.start()
                t2.start()

                t1.join()
                t2.join()

            time.sleep(10)
   
    def checkConnection(device):
        command = "SnmpWalk -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.producent.status_osOID + " -op:" + device.producent.status_opOID + " -q"
        val = 3
        try:
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
        except:
            print("SnmpWalk failure")

    def getSessions(device):
        payload_dest = {'key': api_key, 
                       'type': 'op', 
                       'cmd': '<show><session><all><filter><destination>' + device.ipaddress + '</destination><count>yes</count></filter></all></session></show>'
                       }
        payload_source = {'key': api_key, 
                       'type': 'op', 
                       'cmd': '<show><session><all><filter><source>' + device.ipaddress + '</source><count>yes</count></filter></all></session></show>'
                       }
            
        rd = requests.get(url='https://10.210.41.170/api/', params=payload_dest, verify=False)
        rs = requests.get(url='https://10.210.41.170/api/', params=payload_source, verify=False)

        response_d = rd.text
        response_s = rs.text
            
        parsed_response_d = BS(response_d, features="html.parser")
        parsed_response_s = BS(response_s, features="html.parser")

        result_d = parsed_response_d.find('result').find('member').text
        result_s = parsed_response_s.find('result').find('member').text

        result = int(result_d) + int(result_s)

        device.sessions = result
        device.save()

        def getSessionDetails(firewall, device, zone):
            
            payload = {'key': api_key, 
                       'type': 'op', 
                       'cmd': '<show><session><all><filter><from>' + zone.name + '</from><destination>' + device.ipaddress +  '</destination></filter></all></session></show>'
                       }

            payload_nat = {'key': api_key, 
                       'type': 'op', 
                       'cmd': '<show><session><all><filter><from>' + zone.name + '</from><destination>' + device.nat_ipaddress +  '</destination></filter></all></session></show>'
                       }
            
            r = requests.get(url='https://' + firewall.ipaddress + '/api/', params=payload, verify=False)

            response = r.content
            soup = BS(response, features='lxml')

            result = soup.find('zone').find_all('entry')

            
        