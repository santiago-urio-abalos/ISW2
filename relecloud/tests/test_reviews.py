# relecloud/tests/test_reviews.py
from django.test import SimpleTestCase
from django.db import models

class TempDestination(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=2000)

    class Meta:
        app_label = 'tests'
        managed = False  # No crea tabla en DB

class TempReview(models.Model):
    destination = models.ForeignKey(
        TempDestination,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField()
    comment = models.TextField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Crucero que incluye el destino
    self.cruise = Cruise.objects.create(
        name="Caribbean Adventure",
        price=1000
    )
    self.cruise.destinations.add(self.destination)
    self.cruise.buyers.add(self.user)

    # No hacemos .save() porque no hay DB
    self.assertEqual(review.rating, 5)
    self.assertEqual(review.destination.name, "Maldives")
