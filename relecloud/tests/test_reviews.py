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

    class Meta:
        app_label = 'tests'
        managed = False

class ReviewTests(SimpleTestCase):  # NOT TransactionTestCase
    def test_create_review(self):
        dest = TempDestination(name="Maldives", description="Beautiful")
        review = TempReview(destination=dest, rating=5, comment="Amazing")

        # No hacemos .save() porque no hay DB
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.destination.name, "Maldives")
