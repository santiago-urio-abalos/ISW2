from django.contrib import admin
from .models import Cruise, Destination, InfoRequest
from reviews.models import Review
from django.db import models

# Register your models here.
@admin.register(Cruise)
class CruiseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'departure_date')
    search_fields = ('name',)
    list_filter = ('departure_date',)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'has_image')
    search_fields = ('name',)
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Tiene imagen'

@admin.register(InfoRequest)
class InfoRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'created_at')
    list_filter = ('created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'destination', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'destination')
    search_fields = ('author__username', 'destination__name', 'comment')

