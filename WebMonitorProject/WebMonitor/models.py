from django.db import models
from bs4 import BeautifulSoup as BS
from django.utils import timezone
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
            
            r = requests.get(url='https://10.210.41.170/api/', params=payload, verify=False)

            response = r.content
            soup = BS(response, features='lxml')

            result = soup.find('zone').find_all('entry')

            for elem in result:
                if not Zone.objects.filter(name = elem.get('name')):
                   new_zone = Zone(name = elem.get('name'))
                   new_zone.save()


class Service(models.Model):
    
    name = models.CharField(max_length=50)
    port = models.PositiveIntegerField()
    service_osOID = models.CharField(max_length=50, null=True)
    service_opOID = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class Producent(models.Model):
    
    producent_id = models.IntegerField()
    name = models.CharField(max_length=50)
    status_osOID = models.CharField(max_length=50)
    status_opOID = models.CharField(max_length=50)
    transfer_osOID = models.CharField(max_length=50, null=True)
    transfer_opOID = models.CharField(max_length=50, null=True)
    temperature_osOID = models.CharField(max_length=50, null=True)
    temperature_opOID = models.CharField(max_length=50, null=True)
    storage_osOID = models.CharField(max_length=50, null=True)
    storage_opOID = models.CharField(max_length=50, null=True)
    storage_alloc_osOID = models.CharField(max_length=50, null=True)
    storage_alloc_opOID = models.CharField(max_length=50, null=True)
    freestorage_osOID = models.CharField(max_length=50, null=True)
    freestorage_opOID = models.CharField(max_length=50, null=True)
    freestorage_alloc_osOID = models.CharField(max_length=50, null=True)
    freestorage_alloc_opOID = models.CharField(max_length=50, null=True)
    services = models.ManyToManyField(Service, null=True, blank=True)

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
    storage = models.FloatField(null=True)
    free_storage = models.FloatField(null=True)

    def __str__(self):
        return self.name

    def poll():

        firewall = Firewall.objects.get(domain_name='pa-vm.wmproject.com')
        Firewall.getZones(firewall)
        zones = Zone.objects.all()

        while(True):
            devices = Device.objects.all()
            Session.objects.all().delete()
            
            for d in devices:
                t1 = threading.Thread(target=Device.checkConnection, args=[d])
                t2 = threading.Thread(target=Device.getSessions, args=[d])

                for z in zones:
                    t3 = threading.Thread(target=Session.getSessionDetails, args=[firewall, d, z])

                    t3.start()
                    t3.join()
            
                t1.start()
                t2.start()
                
                t1.join()
                t2.join()


            time.sleep(15)
   
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

    def checkStorage(device):
        #SnmpWalk -r:10.210.134.20 -c:ADServer -os:.1.3.6.1.2.1.25.2.3.1.5.0 -op:.1.3.6.1.2.1.25.2.3.1.5.1 -q
        alloc_size_com = "SnmpWalk -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.producent.storage_alloc_osOID + " -op:" + device.producent.storage_alloc_opOID + " -q"
        alloc_freesize_com = "SnmpWalk -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.producent.freestorage_alloc_osOID + " -op:" + device.producent.freestorage_alloc_opOID + " -q"
        size_com = "SnmpWalk -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.producent.storage_osOID + " -op:" + device.producent.storage_opOID + " -q"
        freesize_com = "SnmpWalk -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.producent.freestorage_osOID + " -op:" + device.producent.freestorage_opOID + " -q"
        try:
            size_val = subprocess.run(size_com, shell=True, capture_output=True)
            size_alloc_val = subprocess.run(alloc_size_com, shell=True, capture_output=True)
            freesize_val = subprocess.run(freesize_com, shell=True, capture_output=True)
            freesize_alloc_val = subprocess.run(alloc_freesize_com, shell=True, capture_output=True)

            storage_size = int(size_val.stdout.decode())
            storage_alloc_size = int(size_alloc_val.stdout.decode())
            freestorage_size = int(freesize_val.stdout.decode())
            freestorage_alloc_size = int(freesize_alloc_val.stdout.decode())

            GB = 1000000000
            device.storage = float(storage_size*storage_alloc_size/GB)
            device.free_storage = float(freestorage_size*freestorage_alloc_size/GB)

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

    

class Session(models.Model):
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    source_zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    source_ip = models.CharField(max_length=20)
    user = models.CharField(max_length=50, null=True)
    application = models.CharField(max_length=30)
    transfer = models.PositiveIntegerField()
    start_time = models.CharField(max_length=30, null=True)

    def getSessionDetails(firewall, device, zone):
        
        payload = {'key': api_key, 
                   'type': 'op', 
                   'cmd': '<show><session><all><filter><from>' + zone.name + '</from><destination>' + device.ipaddress +  '</destination></filter></all></session></show>'
                    }

        payload_nat = {'key': api_key, 
                    'type': 'op', 
                    'cmd': '<show><session><all><filter><nat>both</nat></filter></all></session></show>'
                     }

        payload_user = {'key': api_key, 
                    'type': 'op', 
                    'cmd': '<show><user><ip-user-mapping><all></all></ip-user-mapping></user></show>'
                     }
            
        r = requests.get(url='https://10.210.41.170/api/', params=payload, verify=False)
        rnat = requests.get(url='https://10.210.41.170/api/', params=payload_nat, verify=False)
        ruser = requests.get(url='https://10.210.41.170/api/', params=payload_user, verify=False)
        
        response = r.text
        response_nat = rnat.text
        response_user = ruser.text

        soup = BS(response, features='lxml')
        soup_nat = BS(response_nat, features='lxml')
        soup_user = BS(response_user, features='lxml')

        user_entries = soup_user.find_all('entry')
        nat_entries = soup_nat.find_all('entry')
        result = soup.find_all('entry')
        result_nat = []

        for e in nat_entries:
            if e.xdst.get_text() == device.ipaddress:
                result_nat.append(e)
       
        
        session_details = result + result_nat

        for s in session_details:
            username = ""
            for u in user_entries:
                if s.source.get_text() == u.ip.get_text():
                    username = u.user.get_text()

            #ogarnac format daty w ponizszym
            session = Session(device=device, source_zone=zone, source_ip=s.source.get_text(), user=username, application=s.application.get_text(), transfer=int(s.find('total-byte-count').get_text())/10, start_time=s.find('start-time').get_text())
            session.save()

