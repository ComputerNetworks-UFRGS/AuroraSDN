# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.base_model import BaseModel
from sdn.models.port import Port
from sdn.models.openflow_switch1_0 import OpenflowSwitch1_0


# Create your models here.
class Link(BaseModel):
    src_port = models.ForeignKey(
        Port,
        verbose_name="destination port",
        related_name='dst_port'
    )
    src_port = models.ForeignKey(
        Port,
        verbose_name="source port",
        related_name='src_port'
    )

    dst_port = models.ForeignKey(Port)
    link_type = models.CharField(max_length=100)
    direction = models.CharField(max_length=100)

    def sync(self, link_description, op_switches):

        for op_switch in op_switches:
            sw_dpid = op_switch['dpid']
            ofsw = OpenflowSwitch1_0.objects.get(dpid=sw_dpid)

            if sw_dpid == link_description['src-switch']:
                for p in ofsw.port_set.all():
                    if p.port_number == link_description['src-port']:
                        self.src_port = p
            else:
                if sw_dpid == link_description['dst-switch']:
                    for p in ofsw.port_set.all():
                        if p.port_number == link_description['dst-port']:
                            self.dst_port = p

        try:
            l = Link.objects.get(src_port=self.src_port, dst_port=self.dst_port)
            l.src_port = self.src_port
            l.dst_port = self.dst_port
            l.link_type = link_description['type']
            l.direction = link_description['direction']
            l.save()
        except Link.DoesNotExist:
            self.link_type = link_description['type']
            self.direction = link_description['direction']
            self.save()