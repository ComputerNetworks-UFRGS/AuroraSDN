from django.db import models
from sdn.models.base_model import BaseModel

CONTROLLER_CHOICE = (
    ('b', 'Beacon'),
    ('f', 'Floodlight'),
    ('j', 'Jaxon'),
    ('n', 'NOX'),
    ('p', 'POX')
)


# Create your models here.
class Controller(BaseModel):
    # Ip address
    ip_address = models.CharField(max_length=50)

    # Port
    listen_port = models.CharField(max_length=10)

    # Name
    name = models.CharField(max_length=50)

    # Description
    description = models.CharField(max_length=100)

    # Controller type
    controller_type = models.CharField(max_length=1, choices=CONTROLLER_CHOICE)

    def __unicode__(self):
        return self.name + " - " + self.description