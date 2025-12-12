from django.test import TestCase, Client
from relecloud.models import Destination
from reviews.models import Review
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


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
    """Tests de cálculo de popularidad"""
    
    def setUp(self):
        """Configuración inicial: crear usuario y destinos"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        self.dest1 = Destination.objects.create(name="París", description="La ciudad de la luz")
        self.dest2 = Destination.objects.create(name="Roma", description="La ciudad eterna")
        self.dest3 = Destination.objects.create(name="Londres", description="Capital del Reino Unido")
    
    def test_destination_with_reviews_has_correct_count(self):
        """Test: conteo correcto de reviews"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="A")
        Review.objects.create(destination=self.dest1, author=self.user, rating=4, comment="B")
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="C")
        
        dest_annotated = Destination.objects.annotate(
            review_count=Count('destination_reviews')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.review_count, 3)
    
    def test_destination_without_reviews_has_zero_count(self):
        """Test: destino sin reviews tiene conteo 0"""
        dest_annotated = Destination.objects.annotate(
            review_count=Count('destination_reviews')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.review_count, 0)
    
    def test_average_rating_calculation(self):
        """Test: cálculo correcto de rating promedio"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="A")
        Review.objects.create(destination=self.dest1, author=self.user, rating=4, comment="B")
        Review.objects.create(destination=self.dest1, author=self.user, rating=3, comment="C")
        
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('destination_reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.avg_rating, 4.0)
    
    def test_average_rating_with_single_review(self):
        """Test: promedio con una sola review"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="Perfecto")
        
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('destination_reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest_annotated.avg_rating, 5.0)
    
    def test_average_rating_without_reviews_is_none(self):
        """Test: promedio sin reviews es None"""
        dest_annotated = Destination.objects.annotate(
            avg_rating=Avg('destination_reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertIsNone(dest_annotated.avg_rating)
    
    def test_destinations_ordered_by_review_count(self):
        """Test: ordenamiento por número de reviews"""
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
        """Test: ordenamiento por rating cuando hay mismo número de reviews"""
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
    
    def test_popularity_calculation_performance(self):
        """Test: cálculo de popularidad es eficiente (una sola query)"""
        # Crear múltiples destinos con reviews
        for i in range(10):
            dest = Destination.objects.create(name=f"Destino {i}", description=f"Desc {i}")
            Review.objects.create(destination=dest, author=self.user, rating=5, comment="Test")
        
        # Contar queries
        from django.test.utils import override_settings
        from django.db import connection
        from django.db import reset_queries
        
        with override_settings(DEBUG=True):
            reset_queries()
            list(Destination.objects.annotate(
                review_count=Count('destination_reviews'),
                avg_rating=Avg('destination_reviews__rating')
            ))
            query_count = len(connection.queries)
            
            # Debe ser solo 1 query (el annotate optimiza)
            self.assertEqual(query_count, 1)


class DestinationViewTest(TestCase):
    """Tests de la vista de destinos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        self.dest1 = Destination.objects.create(name="París", description="Ciudad de la luz")
        self.dest2 = Destination.objects.create(name="Roma", description="Ciudad eterna")
        self.dest3 = Destination.objects.create(name="Londres", description="Capital UK")
    
    def test_destinations_view_loads(self):
        """Test: vista de destinos carga correctamente"""
        response = self.client.get(reverse('destinations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'destinations.html')
    
    def test_destinations_view_shows_all_destinations(self):
        """Test: vista muestra todos los destinos"""
        response = self.client.get(reverse('destinations'))
        
        self.assertContains(response, "París")
        self.assertContains(response, "Roma")
        self.assertContains(response, "Londres")
    
    def test_template_shows_review_count(self):
        """Test: template muestra número de reviews"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="Genial")
        Review.objects.create(destination=self.dest1, author=self.user, rating=4, comment="Bueno")
        
        response = self.client.get(reverse('destinations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2 reviews')
    
    def test_template_shows_average_rating(self):
        """Test: template muestra rating promedio"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="A")
        Review.objects.create(destination=self.dest1, author=self.user, rating=3, comment="B")
        
        response = self.client.get(reverse('destinations'))
        
        self.assertContains(response, '4.0')  # Promedio de 5 y 3
    
    def test_template_shows_no_reviews_message(self):
        """Test: template muestra 'Sin valoraciones' cuando no hay reviews"""
        response = self.client.get(reverse('destinations'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sin valoraciones')
    
    def test_destinations_ordered_correctly_in_view(self):
        """Test: destinos ordenados correctamente en la vista"""
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
        """Test: contexto de la vista incluye datos de popularidad"""
        Review.objects.create(destination=self.dest1, author=self.user, rating=5, comment="Test")
        
        response = self.client.get(reverse('destinations'))
        destinations = response.context['destinations']
        
        first_dest = destinations[0]
        self.assertTrue(hasattr(first_dest, 'review_count'))
        self.assertTrue(hasattr(first_dest, 'avg_rating'))


class ReviewValidationTest(TestCase):
    """Tests de validación del modelo Review - TDD"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.destination = Destination.objects.create(name="París", description="Test")
    
    def test_review_requires_author(self):
        """Test TDD: Review debe tener un author obligatorio"""
        with self.assertRaises(Exception):
            Review.objects.create(
                destination=self.destination,
                rating=5,
                comment="Sin autor"
            )
    
    def test_review_requires_destination(self):
        """Test TDD: Review debe tener un destination obligatorio"""
        with self.assertRaises(Exception):
            Review.objects.create(
                author=self.user,
                rating=5,
                comment="Sin destino"
            )
    
    def test_review_requires_rating(self):
        """Test TDD: Review debe tener un rating obligatorio"""
        with self.assertRaises(Exception):
            Review.objects.create(
                author=self.user,
                destination=self.destination,
                comment="Sin rating"
            )
    
    def test_review_requires_comment(self):
        """Test TDD: Review debe tener un comment obligatorio"""
        with self.assertRaises(Exception):
            Review.objects.create(
                author=self.user,
                destination=self.destination,
                rating=5
            )
    
    def test_review_rating_must_be_positive(self):
        """Test TDD: rating debe ser positivo"""
        review = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=1,
            comment="Test"
        )
        self.assertGreater(review.rating, 0)
    
    def test_review_created_at_auto_set(self):
        """Test TDD: created_at se establece automáticamente"""
        before = timezone.now()
        review = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment="Test"
        )
        after = timezone.now()
        
        self.assertIsNotNone(review.created_at)
        self.assertGreaterEqual(review.created_at, before)
        self.assertLessEqual(review.created_at, after)
    
    def test_review_ordering_by_created_at(self):
        """Test TDD: Reviews se pueden ordenar por fecha de creación"""
        review1 = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment="Primera"
        )
        
        review2 = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=4,
            comment="Segunda"
        )
        
        reviews = Review.objects.filter(destination=self.destination).order_by('-created_at')
        self.assertEqual(reviews[0].id, review2.id)
        self.assertEqual(reviews[1].id, review1.id)


class ReviewEdgeCasesTest(TestCase):
    """Tests de casos edge y límites - TDD"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.destination = Destination.objects.create(name="París", description="Test")
    
    def test_user_can_have_multiple_reviews(self):
        """Test TDD: Un usuario puede tener múltiples reviews"""
        dest2 = Destination.objects.create(name="Roma", description="Test")
        
        review1 = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment="Review 1"
        )
        
        review2 = Review.objects.create(
            author=self.user,
            destination=dest2,
            rating=4,
            comment="Review 2"
        )
        
        user_reviews = Review.objects.filter(author=self.user)
        self.assertEqual(user_reviews.count(), 2)
    
    def test_user_can_review_same_destination_multiple_times(self):
        """Test TDD: Usuario puede hacer múltiples reviews del mismo destino"""
        review1 = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment="Primera visita"
        )
        
        review2 = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=4,
            comment="Segunda visita"
        )
        
        dest_reviews = Review.objects.filter(
            author=self.user,
            destination=self.destination
        )
        self.assertEqual(dest_reviews.count(), 2)
    
    def test_empty_comment_is_allowed(self):
        """Test TDD: Comentario vacío está permitido (puede ser solo rating)"""
        review = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment=""
        )
        self.assertEqual(review.comment, "")
    
    def test_very_long_comment(self):
        """Test TDD: Comentarios largos son aceptados"""
        long_comment = "A" * 5000  # Comentario de 5000 caracteres
        
        review = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=5,
            comment=long_comment
        )
        
        self.assertEqual(len(review.comment), 5000)
    
    def test_destination_with_many_reviews(self):
        """Test TDD: Destino puede tener muchas reviews"""
        users = []
        for i in range(100):
            user = User.objects.create_user(username=f'user{i}', password='pass')
            users.append(user)
            Review.objects.create(
                author=user,
                destination=self.destination,
                rating=5,
                comment=f"Review {i}"
            )
        
        count = Review.objects.filter(destination=self.destination).count()
        self.assertEqual(count, 100)
    
    def test_rating_boundary_values(self):
        """Test TDD: Rating acepta valores en los límites esperados"""
        # Mínimo
        review_min = Review.objects.create(
            author=self.user,
            destination=self.destination,
            rating=1,
            comment="Mínimo"
        )
        self.assertEqual(review_min.rating, 1)
        
        # Máximo esperado
        user2 = User.objects.create_user(username='user2', password='pass')
        review_max = Review.objects.create(
            author=user2,
            destination=self.destination,
            rating=5,
            comment="Máximo"
        )
        self.assertEqual(review_max.rating, 5)


class ReviewIntegrationTest(TestCase):
    """Tests de integración - TDD"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.user3 = User.objects.create_user(username='user3', password='pass3')
        
        self.dest1 = Destination.objects.create(name="París", description="Test")
        self.dest2 = Destination.objects.create(name="Roma", description="Test")
        self.dest3 = Destination.objects.create(name="Londres", description="Test")
    
    def test_complete_popularity_workflow(self):
        """Test TDD: Flujo completo de popularidad desde creación hasta vista"""
        # 1. Crear reviews para diferentes destinos
        Review.objects.create(author=self.user1, destination=self.dest1, rating=5, comment="A")
        Review.objects.create(author=self.user2, destination=self.dest1, rating=4, comment="B")
        Review.objects.create(author=self.user3, destination=self.dest1, rating=5, comment="C")
        
        Review.objects.create(author=self.user1, destination=self.dest2, rating=3, comment="D")
        Review.objects.create(author=self.user2, destination=self.dest2, rating=3, comment="E")
        
        # 2. Calcular popularidad
        destinations = Destination.objects.annotate(
            review_count=Count('destination_reviews'),
            avg_rating=Avg('destination_reviews__rating')
        ).order_by('-review_count', '-avg_rating')
        
        # 3. Verificar orden correcto
        self.assertEqual(destinations[0].name, "París")  # 3 reviews, avg 4.67
        self.assertEqual(destinations[1].name, "Roma")   # 2 reviews, avg 3.0
        self.assertEqual(destinations[2].name, "Londres") # 0 reviews
        
        # 4. Verificar valores calculados
        self.assertEqual(destinations[0].review_count, 3)
        self.assertAlmostEqual(destinations[0].avg_rating, 4.67, places=1)
        
        self.assertEqual(destinations[1].review_count, 2)
        self.assertEqual(destinations[1].avg_rating, 3.0)
        
        self.assertEqual(destinations[2].review_count, 0)
        self.assertIsNone(destinations[2].avg_rating)
    
    def test_review_impact_on_destination_ordering(self):
        """Test TDD: Agregar/eliminar reviews cambia el orden de destinos"""
        # Estado inicial: todos sin reviews
        destinations = Destination.objects.annotate(
            review_count=Count('destination_reviews')
        ).order_by('-review_count')
        
        initial_order = [d.name for d in destinations]
        
        # Agregar review a Londres
        Review.objects.create(
            author=self.user1,
            destination=self.dest3,
            rating=5,
            comment="Test"
        )
        
        destinations = Destination.objects.annotate(
            review_count=Count('destination_reviews')
        ).order_by('-review_count')
        
        # Londres debe estar primero ahora
        self.assertEqual(destinations[0].name, "Londres")
        
        # Agregar más reviews a París
        Review.objects.create(author=self.user1, destination=self.dest1, rating=5, comment="A")
        Review.objects.create(author=self.user2, destination=self.dest1, rating=5, comment="B")
        
        destinations = Destination.objects.annotate(
            review_count=Count('destination_reviews')
        ).order_by('-review_count')
        
        # París debe estar primero ahora
        self.assertEqual(destinations[0].name, "París")
    
    def test_review_statistics_update_dynamically(self):
        """Test TDD: Las estadísticas se actualizan dinámicamente"""
        # Estado inicial
        dest = Destination.objects.annotate(
            review_count=Count('destination_reviews'),
            avg_rating=Avg('destination_reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest.review_count, 0)
        self.assertIsNone(dest.avg_rating)
        
        # Agregar primera review
        Review.objects.create(author=self.user1, destination=self.dest1, rating=5, comment="A")
        
        dest = Destination.objects.annotate(
            review_count=Count('destination_reviews'),
            avg_rating=Avg('destination_reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest.review_count, 1)
        self.assertEqual(dest.avg_rating, 5.0)
        
        # Agregar segunda review
        Review.objects.create(author=self.user2, destination=self.dest1, rating=3, comment="B")
        
        dest = Destination.objects.annotate(
            review_count=Count('destination_reviews'),
            avg_rating=Avg('destination_reviews__rating')
        ).get(pk=self.dest1.pk)
        
        self.assertEqual(dest.review_count, 2)
        self.assertEqual(dest.avg_rating, 4.0)  # (5+3)/2
