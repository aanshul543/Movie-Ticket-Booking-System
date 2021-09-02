from django.urls import include, path
from . import views
from .views import MoviesList, CitiesList, MoviesInCity

urlpatterns = [
    path('movies', MoviesList.as_view(), name="movies"),
    path('cities', CitiesList.as_view(), name="cities"),
    path('movies/<city>', MoviesInCity.as_view(), name="movies_in_city"),
    path('book/<city>/<movie>/<theatre>/<show>', views.book_ticket, name="book_ticket"),
    path('shows/<movie>/<city>', views.available_shows_for_movie, name="shows_of_movie_in_city"),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
]