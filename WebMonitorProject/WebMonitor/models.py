from django.db import models
from django.contrib.auth.models import User
from bs4 import BeautifulSoup as BS
from django.utils import timezone
from urllib3.exceptions import InsecureRequestWarning
from django.core.mail import send_mail
from decimal import *
from WebMonitor.SnmpWalk import SnmpWalk
import pytz
import datetime
import time
import random
import requests
import threading

remote_access = {'ssh', 'ssl', 'rsh', 'ms-rdp', 'telnet', 'anydesk', 'windows-remote-management'}
light = {'msrpc-base', 'ms-wmi'}
GB = 1024*1024*1024

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def alert_notification(alert):
    """funkcja sluzaca wyslaniu powiadomienia e-mail"""

    users = User.objects.all()

    for user in [u for u in users if u.email != None]:
        send_mail(
            'WebMonitor Alert!',
            alert.message,
            'webmonitors16770@gmail.com',
            [user.email],
            fail_silently=False,
        )

def os_oid(opOID):
    """funkcja generujaca OID poczatkowy (os) na podstawie OIDu koncowego (op)"""

    replace_char = opOID[len(opOID)-1]
    
    if replace_char == '0':
        replace_sec_char = opOID[len(opOID)-2]
        if replace_sec_char == '1':
            return opOID[:-2] + '9'
        else:
            replace_tmp = int(replace_sec_char)-1
            os_char = str(replace_tmp)
            return opOID[:-2] + os_char + '9'

    replace_tmp = int(replace_char)-1
    os_char = str(replace_tmp)

    return opOID[:-1] + os_char


class Producent(models.Model):
    
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Firewall(models.Model):

    domain_name = models.CharField(max_length=50)
    ipaddress = models.GenericIPAddressField()
    api_key = models.CharField(max_length=200, blank=True)
    producent = models.ForeignKey(Producent, on_delete=models.PROTECT)

    def __str__(self):
        return self.domain_name

    def getZones(self):
        """funkcja pobierajaca strefy bezpieczenstwa z zapory sieciowej Palo Alto Networks"""
            
        payload = {'key': self.api_key, 
                   'type': 'config',
                   'action': 'get',
                   'xpath': "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/zone"
                   }
        
        r = requests.get(url='https://' + self.domain_name + '/api/', params=payload, verify=False)

        response = r.content
        soup = BS(response, features='lxml')

        result = soup.find('zone').find_all('entry')

        for elem in [el for el in result if not Zone.objects.filter(name = el.get('name'))]:
            new_zone = Zone(name = elem.get('name'))
            new_zone.save()


class Zone(models.Model):

    name = models.CharField(max_length=30)
    firewall = models.ForeignKey(Firewall, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Device(models.Model):

    name = models.CharField(max_length=50)
    community_name = models.CharField(max_length=50)
    type = models.CharField(max_length=30)
    producent = models.ForeignKey(Producent, on_delete=models.PROTECT)
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
    status_opOID = models.CharField(max_length=100, null=True, blank=True)
    temperature_opOID = models.CharField(max_length=100, null=True, blank=True)
    cpu_opOID = models.CharField(max_length=100, null=True, blank=True)
    storage_opOID = models.CharField(max_length=100, null=True, blank=True)
    storage_alloc_opOID = models.CharField(max_length=100, null=True, blank=True)
    usedstorage_opOID = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    def poll():
        """funkcja wywolujaca asynchronicznie inne funkcje sluzace do zbierania danych z urzadzen i zapory sieciowej"""

        firewall = Firewall.objects.get(domain_name='pa-vm.wmproject.com')
        firewall.getZones()
        zones = Zone.objects.all()

        while(True):
            devices = Device.objects.all()

            time.sleep(3)
            Session.objects.all().delete()
            
            for device in devices:
                t1 = threading.Thread(target=Device.checkConnection, args=[device])
                t4 = threading.Thread(target=Device.checkStorage, args=[device])
                t5 = threading.Thread(target=Device.checkCPU, args=[device])
                t6 = threading.Thread(target=Device.checkTemperature, args=[device])

                services = Service.objects.filter(device=device)

                for service in services:
                    t7 = threading.Thread(target=Device.checkServices, args=[device, service])

                    t7.start()
                    t7.join()

                t2 = threading.Thread(target=Device.getSessions, args=[device, firewall])
                for zone in zones:
                    t3 = threading.Thread(target=Session.getSessionDetails, args=[firewall, device, zone])

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

            time.sleep(50)

    def checkConnection(device):
        """funkcja sprawdzajaca stan monitorowanego interfejsu"""
        
        if device.status_opOID == None or device.status_opOID.strip() == '':
            return
        try:
            command = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + os_oid(device.status_opOID) + " -op:" + device.status_opOID + " -q"
            val = SnmpWalk.snmpWalkCall(command=command)

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
        """funkcja sprawdzajaca stan serwisow hostowanych na urzadzeniu"""
        
        if service.service_opOID == None or service.service_opOID.strip() == '':
            return
        try:
            command = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + os_oid(service.service_opOID) + " -op:" + service.service_opOID + " -q"
            val = SnmpWalk.snmpWalkCall(command=command)

            def fun(x):
                return {
                    '0': 'stopped',
                    '1': 'active',
                    '2': 'continue-pending',
                    '3': 'pause-pending',
                    '4': 'paused'
                }.get(x, 'Unknown')

            if service.status != None and service.status != fun(val.stdout.decode()[0]) and fun(val.stdout.decode()[0]) != 'active':
                mes = device.name + ' ' + service.name + ' status changed to ' + fun(val.stdout.decode()[0]) + ' at ' +  pytz.utc.localize(datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                alert = Alert(device=device, message=mes, timestamp=pytz.utc.localize(datetime.datetime.now()), type="critical", category='Service')
                alert.save()
                alert_notification(alert)

            service.status = fun(val.stdout.decode()[0])
            service.save()
        except:
            print(device.name + " snmpwalk failure - services")

    def checkStorage(device):
        """funkcja sprawdzajaca wielkosc oraz zajetosc dysku monitorowanego urzadzenia"""

        if device.storage_opOID == None or device.usedstorage_opOID == None or device.storage_opOID.strip() == '' or device.usedstorage_opOID.strip() == '':
            return
        try:
            size_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + os_oid(device.storage_opOID) + " -op:" + device.storage_opOID + " -q"
            usedsize_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + os_oid(device.usedstorage_opOID) + " -op:" + device.usedstorage_opOID + " -q"
            size_val = '0'
            size_alloc_val = '0'
            usedsize_val = '0'
            
            if(device.storage_alloc_opOID != None):
                alloc_size_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + os_oid(device.storage_alloc_opOID) + " -op:" + device.storage_alloc_opOID + " -q"
                size_alloc_val = SnmpWalk.snmpWalkCall(command=alloc_size_com)
                storage_alloc_size = int(size_alloc_val.stdout.decode())
            else:
                storage_alloc_size = 1024
            
            size_val = SnmpWalk.snmpWalkCall(command=size_com) 
            usedsize_val = SnmpWalk.snmpWalkCall(command=usedsize_com)
        
            storage_size = int(size_val.stdout.decode())
            usedstorage_size = int(usedsize_val.stdout.decode())

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
        """funkcja sprawdzajaca obciazenie CPU monitorowanego urzadzenia"""
        
        if device.cpu_opOID == None or device.cpu_opOID.strip() == '':
            return
        try:
            cpu_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + os_oid(device.cpu_opOID) + " -op:" + device.cpu_opOID + " -q"
        
            cpu_val = '0'
            cpu_val = SnmpWalk.snmpWalkCall(command=cpu_com)
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
        """funkcja sprawdzajaca temperature procesora/plyty glownej monitorowanego urzadzenia"""
        
        if device.temperature_opOID == None or device.temperature_opOID.strip() == '':
            return
        try:
            temp_com = "SnmpWalk -v:2 -r:" + device.ipaddress + " -c:" + device.community_name + "  -os:" + os_oid(device.temperature_opOID) + " -op:" + device.temperature_opOID + " -q"
        
            temp_val = '0'
            temp_val = SnmpWalk.snmpWalkCall(command=temp_com)
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
        """funkcja sprawdzajaca ilosc sesji zestawionych do monitorowanego urzadzenia"""

        payload_dest = {'key': firewall.api_key, 
                       'type': 'op', 
                       'cmd': '<show><session><all><filter><destination>' + device.ipaddress + '</destination><count>yes</count></filter></all></session></show>'
                       }
        payload_nat = {'key': firewall.api_key, 
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
        result_nat = 0

        for entry in [ent for ent in nat_entries if ent.xdst.get_text() == device.ipaddress]:
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
    start_time = models.DateTimeField(default=None)
    alert_couse = models.CharField(max_length=50, null=True, default='')

    def getSessionDetails(firewall, device, zone):
        """funkcja pobierajaca parametry sesji zestawionych do monitorowanego urzadzenia"""
        
        payload = {'key': firewall.api_key, 
                   'type': 'op', 
                   'cmd': '<show><session><all><filter><from>' + zone.name + '</from><destination>' + device.ipaddress +  '</destination></filter></all></session></show>'
                    }

        payload_nat = {'key': firewall.api_key, 
                    'type': 'op', 
                    'cmd': '<show><session><all><filter><nat>both</nat></filter></all></session></show>'
                     }

        payload_user = {'key': firewall.api_key, 
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

        for entry in [ent for ent in nat_entries if ent.xdst.get_text() == device.ipaddress and ent.find('from').get_text() == zone]:
            result_nat.append(entry)
        
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
            for us in [u for u in user_entries if s.source.get_text() == u.ip.get_text()]:
                username = us.user.get_text()
            
            session_datetime_tmp = datetime.datetime.strptime(s.find('start-time').get_text(), "%a %b  %d %H:%M:%S %Y") 
            starttime = pytz.utc.localize(session_datetime_tmp)
            couse = ''
            s_zone = Zone.objects.get(name=s.find('from').get_text())
            for alert in alerts:
                c = 0
                if alert.category == 'Storage' and int(s.find('total-byte-count').get_text()) > storage_avg and starttime < alert.timestamp:
                    for app in [a for a in light if a == s.application.get_text()]:
                        c += 1
                    if c == 0:
                        couse = alert.category
                elif alert.category == 'CPU' and starttime < alert.timestamp and starttime > alert.timestamp - datetime.timedelta(minutes=15):
                    for app in [a for a in light if a == s.application.get_text()]:
                        c += 1
                    if c == 0:
                        couse = alert.category
                elif alert.category == 'Session count' and starttime < alert.timestamp and starttime > alert.timestamp - datetime.timedelta(minutes=5):
                    couse = alert.category
                elif alert.category == 'Connection' or alert.category == 'Service' and starttime < alert.timestamp:
                    for app in [a for a in remote_access if(a == s.application.get_text())]:
                        couse = alert.category
                        break
        
            session = Session(device=device, source_zone=s_zone, source_ip=s.source.get_text(), user=username, application=s.application.get_text(), transfer=int(s.find('total-byte-count').get_text()), start_time=starttime, alert_couse=couse)
            session.save()

