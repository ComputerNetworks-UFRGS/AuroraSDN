from django.db import models
from sdn.models.base_model import BaseModel
from sdn.models.controller import Controller


# Create your models here.
class Configuration(BaseModel):
    # Polling Interval
    polling_interval = models.IntegerField()

    # Chart Update Interval
    chart_update_interval = models.IntegerField()

    # Foreign key to controller
    controller = models.ForeignKey(Controller)

    def sync(self, polling_interval, chart_update_interval):
        self.polling_interval = polling_interval
        self.chart_update_interval = chart_update_interval
        self.save()