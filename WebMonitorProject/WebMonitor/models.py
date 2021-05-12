from django.db import models
from django.contrib.auth.models import User
from bs4 import BeautifulSoup as BS
from django.utils import timezone
from urllib3.exceptions import InsecureRequestWarning
from django.core.mail import send_mail
from decimal import *
import pytz
import datetime
import subprocess
import time
import random
import requests
import threading

api_key = 'LUFRPT1DTWoySUdJRnNmRTlUd1I1MXFBc3V0T2VxN0U9eWVhNm5ONk5RaXFwZEJvRG15NkNERTV3SzZQZG9TYlZDcDJSYk56eDZLWXBDSituRmVpbjdySUI5aUVrU21mRA=='
remote_access = {'ssh', 'ssl', 'rsh', 'ms-rdp', 'telnet', 'anydesk', 'windows-remote-management'}
light = {'dns', 'ping', 'msrpc-base', 'ms-wmi'}

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def alert_notification(alert):

        users = User.objects.all()

        for u in users:
            send_mail(
                'WebMonitor Alert!',
                alert.message,
                'webmonitors16770@gmail.com',
                [u.email],
                fail_silently=False,
            )

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
            
            r = requests.get(url='https://' + firewall.domain_name + '/api/', params=payload, verify=False)

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
    used_storage_percentage = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10, editable=False)
    free_storage = models.DecimalField(editable=False, null=True, decimal_places=2, max_digits=10)
    cpu_load = models.PositiveIntegerField(editable=False, null=True)
    cpu_load_warning = models.PositiveIntegerField(null=True, blank=True)
    cpu_load_critical = models.PositiveIntegerField(null=True, blank=True)
    temperature = models.IntegerField(editable=False, null=True)
    temperature_warning = models.IntegerField(null=True, blank=True)
    temperature_critical = models.IntegerField(null=True, blank=True)
    session_count_warning = models.IntegerField(null=True, blank=True)
    session_count_critical = models.IntegerField(null=True, blank=True)

    #oids
    status_osOID = models.CharField(max_length=100, null=True, blank=True)
    status_opOID = models.CharField(max_length=100, null=True, blank=True)
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
                t4 = threading.Thread(target=Device.checkStorage, args=[d])
                t5 = threading.Thread(target=Device.checkCPU, args=[d])
                t6 = threading.Thread(target=Device.checkTemperature, args=[d])

                services = Service.objects.filter(device=d)

                for s in services:
                    t7 = threading.Thread(target=Device.checkServices, args=[d, s])

                    t7.start()
                    t7.join()

                t2 = threading.Thread(target=Device.getSessions, args=[d, firewall])
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

            if device.status != fun(val.stdout.decode()[0]) and fun(val.stdout.decode()[0]) != 'Up':
                mes = device.name + ' interface state changed to ' + fun(val.stdout.decode()[0]) + ' at ' + pytz.utc.localize(datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), category='Connection')
                alert.save()
                alert_notification(alert)

            device.status = fun(val.stdout.decode()[0])
            device.save()
        except:
            print(device.name + " snmpwalk failure - connection")


    def checkServices(device, service):
        
        try:
            command = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + service.service_osOID + " -op:" + service.service_opOID + " -q"
            val = subprocess.run(command, shell=True, capture_output=True)

            def fun(x):
                return {
                    '0': 'stopped',
                    '1': 'active',
                    '2': 'continue-pending',
                    '3': 'pause-pending',
                    '4': 'paused'
                }.get(x, 'Unknown')

            if service.status != None:
                    if service.status != fun(val.stdout.decode()[0]) and fun(val.stdout.decode()[0]) != 'active':
                        mes = device.name + ' ' + service.name + ' status changed to ' + fun(val.stdout.decode()[0]) + ' at ' +  pytz.utc.localize(datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                        alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="critical", category='Service')
                        alert.save()
                        alert_notification(alert)

            service.status = fun(val.stdout.decode()[0])
            service.save()
        except:
            print(device.name + " snmpwalk failure - services")

    def checkStorage(device):

        if device.storage_osOID != None and device.usedstorage_osOID != None:
            try:
                size_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.storage_osOID + " -op:" + device.storage_opOID + " -q"
                usedsize_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.usedstorage_osOID + " -op:" + device.usedstorage_opOID + " -q"
                size_val = '0'
                size_alloc_val = '0'
                usedsize_val = '0'
                
                if(device.storage_alloc_osOID != None):
                    alloc_size_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.storage_alloc_osOID + " -op:" + device.storage_alloc_opOID + " -q"
                    size_alloc_val = subprocess.run(alloc_size_com, shell=True, capture_output=True)
                    storage_alloc_size = int(size_alloc_val.stdout.decode())
                else:
                    storage_alloc_size = 1024
                
                size_val = subprocess.run(size_com, shell=True, capture_output=True)
                usedsize_val = subprocess.run(usedsize_com, shell=True, capture_output=True)
            
                storage_size = int(size_val.stdout.decode())
                usedstorage_size = int(usedsize_val.stdout.decode())
                GB = 1024*1024*1024

                usp_tmp = (usedstorage_size*storage_alloc_size/GB)/(storage_size*storage_alloc_size/GB)*100
                uss_tmp = usedstorage_size*storage_alloc_size/GB
                if device.used_storage != None:
                    if Decimal(device.used_storage).quantize(Decimal('.01')) != Decimal(uss_tmp).quantize(Decimal('.01')):
                        mes = device.name + ' used storage percentage equal to ' + '{0:.2g}'.format(Decimal(str(usp_tmp))) + '% at ' +  pytz.utc.localize(datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                        if  usedstorage_size/storage_size > device.used_storage_critical:
                            alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="critical", category='Storage')
                            alert.save()
                            alert_notification(alert)
                        elif usedstorage_size/storage_size > device.used_storage_warning:
                            alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="warning", category='Storage')
                            alert.save()
                            alert_notification(alert)

                device.storage = storage_size*storage_alloc_size/GB
                device.used_storage = usedstorage_size*storage_alloc_size/GB
                device.free_storage = (((storage_size*storage_alloc_size) - (usedstorage_size*storage_alloc_size))/GB)
                device.used_storage_percentage = device.used_storage/device.storage
                device.save()

            except:
                print(device.name + " snmpwalk failure - storage")


    def checkCPU(device):
        
        if device.cpu_osOID != None:   
            try:
                cpu_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.cpu_osOID + " -op:" + device.cpu_opOID + " -q"
            
                cpu_val = '0'
                cpu_val = subprocess.run(cpu_com, shell=True, capture_output=True)
                cpu_load = int(cpu_val.stdout.decode())
                
                if device.cpu_load != None:
                    if device.cpu_load != cpu_load and device.cpu_load < cpu_load:
                        mes = device.name + ' CPU load equal to ' + str(cpu_load) + '% at ' +  pytz.utc.localize(datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                        if cpu_load > device.cpu_load_critical:
                            alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="critical", category='CPU')
                            alert.save()
                            alert_notification(alert)
                        elif cpu_load > device.cpu_load_warning:
                            alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="warning", category='CPU')
                            alert.save()
                            alert_notification(alert)

                device.cpu_load = cpu_load
                device.save()
            except:
                print(device.name + " snmpwalk failure - cpu")

    
    def checkTemperature(device):
        
        if device.temperature_osOID != None:
            try:
                temp_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + device.temperature_osOID + " -op:" + device.temperature_opOID + " -q"
            
                temp_val = '0'
                temp_val = subprocess.run(temp_com, shell=True, capture_output=True)
                temperature = int(temp_val.stdout.decode())
                
                if device.temperature != None:
                    if device.temperature != temperature and device.temperature < temperature:
                        mes = device.name + ' temperature equal to ' + str(temperature) + 'C at ' +  pytz.utc.localize(datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                        if temperature > device.temperature_critical:
                            alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="critical", category='Temperature')
                            alert.save()
                            alert_notification(alert)
                        elif temperature > device.temperature_warning:
                            alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="warning", category='Temperature')
                            alert.save()
                            alert_notification(alert)

                device.temperature = temperature
                device.save()

            except:
                print(device.name + " snmpwalk failure - temperature")
        
    
    def getSessions(device, firewall):

        payload_dest = {'key': api_key, 
                       'type': 'op', 
                       'cmd': '<show><session><all><filter><destination>' + device.ipaddress + '</destination><count>yes</count></filter></all></session></show>'
                       }
        payload_nat = {'key': api_key, 
                    'type': 'op', 
                    'cmd': '<show><session><all><filter><nat>both</nat></filter></all></session></show>'
                     }

        rd = requests.get(url='https://' + firewall.domain_name + '/api/', params=payload_dest, verify=False)
        rnat = requests.get(url='https://' + firewall.domain_name +'/api/', params=payload_nat, verify=False)

        response_d = rd.text
        response_nat = rnat.text
        soup_nat = BS(response_nat, features='lxml')
        parsed_response_d = BS(response_d, features="html.parser")

        result_d = parsed_response_d.find('result').find('member').text
        nat_entries = soup_nat.find_all('entry')
        result_nat = 0;

        for e in nat_entries:
            if e.xdst.get_text() == device.ipaddress:
                result_nat = result_nat + 1

        
        result = int(result_d) + result_nat

        if device.session_count_warning != None and device.session_count_critical != None:
            mes = device.name + ' session count equal to ' + str(result) + ' at ' +  pytz.utc.localize(datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
            if result > device.session_count_critical:
                alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="critical", category='Session count')
                alert.save()
                alert_notification(alert)
            elif result > device.session_count_warning:
                alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="warning", category='Session count')
                alert.save()
                alert_notification(alert)

        device.sessions = result
        device.save()


class Alert(models.Model):

    device = models.ForeignKey(Device, on_delete=models.PROTECT, default=None)
    message = models.CharField(max_length=180)
    timestamp = models.DateTimeField()
    type = models.CharField(max_length=50, default='warning')
    category = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.message

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
    start_time = models.DateTimeField(null=True, default=None)
    alert_couse = models.CharField(max_length=50, null=True, default='')

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
            
        r = requests.get(url='https://' + firewall.domain_name +'/api/', params=payload, verify=False)
        rnat = requests.get(url='https://' + firewall.domain_name +'/api/', params=payload_nat, verify=False)
        ruser = requests.get(url='https://' + firewall.domain_name +'/api/', params=payload_user, verify=False)
        
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
        alerts = Alert.objects.filter(device=device)

        storage_tmp_val = 0
        for s in session_details:
            storage_tmp_val = storage_tmp_val + int(s.find('total-byte-count').get_text())

        storage_avg = 1000000
        if len(session_details) != 0:
            storage_avg = storage_tmp_val/len(session_details)

        for s in session_details:
            username = ""
            for u in user_entries:
                if s.source.get_text() == u.ip.get_text():
                    username = u.user.get_text()
            
            session_datetime_tmp = datetime.datetime.strptime(s.find('start-time').get_text(), "%a %B  %d %H:%M:%S %Y") 
            starttime = pytz.utc.localize(session_datetime_tmp)
            couse = ''
            s_zone = Zone.objects.get(name=s.find('from').get_text())
            for alert in alerts:
                if alert.category == 'Storage' and int(s.find('total-byte-count').get_text()) > storage_avg and starttime < alert.timestamp:
                    for app in light:
                        if(app == s.application.get_text()):
                            break
                        couse = alert.category
                elif alert.category == 'CPU' and starttime < alert.timestamp and starttime > alert.timestamp - datetime.timedelta(minutes=15):
                    for app in light:
                        if(app == s.application.get_text()):
                            break
                        couse = alert.category
                elif alert.category == 'Session count' and starttime < alert.timestamp and starttime > alert.timestamp - datetime.timedelta(minutes=5):
                    couse = alert.category
                elif alert.category == 'Connection' or alert.category == 'Service' and starttime < alert.timestamp:
                    for app in remote_access:
                        if(app == s.application.get_text()):
                            couse = alert.category
                            break
        
            session = Session(device=device, source_zone=s_zone, source_ip=s.source.get_text(), user=username, application=s.application.get_text(), transfer=int(s.find('total-byte-count').get_text()), start_time=starttime, alert_couse=couse)
            session.save()

