from django.contrib import admin
from .models import City, Movie, Show, Theatre, MovieTheatreShow

# Register your models here.
admin.site.register(City)
admin.site.register(Movie)
admin.site.register(Show)
admin.site.register(Theatre)
admin.site.register(MovieTheatreShow)