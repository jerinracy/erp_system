from django.db import models
from core.models.base import TimeStampedModel
# Create your models here.


class Tenant(TimeStampedModel):
    name = models.CharField(max_length=255)

    owner_name = models.CharField(max_length=255, blank=True, null=True)
    owner_email = models.EmailField(blank=True, null=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20,
                              choices=[('pending', 'Pending'),
                                       ('active', 'Active'),
                                       ('inactive', 'Inactive')],
                              default='pending'
                              )

    def __str__(self):
        return self.name
