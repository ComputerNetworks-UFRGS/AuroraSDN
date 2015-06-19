# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.base_model import BaseModel
from sdn.models.controller import Controller
from sdn.models.port import Port


# Create your models here.
class Host(BaseModel):
    mac_address = models.CharField(max_length=100, db_index=True)
    ipv4_address = models.CharField(max_length=100, db_index=True)
    port = models.ForeignKey(Port, null=True)

    # Foreign key to controller
    controller = models.ForeignKey(Controller)

    def sync(self, host_description):
        # TODO for more interfaces
        if (len(host_description['mac']) > 0):
            self.mac_address = host_description['mac'][0]
        else:
            self.mac_address = 'none'
        if (len(host_description['ipv4']) > 0):
            self.ipv4_address = host_description['ipv4'][0]
        else:
            self.ipv4_address = 'none'
        if (len(host_description['attachmentPoint']) > 0):
            prt_num = host_description['attachmentPoint'][0]['port']
            if (prt_num > 0):
                dpid = host_description['attachmentPoint'][0]['switchDPID']
                self.port = Port.objects.get(port_number=prt_num, switch__dpid=dpid)

                try:
                    # Verify if host exists
                    h = Host.objects.get(mac_address=self.mac_address, controller=self.controller)
                    h.mac_address = self.mac_address
                    h.ipv4_address = self.ipv4_address
                    h.port = self.port
                    h.save()
                except Host.DoesNotExist:
                    self.save()