# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.base_model import BaseModel
from sdn.models.openflow_header_counter1_0 import OpenflowHeaderCounter1_0


# Create your models here.
class OpenflowHeader1_0(BaseModel):
    # Fields for openflow switch specification version 1.0
    ingress_port = models.IntegerField()
    ethernet_source_address = models.CharField(max_length=100, db_index=True)
    ethernet_destination_address = models.CharField(max_length=100, db_index=True)
    ethernet_type = models.CharField(max_length=100, db_index=True)
    vlan_id = models.IntegerField()
    vlan_priority = models.IntegerField()
    ip_source_address = models.CharField(max_length=100, db_index=True)
    ip_destination_address = models.CharField(max_length=100, db_index=True)
    ip_protocol = models.IntegerField()
    ip_tos_bits = models.IntegerField()

    # If ICMP transport_source_port = ICMP Type
    transport_source_port = models.IntegerField()

    # If ICMP transport_destination_port = ICMP Code
    transport_destination_port = models.IntegerField()

    # Flow Status = active or idle (true or false)
    flow_status = models.BooleanField(default=True)

    # Sync time to controll new and old flows
    # TODO change timestamp field type
    last_synchronization_time = models.CharField(max_length=100)

    # Foreign key to openflow table
    openflow_table1_0 = models.ForeignKey('OpenflowFlowTable1_0')

    def sync(self, header_description, sync_time):
        self.ingress_port = header_description['match']['inputPort']
        self.ethernet_source_address = header_description['match']['dataLayerSource']
        self.ethernet_destination_address = header_description['match']['dataLayerDestination']
        self.ethernet_type = header_description['match']['dataLayerType']
        self.vlan_id = header_description['match']['dataLayerVirtualLan']
        self.vlan_priority = header_description['match']['dataLayerVirtualLanPriorityCodePoint']
        self.ip_source_address = header_description['match']['networkSource']
        self.ip_destination_address = header_description['match']['networkDestination']
        self.ip_protocol = header_description['match']['networkProtocol']
        self.ip_tos_bits = header_description['match']['networkTypeOfService']
        self.transport_source_port = header_description['match']['transportSource']
        self.transport_destination_port = header_description['match']['transportDestination']
        self.last_synchronization_time = sync_time

        offc = OpenflowHeaderCounter1_0()
        try:
            ofh = OpenflowHeader1_0.objects.get(ingress_port=self.ingress_port,
                ethernet_source_address=self.ethernet_source_address,
                ethernet_destination_address=self.ethernet_destination_address,
                ethernet_type=self.ethernet_type,
                vlan_id=self.vlan_id,
                vlan_priority=self.vlan_priority,
                ip_source_address=self.ip_source_address,
                ip_destination_address=self.ip_destination_address,
                ip_protocol=self.ip_protocol,
                ip_tos_bits=self.ip_tos_bits,
                transport_source_port=self.transport_source_port,
                transport_destination_port=self.transport_destination_port)
            ofh.last_synchronization_time = self.last_synchronization_time = sync_time
            ofh.save()
            offc.openflow_header1_0 = ofh
        except OpenflowHeader1_0.DoesNotExist:
            self.save()
            offc.openflow_header1_0 = self

        # Adding counters for headers
        offc.sync(header_description, sync_time)

