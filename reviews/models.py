# reviews/models.py
from django.db import models
from django.contrib.auth.models import User
from relecloud.models import Destination

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, default=1)


    def __str__(self):
        return f"{self.author} - {self.destination} ({self.rating})"

# Modelo temporal para la tabla antigua
class OldReview(models.Model):
    id = models.BigAutoField(primary_key=True)
    author = models.IntegerField()
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField()
    destination = models.IntegerField()

    class Meta:
        db_table = 'relecloud_review'
        managed = False

    def __str__(self):
        return f"OldReview {self.id} ({self.rating})"