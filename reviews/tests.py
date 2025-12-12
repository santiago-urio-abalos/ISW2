from django.test import TestCase, Client
from relecloud.models import Destination
from reviews.models import Review
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.urls import reverse


class ReviewModelTest(TestCase):
    """Tests del modelo Review"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.destination = Destination.objects.create(
            name="París",
            description="La ciudad de la luz"
        )
    
    def test_review_creation(self):
        """Test: crear una review correctamente"""
        review = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment="Excelente destino"
        )
        
        self.assertEqual(review.author, self.user)
        self.assertEqual(review.destination, self.destination)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excelente destino")
        self.assertIsNotNone(review.created_at)
    
    def test_review_string_representation(self):
        """Test: representación en string de Review"""
        review = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=4,
            comment="Muy bueno"
        )
        
        expected = f"{self.user} - {self.destination} (4)"
        self.assertEqual(str(review), expected)
    
    def test_review_related_name(self):
        """Test: related_name='destination_reviews' funciona correctamente"""
        Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment="Perfecto"
        )
        
        self.assertEqual(self.destination.destination_reviews.count(), 1)
    
    def test_multiple_reviews_same_destination(self):
        """Test: múltiples reviews para el mismo destino"""
        user2 = User.objects.create_user(username='user2', password='pass2')
        
        Review.objects.create(author=self.user, destination=self.destination, rating=5, comment="Genial")
        Review.objects.create(author=user2, destination=self.destination, rating=4, comment="Bueno")
        
        self.assertEqual(self.destination.destination_reviews.count(), 2)
    
    def test_review_rating_range(self):
        """Test: rating debe ser un número positivo"""
        review = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=3,
            comment="Regular"
        )
        
        self.assertGreater(review.rating, 0)
        self.assertLessEqual(review.rating, 5)
    
    def test_review_cascade_delete_with_user(self):
        """Test: eliminar usuario elimina sus reviews"""
        Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment="Excelente"
        )
        
        self.assertEqual(Review.objects.count(), 1)
        self.user.delete()
        self.assertEqual(Review.objects.count(), 0)
    
    def test_review_cascade_delete_with_destination(self):
        """Test: eliminar destino elimina sus reviews"""
        Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment="Excelente"
        )
        
        self.assertEqual(Review.objects.count(), 1)
        self.destination.delete()
        self.assertEqual(Review.objects.count(), 0)


class DestinationPopularityTest(TestCase):
    """Tests TDD - PBI 1: Calcular popularidad de destinos"""
    
    def setUp(self):
        """Configuración inicial: crear usuario y destinos"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        self.dest1 = Destination.objects.create(name="París", description="La ciudad de la luz")
        self.dest2 = Destination.objects.create(name="Roma", description="La ciudad eterna")
        self.dest3 = Destination.objects.create(name="Londres", description="Capital del Reino Unido")
    
    def test_destination_with_reviews_has_correct_count(self):
        """Test TDD: conteo correcto de reviews"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="A")
        Review.objects.create(destination=self.dest1, author=self.user, rating=4, comment="B")
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="C")
        
        dest_annotated = Destination.objects.annotate(
            review_count=Count('destination_reviews')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.review_count, 3)
    
    def test_destination_without_reviews_has_zero_count(self):
        """Test TDD: destino sin reviews tiene conteo 0"""
        dest_annotated = Destination.objects.annotate(
            review_count=Count('destination_reviews')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.review_count, 0)
    
    def test_average_rating_calculation(self):
        """Test TDD: cálculo correcto de rating promedio"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="A")
        Review.objects.create(destination=self.dest1, author=self.user, rating=4, comment="B")
        Review.objects.create(destination=self.dest1, author=self.user, rating=3, comment="C")
        
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('destination_reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.avg_rating, 4.0)
    
    def test_average_rating_without_reviews_is_none(self):
        """Test TDD: promedio sin reviews es None"""
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('destination_reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertIsNone(dest_annotated.avg_rating)
    
    def test_destinations_ordered_by_review_count(self):
        """Test TDD: ordenamiento por número de reviews (popularidad)"""
        # París: 3 reviews
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="A")
        Review.objects.create(destination=self.dest1, author=self.user, rating=4, comment="B")
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="C")
        
        # Roma: 1 review
        Review.objects.create(destination=self.dest2, author=self.user, rating=5, comment="D")
        
        # Londres: 0 reviews
        
        destinations = Destination.objects.annotate(
            review_count=Count('destination_reviews')
        ).order_by('-review_count')
        
        self.assertEqual(destinations[0].name, "París")
        self.assertEqual(destinations[1].name, "Roma")
        self.assertEqual(destinations[2].name, "Londres")
    
    def test_destinations_ordered_by_rating_when_same_count(self):
        """Test TDD: ordenamiento por rating cuando hay empate en reviews"""
        # París: 2 reviews, promedio 4.5
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="A")
        Review.objects.create(destination=self.dest1, author=self.user, rating=4, comment="B")
        
        # Roma: 2 reviews, promedio 3.0
        Review.objects.create(destination=self.dest2, author=self.user, rating=3, comment="C")
        Review.objects.create(destination=self.dest2, author=self.user, rating=3, comment="D")
        
        destinations = Destination.objects.annotate(
            review_count=Count('destination_reviews'),
            avg_rating=Avg('destination_reviews__rating')
        ).order_by('-review_count', '-avg_rating')
        
        self.assertEqual(destinations[0].name, "París")
        self.assertEqual(destinations[1].name, "Roma")


class DestinationViewTest(TestCase):
    """Tests TDD - PBI 3: Mostrar información de popularidad en la interfaz"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        self.dest1 = Destination.objects.create(name="París", description="Ciudad de la luz")
        self.dest2 = Destination.objects.create(name="Roma", description="Ciudad eterna")
        self.dest3 = Destination.objects.create(name="Londres", description="Capital UK")
    
    def test_destinations_view_loads(self):
        """Test TDD: vista de destinos carga correctamente"""
        response = self.client.get(reverse('destinations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'destinations.html')
    
    def test_template_shows_review_count(self):
        """Test TDD: template muestra número de reviews"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="Genial")
        Review.objects.create(destination=self.dest1, author=self.user, rating=4, comment="Bueno")
        
        response = self.client.get(reverse('destinations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2 reviews')
    
    def test_template_shows_average_rating(self):
        """Test TDD: template muestra rating promedio"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="A")
        Review.objects.create(destination=self.dest1, author=self.user, rating=3, comment="B")
        
        response = self.client.get(reverse('destinations'))
        
        self.assertContains(response, '4.0')  # Promedio de 5 y 3
    
    def test_template_shows_no_reviews_message(self):
        """Test TDD: template muestra 'Sin valoraciones' cuando no hay reviews"""
        response = self.client.get(reverse('destinations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sin valoraciones')
    
    def test_destinations_ordered_correctly_in_view(self):
        """Test TDD: destinos ordenados por popularidad en la vista"""
        # París: 3 reviews
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="A")
        Review.objects.create(destination=self.dest1, author=self.user, rating=4, comment="B")
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="C")
        
        # Roma: 1 review
        Review.objects.create(destination=self.dest2, author=self.user, rating=5, comment="D")
        
        response = self.client.get(reverse('destinations'))
        destinations = response.context['destinations']
        
        self.assertEqual(destinations[0].name, "París")
        self.assertEqual(destinations[1].name, "Roma")
        self.assertEqual(destinations[2].name, "Londres")
    
    def test_view_context_includes_popularity_data(self):
        """Test TDD: contexto de la vista incluye datos de popularidad calculados"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="Test")
        
        response = self.client.get(reverse('destinations'))
        destinations = response.context['destinations']
        
        first_dest = destinations[0]
        self.assertTrue(hasattr(first_dest, 'review_count'))
        self.assertTrue(hasattr(first_dest, 'avg_rating'))

