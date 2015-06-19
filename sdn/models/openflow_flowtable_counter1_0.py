# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.base_model import BaseModel


# Create your models here.
class OpenflowFlowTableCounter1_0(BaseModel):

    # Per Table
    active_entries = models.IntegerField(null=True)
    packet_lookups = models.BigIntegerField(null=True)
    packet_matches = models.BigIntegerField(null=True)

    # Foreign key to a openflow table 1_0
    openflow_table1_0 = models.ForeignKey('OpenflowFlowTable1_0')

    def sync(self, table_description):
        self.active_entries = table_description['activeCount']
        self.packet_lookups = table_description['lookupCount']
        self.packet_matches = table_description['matchedCount']
        try:
            oftc = OpenflowFlowTableCounter1_0.objects.get(openflow_table1_0=self.openflow_table1_0)
            oftc.active_entries = self.active_entries
            oftc.packet_lookups = self.packet_lookups
            oftc.packet_matches = self.packet_matches
            oftc.save()
        except OpenflowFlowTableCounter1_0.DoesNotExist:
            self.save()