from django.test import TestCase
from .models import Destination, Review
from django.db.models import Count, Avg

# Create your tests here.

class DestinationPopularityTest(TestCase):
    """
    Tests para el cálculo de popularidad de destinos basado en reviews
    """
    
    def setUp(self):
        """Configuración inicial: crear destinos de prueba"""
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
        """Test: destino con reviews tiene conteo correcto"""
        # Crear 3 reviews para París
        Review.objects.create(destination=self.dest1, rating=5, comment="Excelente")
        Review.objects.create(destination=self.dest1, rating=4, comment="Muy bueno")
        Review.objects.create(destination=self.dest1, rating=5, comment="Increíble")
        
        # Anotar con count
        dest_annotated = Destination.objects.annotate(
            review_count=Count('reviews')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.review_count, 3)
    
    def test_destination_without_reviews_has_zero_count(self):
        """Test: destino sin reviews tiene popularidad = 0"""
        dest_annotated = Destination.objects.annotate(
            review_count=Count('reviews')
        ).get(pk=self.dest3.pk)
        
        self.assertEqual(dest_annotated.review_count, 0)
    
    def test_average_rating_calculation(self):
        """Test: cálculo correcto de rating promedio"""
        # Reviews con ratings 5, 4, 3 -> promedio = 4.0
        Review.objects.create(destination=self.dest1, rating=5)
        Review.objects.create(destination=self.dest1, rating=4)
        Review.objects.create(destination=self.dest1, rating=3)
        
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.avg_rating, 4.0)
    
    def test_destination_without_reviews_has_null_average(self):
        """Test: destino sin reviews tiene promedio None"""
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).get(pk=self.dest3.pk)
        
        self.assertIsNone(dest_annotated.avg_rating)
    
    def test_destinations_ordered_by_popularity(self):
        """Test: destinos se ordenan correctamente por popularidad"""
        # París: 3 reviews
        Review.objects.create(destination=self.dest1, rating=5)
        Review.objects.create(destination=self.dest1, rating=4)
        Review.objects.create(destination=self.dest1, rating=5)
        
        # Roma: 1 review
        Review.objects.create(destination=self.dest2, rating=5)
        
        # Londres: 0 reviews
        
        # Obtener destinos ordenados por popularidad
        destinations = Destination.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')
        
        # Verificar orden: París (3), Roma (1), Londres (0)
        self.assertEqual(destinations[0].name, "París")
        self.assertEqual(destinations[1].name, "Roma")
        self.assertEqual(destinations[2].name, "Londres")
    
    def test_popularity_with_same_count_different_rating(self):
        """Test: con mismo # de reviews, ordena por rating promedio"""
        # París: 2 reviews, promedio 4.5
        Review.objects.create(destination=self.dest1, rating=5)
        Review.objects.create(destination=self.dest1, rating=4)
        
        # Roma: 2 reviews, promedio 3.0
        Review.objects.create(destination=self.dest2, rating=3)
        Review.objects.create(destination=self.dest2, rating=3)
        
        destinations = Destination.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')
        
        # París debería estar primero por mejor rating
        self.assertEqual(destinations[0].name, "París")
        self.assertEqual(destinations[1].name, "Roma")
    
    def test_review_model_creation(self):
        """Test: creación correcta del modelo Review"""
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
        """Test: método __str__ del modelo Review"""
        review = Review.objects.create(
            destination=self.dest1,
            rating=4
        )
        
        expected_str = f'Review for {self.dest1.name} - 4/5'
        self.assertEqual(str(review), expected_str)
    
    def test_popularity_calculation_performance(self):
        """Test: cálculo de popularidad en menos de 1 segundo"""
        import time
        
        # Crear varios destinos y reviews
        for i in range(10):
            dest = Destination.objects.create(
                name=f"Destino {i}",
                description=f"Descripción {i}"
            )
            for j in range(5):
                Review.objects.create(destination=dest, rating=(j % 5) + 1)
        
        start_time = time.time()
        
        # Ejecutar consulta con anotaciones
        destinations = Destination.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-review_count', '-avg_rating')
        
        list(destinations)  # Forzar evaluación del queryset
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verificar que toma menos de 1 segundo
        self.assertLess(execution_time, 1.0)
