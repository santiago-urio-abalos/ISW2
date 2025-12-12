from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

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
    image = models.ImageField(
        upload_to='destinations/',
        null=True,
        blank=True,
        help_text='Imagen del destino'
    )
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('destination_detail', kwargs={'pk': self.pk})

class Review(models.Model):
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        help_text='Rating from 1 to 5'
    )
    comment = models.TextField(
        max_length=500,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Review for {self.destination.name} - {self.rating}/5'

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


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey('Destination', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} compró {self.destination.name}"