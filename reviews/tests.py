<<<<<<< HEAD
from django.test import TestCase

# Create your tests here.
=======
from django.test import TestCase
from relecloud.models import Destination
from reviews.models import Review
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.urls import reverse


class DestinationPopularityWithReviewsAppTest(TestCase):
    """
    Tests para verificar que la popularidad funciona con reviews.Review
    """
    
    def setUp(self):
        """Configuración inicial: crear usuario y destinos"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
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
    
    def test_review_model_uses_correct_related_name(self):
        """Test: Review usa related_name='destination_reviews'"""
        Review.objects.create(
            destination=self.dest1,
            author=self.user,
            rating=5,
            comment="Excelente"
        )
        
        # Verificar que se puede acceder via related_name
        self.assertEqual(self.dest1.destination_reviews.count(), 1)
    
    def test_destination_with_reviews_has_correct_count(self):
        """Test: conteo correcto de reviews usando destination_reviews"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5)
        Review.objects.create(destination=self.dest1, author=self.user, rating=4)
        Review.objects.create(destination=self.dest1, author=self.user, rating=5)
        
        dest_annotated = Destination.objects.annotate(
            review_count=Count('destination_reviews')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.review_count, 3)
    
    def test_average_rating_calculation(self):
        """Test: cálculo correcto de rating promedio"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5)
        Review.objects.create(destination=self.dest1, author=self.user, rating=4)
        Review.objects.create(destination=self.dest1, author=self.user, rating=3)
        
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('destination_reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.avg_rating, 4.0)
    
    def test_destinations_ordered_by_popularity(self):
        """Test: ordenamiento correcto por popularidad"""
        # París: 3 reviews
        Review.objects.create(destination=self.dest1, author=self.user, rating=5)
        Review.objects.create(destination=self.dest1, author=self.user, rating=4)
        Review.objects.create(destination=self.dest1, author=self.user, rating=5)
        
        # Roma: 1 review
        Review.objects.create(destination=self.dest2, author=self.user, rating=5)
        
        # Londres: 0 reviews
        
        destinations = Destination.objects.annotate(
            review_count=Count('destination_reviews'),
            avg_rating=Avg('destination_reviews__rating')
        ).order_by('-review_count', '-avg_rating')
        
        self.assertEqual(destinations[0].name, "París")
        self.assertEqual(destinations[1].name, "Roma")
        self.assertEqual(destinations[2].name, "Londres")
    
    def test_template_shows_review_info(self):
        """Test: template muestra información de reviews"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5)
        Review.objects.create(destination=self.dest1, author=self.user, rating=4)
        
        response = self.client.get(reverse('destinations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2 reviews')
        self.assertContains(response, 'París')
    
    def test_template_shows_no_reviews_message(self):
        """Test: template muestra 'Sin valoraciones' cuando no hay reviews"""
        response = self.client.get(reverse('destinations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sin valoraciones')
>>>>>>> 089ae2fcb446be135d0a687d33e6a8eeefc8a59d
