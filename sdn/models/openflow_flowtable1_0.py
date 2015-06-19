# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.base_model import BaseModel
from sdn.models.openflow_flowtable_counter1_0 import OpenflowFlowTableCounter1_0
from sdn.models.openflow_header1_0 import OpenflowHeader1_0


# Create your models here.
class OpenflowFlowTable1_0(BaseModel):
    # Foreign key to a openflow switch
    table_id = models.IntegerField()
    openflow_switch1_0 = models.ForeignKey('OpenflowSwitch1_0')

    def sync(self, table_description, header_description, sync_time):
        # The openflow switch 1.0 has one openflow table
        self.table_id = table_description['tableId']
        oftc = OpenflowFlowTableCounter1_0()
        oftable = OpenflowFlowTable1_0()
        try:
            oft = OpenflowFlowTable1_0.objects.get(table_id=self.table_id, openflow_switch1_0=self.openflow_switch1_0)
            oft.table_id = self.table_id
            oft.openflow_switch1_0 = self.openflow_switch1_0
            oft.save()
            oftable = oft
            oftc.openflow_table1_0 = oft
        except OpenflowFlowTable1_0.DoesNotExist:
            self.save()
            oftable = self
            oftc.openflow_table1_0 = self

        # TODO: put table counter in sync method
        # Adding the table counters
        oftc.sync(table_description)

        # Adding the flow headers
        for header in header_description:
            ofh = OpenflowHeader1_0()
            ofh.openflow_table1_0 = oftable
            ofh.sync(header, sync_time)