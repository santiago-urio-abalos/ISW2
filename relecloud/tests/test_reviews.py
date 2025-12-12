import pytest
from django.db import IntegrityError  
from relecloud.models import Destination, Review
from django.db import models


@pytest.mark.django_db
class TestReviews:
    def setup_method(self):
        self.destination = Destination.objects.create(
            name="Marte",
            description="Planeta rojo"
        )

    def test_create_review_without_destination_fails(self):
        # No se puede crear review sin destino
        with pytest.raises(IntegrityError):
            Review.objects.create(rating=5)

    def test_create_review_without_rating_fails(self):
        # No se puede crear review sin rating
        with pytest.raises(IntegrityError):
            Review.objects.create(destination=self.destination)

    def test_create_valid_review(self):
        # Crear review válido
        review = Review.objects.create(
            destination=self.destination,
            rating=4,
            comment="Muy buena experiencia"
        )
        assert review.rating == 4
        assert review.destination == self.destination
        assert review.comment == "Muy buena experiencia"

    def test_average_rating_calculated_correctly(self):
        # Crear varias reviews
        Review.objects.create(destination=self.destination, rating=5)
        Review.objects.create(destination=self.destination, rating=3)
        Review.objects.create(destination=self.destination, rating=4)

        avg_rating = self.destination.reviews.all().aggregate(models.Avg('rating'))['rating__avg']
        assert avg_rating == 4
# End of file relecloud/tests/test_reviews.py