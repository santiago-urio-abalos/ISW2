from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail
from django.db.models import Count, Avg
from django.utils import timezone
from .models import Cruise, InfoRequest, Destination, Review

# --- Tests para el formulario info_request ---
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class InfoRequestFormTests(TestCase):
    # Cambio insignificante para forzar PR en la nueva rama
    def setUp(self):
        self.client = Client()
        self.cruise = Cruise.objects.create(
            name="Test Cruise",
            description="Test description",
            departure_date=timezone.now().date()
        )
        self.url = reverse('info_request')

    def test_info_request_success(self):
        data = {
            'name': 'Miguel',
            'email': 'miguel@example.com',
            'cruise': self.cruise.id,
            'notes': 'Quiero información',
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, '¡Solicitud enviada correctamente!')
        self.assertEqual(InfoRequest.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Miguel', mail.outbox[0].body)
        self.assertIn('Test Cruise', mail.outbox[0].body)

    def test_info_request_duplicate(self):
        InfoRequest.objects.create(
            name='Miguel',
            email='miguel@example.com',
            cruise=self.cruise,
            notes='Primera solicitud',
        )
        data = {
            'name': 'Miguel',
            'email': 'miguel@example.com',
            'cruise': self.cruise.id,
            'notes': 'Segunda solicitud',
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, 'Ya has enviado una solicitud para este crucero')
        self.assertEqual(InfoRequest.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

# --- Tests para popularidad de destinos y reviews ---
class DestinationPopularityTest(TestCase):
    """
    Tests para el cálculo de popularidad de destinos basado en reviews
    """
    def setUp(self):
        self.dest1 = Destination.objects.create(
            name="París",
            description="La ciudad de la luz"
        )
        self.dest2 = Destination.objects.create(
            name="Roma",
            description="La ciudad eterna"
        )
        self.dest3 = Destination.objects.create(
            name="Londres",
            description="Capital del Reino Unido"
        )

    def test_destination_with_reviews_has_correct_count(self):
        Review.objects.create(destination=self.dest1, rating=5, comment="Excelente")
        Review.objects.create(destination=self.dest1, rating=4, comment="Muy bueno")
        Review.objects.create(destination=self.dest1, rating=5, comment="Increíble")
        dest_annotated = Destination.objects.annotate(
            review_count=Count('reviews')
        ).get(pk=self.dest1.pk)
        self.assertEqual(dest_annotated.review_count, 3)

    def test_destination_without_reviews_has_zero_count(self):
        dest_annotated = Destination.objects.annotate(
            review_count=Count('reviews')
        ).get(pk=self.dest3.pk)
        self.assertEqual(dest_annotated.review_count, 0)

    def test_average_rating_calculation(self):
        Review.objects.create(destination=self.dest1, rating=5)
        Review.objects.create(destination=self.dest1, rating=4)
        Review.objects.create(destination=self.dest1, rating=3)
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).get(pk=self.dest1.pk)
        self.assertEqual(dest_annotated.avg_rating, 4.0)

    def test_destination_without_reviews_has_null_average(self):
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).get(pk=self.dest3.pk)
        self.assertIsNone(dest_annotated.avg_rating)

    def test_destinations_ordered_by_popularity(self):
        Review.objects.create(destination=self.dest1, rating=5)
        Review.objects.create(destination=self.dest1, rating=4)
        Review.objects.create(destination=self.dest1, rating=5)
        Review.objects.create(destination=self.dest2, rating=5)
        destinations = Destination.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')
        self.assertEqual(destinations[0].name, "París")
        self.assertEqual(destinations[1].name, "Roma")
        self.assertEqual(destinations[2].name, "Londres")

    def test_popularity_with_same_count_different_rating(self):
        Review.objects.create(destination=self.dest1, rating=5)
        Review.objects.create(destination=self.dest1, rating=4)
        Review.objects.create(destination=self.dest2, rating=3)
        Review.objects.create(destination=self.dest2, rating=3)
        destinations = Destination.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')
        self.assertEqual(destinations[0].name, "París")
        self.assertEqual(destinations[1].name, "Roma")

    def test_review_model_creation(self):
        review = Review.objects.create(
            destination=self.dest1,
            rating=5,
            comment="Excelente destino"
        )
        self.assertEqual(review.destination, self.dest1)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excelente destino")
        self.assertIsNotNone(review.created_at)

    def test_review_str_method(self):
        review = Review.objects.create(
            destination=self.dest1,
            rating=4
        )
        expected_str = f'Review for {self.dest1.name} - 4/5'
        self.assertEqual(str(review), expected_str)

    def test_popularity_calculation_performance(self):
        import time
        for i in range(10):
            dest = Destination.objects.create(
                name=f"Destino {i}",
                description=f"Descripción {i}"
            )
            for j in range(5):
                Review.objects.create(destination=dest, rating=(j % 5) + 1)
        start_time = time.time()
        destinations = Destination.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')
        list(destinations)
        end_time = time.time()
        execution_time = end_time - start_time
        self.assertLess(execution_time, 1.0)

# --- Tests para verificar la información de popularidad en el template ---
class DestinationTemplateTest(TestCase):
    def setUp(self):
        self.dest_with_reviews = Destination.objects.create(
            name="Barcelona",
            description="Ciudad mediterránea"
        )
        self.dest_without_reviews = Destination.objects.create(
            name="Madrid",
            description="Capital de España"
        )
        Review.objects.create(destination=self.dest_with_reviews, rating=5, comment="Excelente")
        Review.objects.create(destination=self.dest_with_reviews, rating=4, comment="Muy bueno")
        Review.objects.create(destination=self.dest_with_reviews, rating=5, comment="Increíble")

    def test_template_shows_review_count_for_destination_with_reviews(self):
        response = self.client.get(reverse('destinations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3 reviews')
        self.assertContains(response, 'Barcelona')

    def test_template_shows_average_rating_for_destination_with_reviews(self):
        response = self.client.get(reverse('destinations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '4.7/5')

    def test_template_shows_no_reviews_message_for_destination_without_reviews(self):
        response = self.client.get(reverse('destinations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sin valoraciones')
        self.assertContains(response, 'Madrid')

    def test_template_displays_all_destinations(self):
        response = self.client.get(reverse('destinations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Barcelona')
        self.assertContains(response, 'Madrid')

    def test_destinations_ordered_correctly_in_template(self):
        response = self.client.get(reverse('destinations'))
        content = response.content.decode('utf-8')
        barcelona_pos = content.find('Barcelona')
        madrid_pos = content.find('Madrid')
        self.assertLess(barcelona_pos, madrid_pos, "Destino con reviews debe aparecer antes que destino sin reviews")

    def test_plural_handling_for_single_review(self):
        dest_single = Destination.objects.create(
            name="Sevilla",
            description="Ciudad andaluza"
        )
        Review.objects.create(destination=dest_single, rating=5)
        response = self.client.get(reverse('destinations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1 review')
        self.assertNotContains(response, '1 reviews')
