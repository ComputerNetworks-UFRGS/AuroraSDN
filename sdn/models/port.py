# -*- coding: utf-8 -*-
from django.db import models
from sdn.models.base_model import BaseModel
from sdn.models.switch import Switch
from sdn.models.openflow_port_counter1_0 import OpenflowPortCounter1_0


# Create your models here.
class Port(BaseModel):
    port_number = models.IntegerField()
    hardware_address = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    config = models.IntegerField()
    state = models.IntegerField()
    current_features = models.IntegerField()
    advertised_features = models.IntegerField()
    supported_features = models.IntegerField()
    peer_features = models.IntegerField()

    # Foreign key to switch
    switch = models.ForeignKey(Switch)

    def sync(self, port_description, port_counters):
        self.port_number = port_description['portNumber']
        self.hardware_address = port_description['hardwareAddress']
        self.name = port_description['name']
        self.config = port_description['config']
        self.state = port_description['state']
        self.current_features = port_description['currentFeatures']
        self.advertised_features = port_description['advertisedFeatures']
        self.supported_features = port_description['supportedFeatures']
        self.peer_features = port_description['peerFeatures']

        # Create a port counter
        ofpc = OpenflowPortCounter1_0()
        try:
            # Verify if this port already exists
            p = Port.objects.get(port_number=self.port_number, hardware_address=self.hardware_address, name=self.name)
            p.config = self.config
            p.state - self.state
            p.currentFeatures = self.current_features
            p.advertised_features = self.advertised_features
            p.supported_features = self.supported_features
            p.peer_features = self.peer_features
            p.save()
            # Assign port to a port counter
            ofpc.port = p
        except Port.DoesNotExist:
            self.save()
            # Assign port to a port counter
            ofpc.port = self
        # Call port counter sync method
        ofpc.sync(port_counters)