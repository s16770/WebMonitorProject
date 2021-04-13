from django.db import models
from bs4 import BeautifulSoup as BS
from django.utils import timezone
from urllib3.exceptions import InsecureRequestWarning
import datetime
import subprocess
import time
import random
import requests
import threading

api_key = 'LUFRPT1DTWoySUdJRnNmRTlUd1I1MXFBc3V0T2VxN0U9eWVhNm5ONk5RaXFwZEJvRG15NkNERTV3SzZQZG9TYlZDcDJSYk56eDZLWXBDSituRmVpbjdySUI5aUVrU21mRA=='

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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


class Producent(models.Model):
    
    producent_id = models.IntegerField()
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Device(models.Model):

    name = models.CharField(max_length=50)
    community_name = models.CharField(max_length=50)
    type = models.CharField(max_length=30)
    producent = models.ForeignKey(Producent, on_delete=models.PROTECT, null=True, blank=True, default=None)
    model = models.CharField(max_length=50)
    ipaddress = models.GenericIPAddressField()
    sessions = models.PositiveIntegerField(editable=False, null=True)
    status = models.CharField(max_length=50, editable=False, null=True)
    storage = models.DecimalField(editable=False, null=True, decimal_places=2, max_digits=10)
    used_storage = models.DecimalField(editable=False, null=True, decimal_places=2, max_digits=10)
    used_storage_warning = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    used_storage_critical = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    used_storage_percentage = models.FloatField(null=True, blank=True, default=1.0)
    free_storage = models.DecimalField(editable=False, null=True, decimal_places=2, max_digits=10)
    cpu_load = models.PositiveIntegerField(editable=False, null=True)
    cpu_load_warning = models.PositiveIntegerField(null=True, blank=True)
    cpu_load_critical = models.PositiveIntegerField(null=True, blank=True)
    temperature = models.IntegerField(editable=False, null=True)
    temperature_warning = models.IntegerField(null=True, blank=True)
    temperature_critical = models.IntegerField(null=True, blank=True)

    #oids
    status_osOID = models.CharField(max_length=100, null=True, blank=True)
    status_opOID = models.CharField(max_length=100, null=True, blank=True)
    transfer_osOID = models.CharField(max_length=100, null=True, blank=True)
    transfer_opOID = models.CharField(max_length=100, null=True, blank=True)
    temperature_osOID = models.CharField(max_length=100, null=True, blank=True)
    temperature_opOID = models.CharField(max_length=100, null=True, blank=True)
    cpu_osOID = models.CharField(max_length=100, null=True, blank=True)
    cpu_opOID = models.CharField(max_length=100, null=True, blank=True)
    storage_osOID = models.CharField(max_length=100, null=True, blank=True)
    storage_opOID = models.CharField(max_length=100, null=True, blank=True)
    storage_alloc_osOID = models.CharField(max_length=100, null=True, blank=True)
    storage_alloc_opOID = models.CharField(max_length=100, null=True, blank=True)
    usedstorage_osOID = models.CharField(max_length=100, null=True, blank=True)
    usedstorage_opOID = models.CharField(max_length=100, null=True, blank=True)

    #storage_his = np.full([480], None)
    #temperature_his = np.full([480], None)
    #cpu_his = np.full([480], None)
    #s_counter = 0
    #t_counter = 0
    #c_counter = 0

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
                t4 = threading.Thread(target=Device.checkStorage, args=[d])
                t5 = threading.Thread(target=Device.checkCPU, args=[d])
                t6 = threading.Thread(target=Device.checkTemperature, args=[d])

                services = Service.objects.filter(device=d)

                for s in services:
                    t7 = threading.Thread(target=Device.checkServices, args=[d, s])

                    t7.start()
                    t7.join()

                for z in zones:
                    t3 = threading.Thread(target=Session.getSessionDetails, args=[firewall, d, z])

                    t3.start()
                    t3.join()
            
                t1.start()
                t2.start()
                t4.start()
                t5.start()
                t6.start()
                
                t1.join()
                t2.join()
                t4.join()
                t5.join()
                t6.join()

            time.sleep(15)
   
    def checkConnection(device):
        
        try:
            command = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.status_osOID + " -op:" + device.status_opOID + " -q"
            val = subprocess.run(command, shell=True, capture_output=True)

            def fun(x):
                return {
                    '1': 'Up',
                    '2': 'Down'
                }.get(x, 'Unknown')

            device.status = fun(val.stdout.decode()[0])
            device.save()
        except:
            print("SnmpWalk failure")


    def checkServices(device, service):
        
        try:
            command = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + service.service_osOID + " -op:" + service.service_opOID + " -q"
            val = subprocess.run(command, shell=True, capture_output=True)

            def fun(x):
                return {
                    '1': 'active',
                    '2': 'continue-pending',
                    '3': 'pause-pending',
                    '4': 'paused'
                }.get(x, 'Unknown')

            service.status = fun(val.stdout.decode()[0])
            service.save()
        except:
            print("SnmpWalk failure")

    def checkStorage(device):

        if device.storage_osOID != None and device.storage_alloc_osOID != None and device.usedstorage_osOID != None:
            try:
                alloc_size_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.storage_alloc_osOID + " -op:" + device.storage_alloc_opOID + " -q"
                size_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.storage_osOID + " -op:" + device.storage_opOID + " -q"
                usedsize_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.usedstorage_osOID + " -op:" + device.usedstorage_opOID + " -q"
                size_val = '0'
                size_alloc_val = '0'
                usedsize_val = '0'
        
                size_val = subprocess.run(size_com, shell=True, capture_output=True)
                size_alloc_val = subprocess.run(alloc_size_com, shell=True, capture_output=True)
                usedsize_val = subprocess.run(usedsize_com, shell=True, capture_output=True)
            
                storage_size = int(size_val.stdout.decode())
                storage_alloc_size = int(size_alloc_val.stdout.decode())
                usedstorage_size = int(usedsize_val.stdout.decode())
            
                GB = 1000000000
                device.storage = float(storage_size*storage_alloc_size/GB)
                device.used_storage = float(usedstorage_size*storage_alloc_size/GB)
                device.free_storage = float(((storage_size*storage_alloc_size) - float(usedstorage_size*storage_alloc_size))/GB)
                device.used_storage_percentage = device.used_storage/device.storage
                device.save()
            except:
                print("SnmpWalk failure")

            
            #storage_his[s_counter] = device.used_storage
            #timeline = [datetime.datetime.now() + datetime.timedelta(minutes=i) for i in range(480)]


    def checkCPU(device):
        
        if device.cpu_osOID != None:   
            try:
                cpu_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.cpu_osOID + " -op:" + device.cpu_opOID + " -q"
            
                cpu_val = '0'
                cpu_val = subprocess.run(cpu_com, shell=True, capture_output=True)
                cpu_load = int(cpu_val.stdout.decode())
            
                device.cpu_load = cpu_load
                device.save()
            except:
                print("SnmpWalk failure")

    
    def checkTemperature(device):
        
        if device.temperature_osOID != None:
            try:
                temp_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.temperature_osOID + " -op:" + device.temperature_opOID + " -q"
            
                temp_val = '0'
                temp_val = subprocess.run(temp_com, shell=True, capture_output=True)
                temperature = int(temp_val.stdout.decode())
            
                device.temperature = temperature
                device.save()
            except:
                print("SnmpWalk failure")
        
        mes = 'Temperature rose to ' + device.temperature + ' C '

        if device.temperature > device.temperature_critical:
            alert = Alert(device=device, message=mes, timestamp=datetime.datetime.now(), type="critical")
            alert.save()
        elif device.temperature > device.temperature_warning:
            alert = Alert(device=device, message=mes, timestamp=datetime.datetime.now(), type="warning")
            alert.save()
    
    def getSessions(device):

        payload_dest = {'key': api_key, 
                       'type': 'op', 
                       'cmd': '<show><session><all><filter><destination>' + device.ipaddress + '</destination><count>yes</count></filter></all></session></show>'
                       }
        #payload_source = {'key': api_key, 
        #               'type': 'op', 
        #               'cmd': '<show><session><all><filter><source>' + device.ipaddress + '</source><count>yes</count></filter></all></session></show>'
        #               }
            
        rd = requests.get(url='https://10.210.41.170/api/', params=payload_dest, verify=False)
        #rs = requests.get(url='https://10.210.41.170/api/', params=payload_source, verify=False)

        response_d = rd.text
        #response_s = rs.text
            
        parsed_response_d = BS(response_d, features="html.parser")
        #parsed_response_s = BS(response_s, features="html.parser")

        result_d = parsed_response_d.find('result').find('member').text
        #result_s = parsed_response_s.find('result').find('member').text

        result = int(result_d)  # + int(result_s)

        device.sessions = result
        device.save()


class Alert(models.Model):

    device = models.ForeignKey(Device, on_delete=models.PROTECT, default=None)
    message = models.CharField(max_length=180)
    timestamp = models.DateTimeField()
    type = models.CharField(max_length=50, default='warning')

    def __str__(self):
        return self.device + ' - ' + self.message + ' at ' + self.timestamp

class Service(models.Model):
    
    name = models.CharField(max_length=50)
    device = models.ForeignKey(Device, on_delete=models.PROTECT, default=None)
    status = models.CharField(max_length=50, editable=False, null=True)
    service_osOID = models.CharField(max_length=200, null=True)
    service_opOID = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

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

