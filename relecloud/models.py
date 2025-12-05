from django.db import models
from django.urls import reverse

# Create your models here.
class Destination(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        null=False,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('destination_detail', kwargs={'pk': self.pk})

class Cruise(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        null=False,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False,
        default='No description available.',
    )
    destinations = models.ManyToManyField(
        Destination,
        related_name='cruises'
    )
    departure_date = models.DateField()
    def __str__(self):
        return self.name

class InfoRequest(models.Model):
    name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    email = models.EmailField()
    notes = models.TextField(
        max_length=2000,
        null=True,
        blank=True,
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)