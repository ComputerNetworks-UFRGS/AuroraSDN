from django.db import models
from sdn.models.base_model import BaseModel
from sdn.models.controller import Controller


# Create your models here.
class Switch(BaseModel):
    # Buffers
    buffers = models.IntegerField()

    # Description
    software = models.CharField(max_length=100)
    hardware = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    serial_num = models.CharField(max_length=100)
    datapath = models.CharField(max_length=100)

    # Capabilities
    capabilities = models.IntegerField()

    # Inet Address
    inet_address = models.CharField(max_length=100)

    # Connected Since
    connected_since = models.BigIntegerField()

    # DPID
    dpid = models.CharField(max_length=100, db_index=True)

    # Foreign key to controller
    controller = models.ForeignKey(Controller)