# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.switch import Switch
from sdn.models.port import Port
from sdn.models.openflow_flowtable1_0 import OpenflowFlowTable1_0
import logging
import time

# Get an instance of a logger
logger = logging.getLogger(__name__)

SWITCH_CHOICE = (
    ('ofd', 'OPENFLOW_DEDICATED'),
    ('ofe', 'OPENFLOW_ENABLED')
)


# Create your models here.
class OpenflowSwitch1_0(Switch):
    # Switch type
    switch_type = models.CharField(max_length=3, choices=SWITCH_CHOICE)

    def sync(self, switch_description, table_description, header_description, port_description, sync_time, debug_time):
        # TODO: Identify which are switch types)
        self.switch_type = 'ofe'
        self.buffers = switch_description['buffers']
        self.software = switch_description['description']['software']
        self.hardware = switch_description['description']['hardware']
        self.manufacturer = switch_description['description']['manufacturer']
        self.serialNum = switch_description['description']['serialNum']
        self.datapath = switch_description['description']['datapath']
        self.capabilities = switch_description['capabilities']
        self.inet_address = switch_description['inetAddress']
        self.connected_since = switch_description['connectedSince']
        self.dpid = switch_description['dpid']

        # Create an openflow table
        oft = OpenflowFlowTable1_0()
        try:
            # Verify if this openflowswitch already exists
            ofs = OpenflowSwitch1_0.objects.get(controller=self.controller, dpid=self.dpid)
            ofs.buffers = self.buffers
            ofs.software = self.software
            ofs.hardware = self.hardware
            ofs.manufacturer = self.manufacturer
            ofs.serialNum = self.serialNum
            ofs.datapath = self.datapath
            ofs.capabilities = self.capabilities
            ofs.inet_address = self.inet_address
            ofs.connected_since = self.connected_since
            ofs.save()
            # Assign openflow table to openflow switch
            oft.openflow_switch1_0 = ofs
        except OpenflowSwitch1_0.DoesNotExist:
            self.save()
            # Assign openflow table to openflow switch
            oft.openflow_switch1_0 = self

        for p in switch_description['ports']:
            port = Port()
            port.switch = self
            pn = None
            for pn in port_description:
                if pn['portNumber'] == p['portNumber']:
                    break
            port.sync(p, pn)
        # Call openflow table sync method
        oft.sync(table_description, header_description, sync_time)

        logger.debug("Each switch " + str(int(time.time()) - debug_time) + " DPID " + str(self.dpid))