# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.base_model import BaseModel


# Create your models here.
class OpenflowPortCounter1_0(BaseModel):
    # Per Port
    received_packets = models.BigIntegerField(null=True)
    transmitted_packets = models.BigIntegerField(null=True)
    received_bytes = models.BigIntegerField(null=True)
    transmitted_bytes = models.BigIntegerField(null=True)
    received_drops = models.BigIntegerField(null=True)
    transmit_drops = models.BigIntegerField(null=True)
    receive_errors = models.BigIntegerField(null=True)
    transmit_errors = models.BigIntegerField(null=True)
    receive_frame_alignment_errors = models.BigIntegerField(null=True)
    receive_overrun_erros = models.BigIntegerField(null=True)
    receive_crc_errors = models.BigIntegerField(null=True)
    collisions = models.BigIntegerField(null=True)

    # Foreign key to a port
    port = models.ForeignKey('Port')

    def sync(self, port_counters):
        self.received_packets = port_counters['receivePackets']
        self.transmitted_packets = port_counters['transmitPackets']
        self.received_bytes = port_counters['receiveBytes']
        self.transmitted_bytes = port_counters['transmitBytes']
        self.received_drops = port_counters['receiveDropped']
        self.transmit_drops = port_counters['transmitDropped']
        self.receive_errors = port_counters['receiveErrors']
        self.transmit_errors = port_counters['transmitErrors']
        self.receive_frame_alignment_errors = port_counters['receiveFrameErrors']
        self.receive_overrun_erros = port_counters['receiveOverrunErrors']
        self.receive_crc_errors = port_counters['receiveCRCErrors']
        self.collisions = port_counters['collisions']
        try:
            opc = OpenflowPortCounter1_0.objects.get(port=self.port)
            opc.received_packets = self.received_packets
            opc.transmitted_packets = self.transmitted_packets
            opc.received_bytes = self.received_bytes
            opc.transmitted_bytes = self.transmitted_bytes
            opc.received_drops = self.received_drops
            opc.transmit_drops = self.transmit_drops
            opc.receive_errors = self.receive_errors
            opc.transmit_errors = self.transmit_errors
            opc.receive_frame_alignment_errors = self.receive_frame_alignment_errors
            opc.receive_overrun_erros = self.receive_overrun_erros
            opc.receive_crc_errors = self.receive_crc_errors
            opc.collisions = self.collisions
            opc.save()
        except OpenflowPortCounter1_0.DoesNotExist:
            self.save()