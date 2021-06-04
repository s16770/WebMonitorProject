import subprocess

class SnmpWalk:
    
    def snmpWalkCall(command=None, shell=True, capture_output=True):
        return subprocess.run(command, shell=shell, capture_output=True)


