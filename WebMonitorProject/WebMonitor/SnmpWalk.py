import subprocess

class SnmpWalk:
    
    def snmpWalkCall(command=None, shell=True, capture_output=True):
        """funkcja wywolujaca polecenie systemowe (SnmpWalk)"""

        return subprocess.run(command, shell=shell, capture_output=True)


