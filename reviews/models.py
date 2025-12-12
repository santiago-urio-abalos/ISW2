<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 96c4a1d8085dc55cd4a61d72cf3c47c6915c8b8c
# reviews/models.py
from django.db import models
from django.contrib.auth.models import User
from relecloud.models import Destination

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    destination = models.ForeignKey(
        Destination, 
        on_delete=models.CASCADE, 
        related_name='destination_reviews'  # Evita conflicto y permite destination.destination_reviews.all()
    )

    def __str__(self):
        return f"{self.author} - {self.destination} ({self.rating})"
<<<<<<< HEAD
=======
# reviews/models.py
from django.db import models
from django.contrib.auth.models import User
from relecloud.models import Destination

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    destination = models.ForeignKey(
        Destination, 
        on_delete=models.CASCADE, 
        related_name='destination_reviews'  # Evita conflicto y permite destination.destination_reviews.all()
    )

    def __str__(self):
        return f"{self.author} - {self.destination} ({self.rating})"
>>>>>>> 089ae2fcb446be135d0a687d33e6a8eeefc8a59d
=======
>>>>>>> 96c4a1d8085dc55cd4a61d72cf3c47c6915c8b8c
