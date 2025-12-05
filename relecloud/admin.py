from django.contrib import admin
from .models import Cruise, Destination, InfoRequest
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

@admin.register(InfoRequest)
class InfoRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'created_at')
    list_filter = ('created_at',)

