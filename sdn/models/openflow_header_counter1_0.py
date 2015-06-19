# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.base_model import BaseModel


# Create your models here.
class OpenflowHeaderCounter1_0(BaseModel):

    # Per Flow
    received_packets = models.BigIntegerField(null=True)
    received_bytes = models.BigIntegerField(null=True)
    duration_seconds = models.BigIntegerField(null=True)
    duration_nanoseconds = models.BigIntegerField(null=True)

    # Foreign key to a openflow header 1_0
    openflow_header1_0 = models.ForeignKey('OpenflowHeader1_0')

    def sync(self, header_description, sync_time):
        self.received_packets = header_description['packetCount']
        self.received_bytes = header_description['byteCount']
        self.duration_seconds = header_description['durationSeconds']
        self.duration_nanoseconds = header_description['durationNanoseconds']
        try:
            offc = OpenflowHeaderCounter1_0.objects.get(openflow_header1_0=self.openflow_header1_0)
            if int(offc.received_packets) == int(self.received_packets):
                offc.openflow_header1_0.flow_status = False
                offc.openflow_header1_0.save()
            else:
                offc.openflow_header1_0.flow_status = True
                offc.openflow_header1_0.last_synchronization_time = sync_time
                offc.openflow_header1_0.save()
            offc.received_packets = self.received_packets
            offc.received_bytes = self.received_bytes
            offc.duration_seconds = self.duration_seconds
            offc.duration_nanoseconds = self.duration_nanoseconds
            offc.save()
        except OpenflowHeaderCounter1_0.DoesNotExist:
            self.save()