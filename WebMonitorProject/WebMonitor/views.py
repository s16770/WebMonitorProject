from django.shortcuts import render
from django.http import HttpResponse

devices = [
    {
        'Name': 'SW_Internal',
        'Type': 'Switch',
        'Vendor': 'Juniper',
        'Model': 'EX2200'
    },
    {
        'Name': 'ADServer',
        'Type': 'Server',
        'Vendor': 'Microsoft',
        'Model': 'Windows Server 2019'
    } 
]

def dashboard(request):
    context = {
        'devices': devices
    }
    return render(request, 'WebMonitor/dashboard.html', context)


