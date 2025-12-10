@pytest.mark.django_db
class TestCruiseReviews:

    def test_reviews_attached_to_cruise(self):
        user = User.objects.create_user(username="u", password="1234")
        dest = Destination.objects.create(name="Islas", description="abc")
        cruise = Cruise.objects.create(name="Island Tour", price=900)
        cruise.destinations.add(dest)

        Review.objects.create(
            author=user,
            destination=dest,
            rating=5,
            comment="Excelente"
        )

        # Solo debe recoger las reviews del destino del crucero
        reviews = Review.objects.filter(destination__in=cruise.destinations.all())
        assert reviews.count() == 1
