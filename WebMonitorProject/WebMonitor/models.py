from django.db import models
import subprocess
import time
import random



class Device(models.Model):
    name = models.CharField(max_length=50)
    community_name = models.CharField(max_length=50)
    type = models.CharField(max_length=30)
    producent = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    macaddress = models.CharField(max_length=20)
    ipaddress = models.GenericIPAddressField()
    sessions = models.PositiveIntegerField()
    status = models.NullBooleanField()

    def __str__(self):
        return self.name

    def checkConnection(device, oidfirst, oidlast):
        time.sleep(12)
        command = "SnmpWalk -r:" + device.ipaddress + " -c: " + device.community_name + "  -os:" + oidfirst + " -op:" + oidlast + " -q"
        val = 3
        val = subprocess.run(command, shell=True, stderr=subprocess.DEVNULL)
        if val == 1:
            device.status = True
        elif val == 2:
            device.status = False
        else:
            device.status = None
        device.save()

    #def test2(dev):
    #    list = [True, False, None]
    #    while(True):
    #        r = random.choice(list)
    #        dev.status = r
    #        dev.save()
    #        time.sleep(4.0)

    def test3(dev):
        dev.status = False
        dev.save()

    def test4(dev):
        time.sleep(5)
        dev.status = True
        dev.save()
            