import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from relecloud.models import Destination, Cruise, Review

@pytest.mark.django_db
class TestReviews:

    def setup_method(self):
        # Usuario comprador
        self.user = User.objects.create_user(username="testuser", password="1234")

        # Destino
        self.destination = Destination.objects.create(
            name="Caribe",
            description="Playas",
        )

        # Crucero que incluye el destino
        self.cruise = Cruise.objects.create(
            name="Caribbean Adventure",
            price=1000
        )
        self.cruise.destinations.add(self.destination)

        # Simulación de compra: puedes tener un modelo Purchase o similar.
        # Si no lo tienes, asumimos que Cruise tiene una relación con usuarios,
        # por ejemplo: cruise.buyers.add(user)
        self.cruise.buyers.add(self.user)

    def test_only_logged_users_can_access_review_form(self, client):
        url = reverse("add_review", args=[self.destination.id])
        response = client.get(url)

        # Redirige al login
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_user_without_purchase_cannot_post_review(self, client):
        other_user = User.objects.create_user(username="other", password="1234")

        client.login(username="other", password="1234")

        url = reverse("add_review", args=[self.destination.id])
        response = client.post(url, {
            "rating": 5,
            "comment": "Muy bien"
        })

        assert response.status_code == 403  # Prohibido

    def test_user_with_purchase_can_post_review(self, client):
        client.login(username="testuser", password="1234")

        url = reverse("add_review", args=[self.destination.id])
        response = client.post(url, {
            "rating": 4,
            "comment": "Muy bueno"
        })

        assert response.status_code == 302  # Redirección correcta
        assert Review.objects.count() == 1

        review = Review.objects.first()
        assert review.rating == 4
        assert review.destination == self.destination
        assert review.author == self.user

    def test_average_rating_calculated_correctly(self, client):
        Review.objects.create(destination=self.destination, author=self.user, rating=4, comment="Bien")
        Review.objects.create(destination=self.destination, author=self.user, rating=2, comment="Mal")

        url = reverse("destination_detail", args=[self.destination.id])
        response = client.get(url)

        # La vista debe incluir en el contexto el average_rating
        avg = response.context["average_rating"]

        assert avg == 3  # (4 + 2) / 2

    def test_destination_sorted_by_popularity(self, client):
        # Creamos un segundo destino
        d2 = Destination.objects.create(name="Mediterráneo", description="Bonito")

        # Popularidad:
        # Caribe → 2 reviews
        # Med → 1 review
        Review.objects.create(destination=self.destination, author=self.user, rating=5)
        Review.objects.create(destination=self.destination, author=self.user, rating=4)
        Review.objects.create(destination=d2, author=self.user, rating=3)

        url = reverse("destination_list")
        response = client.get(url)

        destinations = response.context["destinations"]

        # Debe estar ordenado: Caribe primero (2), Mediterráneo (1)
        assert list(destinations) == [self.destination, d2]
