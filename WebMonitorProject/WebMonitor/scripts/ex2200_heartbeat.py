from background_task import background
from subprocess import check_output
from WebMonitor.models import Device
from django.contrib.auth.models import User

device = Device.objects.get(name="SW_Internal")

#command = "SnmpWalk -r:" + device.ipaddress + " -c: " + device.community_name + "  -os:.1.3.6.1.2.1.2.2.1.8.33 -op:..1.3.6.1.2.1.2.2.1.8.34 -q"
command = 'dir'

@background(schedule=5)
def heartbeat():

    val == 3
    #val = check_output(command, shell=True)
    check_output(command, shell=True)
    if val == 1:
        device.status = 'Up'
    elif val == 2:
        device.status = 'Down'
    else:
        device.status = 'Unknown'
        
    device.save()
    print('TEST')


heartbeat()



