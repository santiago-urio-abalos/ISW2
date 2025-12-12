from django.contrib import admin
<<<<<<< HEAD
from .models import Cruise, Destination, InfoRequest, Review
=======
from .models import Cruise, Destination, InfoRequest
from reviews.models import Review
>>>>>>> 089ae2fcb446be135d0a687d33e6a8eeefc8a59d
from django.db import models

# Register your models here.
@admin.register(Cruise)
class CruiseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'departure_date')
    search_fields = ('name',)
    list_filter = ('departure_date',)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'destination', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('destination__name', 'comment')

@admin.register(InfoRequest)
class InfoRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'created_at')
    list_filter = ('created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'destination', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'destination')
    search_fields = ('author__username', 'destination__name', 'comment')

