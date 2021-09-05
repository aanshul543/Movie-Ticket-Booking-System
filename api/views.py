import logging
from django.http import JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view
from .models import BookedTickets, Movie, City, MovieTheatreShow, Theatre, Show
from .serializers import MovieSerializer, CitySerializer, TheatreSerializer, ShowSerializer, BookedTicketsSerializer

# logger = logging.getLogger(__name__)
logging.basicConfig(filename='api.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')


# Create your views here.
class MoviesList(generics.ListAPIView):
    # API endpoint that allows movies to be viewed.
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class CitiesList(generics.ListAPIView):
    # API endpoint that allows movies to be viewed.
    queryset = City.objects.all()
    serializer_class = CitySerializer


class MoviesInCity(generics.ListAPIView):
    serializer_class = MovieSerializer

    def get_queryset(self):
        city = self.kwargs['city']
        logging.info(f"Users requested for movies in city {city}")
        city_id = City.objects.filter(name__iexact=city).first().id
        logging.info(f"Requested City Id is {city_id}")
        movies_city = MovieTheatreShow.objects.filter(city_id=city_id)
        return Movie.objects.filter(pk__in=movies_city.values('movie_id').distinct())

class FetchBookedTickets(generics.ListAPIView):
    serializer_class = BookedTicketsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            username = request.user.username
            bookedTickets = BookedTickets.objects.filter(username=username)
            response = []
            for data in bookedTickets:
                obj = {"username": data.username, "movie": data.movie.name, "theatre": data.theatre.name, "show": data.show.name, "city": data.city.name, "Booked": data.booked_seats}              
                response.append(obj)
            return JsonResponse(response, safe=False)
        else:
            logging.warning("Unauthorized attempt to book ticket")
            return JsonResponse({"message": "Kindly login to continue booking for your favorite movie now"},
                            status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def available_shows_for_movie(request, movie, city):
    movie_name = movie.title()
    city_name = city.title()
    requested_city = City.objects.filter(name=city_name).first()
    requested_movie = Movie.objects.filter(name=movie_name).first()
    if requested_city and requested_movie:
        shows_for_requested_movie_in_city = MovieTheatreShow.objects.filter(
            city=requested_city, movie=requested_movie).values('show_id', 'theatre_id')
        theatre_show_list = []
        for show_in_theatre in shows_for_requested_movie_in_city:
            theatre_show_list.append(show_in_theatre)

        theatre_shows_map = [
            {'theatre_id': id, 'show_id': [d['show_id'] for d in theatre_show_list if d['theatre_id'] == id]}
            for id in set(map(lambda d: d['theatre_id'], theatre_show_list))]
        theatres_list = []
        for theatre_show in theatre_shows_map:
            theatre = Theatre.objects.filter(pk=theatre_show['theatre_id']).first()
            theatre_shows_json = TheatreSerializer(theatre).data
            shows_list_json = []
            for show_id in theatre_show['show_id']:
                show = Show.objects.filter(pk=show_id).first()
                shows_list_json.append(ShowSerializer(show).data)
            theatre_shows_json["shows"] = shows_list_json
            theatres_list.append(theatre_shows_json)
        theatre_shows_json = theatres_list
        movie_details_json = MovieSerializer(requested_movie).data
        movie_details_json["theatres"] = theatre_shows_json
        return JsonResponse(movie_details_json, safe=False)
    elif requested_city is None:
        return JsonResponse({"message": f"{city_name} is not registered"})
    elif requested_movie is None:
        return JsonResponse({"message": f"{movie_name} movie is not available"})

    return JsonResponse({"message": "Something went wrong"})

@api_view(['POST'])
def book_ticket(request, city, movie, theatre, show, number_of_tickets):
    if request.user.is_authenticated:
        # Normalizing user input data
        city_name, movie_name, theatre_name, show_name, numberOfTickets = city.title(), movie.title(), theatre.title(), show.title(), int(number_of_tickets.title())
        city = City.objects.filter(name=city_name).first()
        movie = Movie.objects.filter(name=movie_name).first()
        theatre = Theatre.objects.filter(name=theatre_name).first()
        show = Show.objects.filter(name=show_name).first()
        if city is None:
            return JsonResponse({"message": f"City {city_name} is not registered."})
        if movie is None:
            return JsonResponse({"message": f"Movie {movie_name} is not available"})
        if theatre is None:
            return JsonResponse({"message": f"Theatre {theatre_name} is not registered. Please check available shows list."})
        if show is None:
            return JsonResponse({"message": f"Show {show_name} is not valid. Please check available shows list."})
        movie_show = MovieTheatreShow.objects.filter(
            city=city, movie=movie, theatre=theatre, show=show).first()
        if movie_show:
            if movie_show.show.available_seats >= numberOfTickets:
                movie_show.show.available_seats -= numberOfTickets
                bookedTicketsData = BookedTickets(username = request.user.username, movie = movie, theatre = theatre, show = show, city = city, booked_seats = numberOfTickets)
                movie_show.show.save()
                bookedTicketsData.save()
                return JsonResponse({"message": "You have successfully booked ticket for this show"})        
            elif movie_show.show.available_seats == 0:
                return JsonResponse({"message": "There are no Seats available for this Show"})
            else:
                return JsonResponse({"message": f"There are only {movie_show.show.available_seats} Seats available for this Show"})
        else:
            return JsonResponse({"message": "Booking failed as the selected preferences are incorrect/in valid"})
    else:
        logging.warning("Unauthorized attempt to book ticket")
        return JsonResponse({"message": "Kindly login to continue booking for your favorite movie now"},
                        status=status.HTTP_401_UNAUTHORIZED)