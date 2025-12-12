from django.contrib import admin
<<<<<<< HEAD
<<<<<<< HEAD
from .models import Cruise, Destination, InfoRequest, Review
=======
from .models import Cruise, Destination, InfoRequest
from reviews.models import Review
>>>>>>> 089ae2fcb446be135d0a687d33e6a8eeefc8a59d
from django.db import models
=======
from .models import Cruise, Destination, InfoRequest
from reviews.models import Review
from django.db import DatabaseError
>>>>>>> 96c4a1d8085dc55cd4a61d72cf3c47c6915c8b8c

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
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            # Avoid selecting the `image` column (it may not exist yet in prod DB)
            return qs.defer('image')
        except DatabaseError:
            # If the DB raises an error (missing column), restrict selected
            # fields to those that exist, excluding `image`.
            field_names = [f.name for f in Destination._meta.local_fields if f.name != 'image']
            if field_names:
                return qs.only(*field_names)
            return qs

    def has_image(self, obj):
        # Do not trigger a DB load for `image`. Check the instance dict
        # (loaded fields) and avoid accessing the attribute which would
        # issue another query and fail if column is missing.
        return bool(obj.__dict__.get('image'))
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

