from django.db import models

class Device(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=30)
    producent = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    macaddress = models.CharField(max_length=20)
    ipaddress = models.CharField(max_length=20)

    def __str__(self):
        return self.name