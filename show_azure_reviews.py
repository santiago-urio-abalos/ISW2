import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyect.settings')
django.setup()

from reviews.models import Review
from django.db.models import Count, Avg

print("\n" + "="*80)
print("📊 REVIEWS EN AZURE POSTGRESQL (santiagodb.postgres.database.azure.com)")
print("="*80 + "\n")

reviews = Review.objects.select_related('destination', 'author').all()
print(f"Total de reviews en la base de datos: {reviews.count()}\n")

if reviews.count() == 0:
    print("⚠️  No hay reviews en la base de datos todavía.")
    print("Puedes crear reviews desde: https://newhope.azurewebsites.net/admin/relecloud/review/")
else:
    for i, review in enumerate(reviews, 1):
        print(f"{i}. ⭐ {review.rating}/5 - {review.destination.name}")
        print(f"   Autor: {review.author.username}")
        print(f"   Comentario: {review.comment}")
        print(f"   Fecha: {review.created_at.strftime('%Y-%m-%d %H:%M')}")
        print()

print("="*80)
print("📈 RESUMEN POR DESTINO")
print("="*80 + "\n")

from relecloud.models import Destination
destinations = Destination.objects.annotate(
    review_count=Count('destination_reviews'),
    avg_rating=Avg('destination_reviews__rating')
).order_by('-review_count', '-avg_rating')

for dest in destinations:
    if dest.review_count > 0:
        print(f"✓ {dest.name}: {dest.review_count} reviews, promedio {dest.avg_rating:.1f}/5")
    else:
        print(f"  {dest.name}: Sin reviews")

print("\n" + "="*80)
