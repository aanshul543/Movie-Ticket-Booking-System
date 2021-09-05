from django.urls import include, path
from . import views
from django.views.decorators.csrf import csrf_exempt
from .views import MoviesList, CitiesList, MoviesInCity, FetchBookedTickets

urlpatterns = [
    path('movies', MoviesList.as_view(), name="movies"),
    path('cities', CitiesList.as_view(), name="cities"),
    path('movies/<city>', MoviesInCity.as_view(), name="movies_in_city"),
    path('book/<city>/<movie>/<theatre>/<show>/<number_of_tickets>', views.book_ticket, name="book_ticket"),
    path('shows/<movie>/<city>', views.available_shows_for_movie, name="shows_of_movie_in_city"),
    path('bookedtickets', FetchBookedTickets.as_view(), name="Show all booked tickets for logged in user"),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
]