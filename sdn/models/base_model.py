import logging
from django.db import models


class BaseModel(models.Model):
    class Meta:
        # Makes django recognize model in split modules
        app_label = 'sdn'
        # Turns this into an abstract model (does not create table for it)
        abstract = True

    # Default exception for models in manager
    class ModelException(Exception):
        # Get an instance of a logger
        logger = logging.getLogger(__name__)

        def __init__(self, msg):
            self.msg = msg
            self.logger.warning(msg)

        def __str__(self):
            return repr(self.msg)
