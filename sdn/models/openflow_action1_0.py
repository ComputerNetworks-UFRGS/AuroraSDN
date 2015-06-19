# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.base_model import BaseModel

FORWARD_CHOICE = (
    (0, 'ALL'),
    (1, 'CONTROLLER'),
    (2, 'LOCAL'),
    (3, 'TABLE'),
    (4, 'IN_PORT'),
    (5, 'NORMAL'),
    (6, 'FLOOD')
)


# Create your models here.
class OpenflowAction1_0(BaseModel):
    # Fields for openflow switch specification version 1.0
    # Forward
    # Required Actions: ALL, CONTROLLER, LOCAL, TABLE, IN_PORT, NORMAL, FLOOD
    # Openflow-enabled: NORMAL, FLOOD
    forward = models.CharField(max_length=1, choices=FORWARD_CHOICE)

    # Required to all Openflow switches
    # Drop a flow-entry
    drop = models.CharField(max_length=100)

    # Foreign key to a openflow header 1_0
    openflow_header1_0 = models.ForeignKey('OpenflowHeader1_0')

    # Only for Openflow-enabled switches
    # Enqueue TODO

    # Modify-Field TODO