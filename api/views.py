import logging
from django.http import JsonResponse
from rest_framework import generics, status
from .models import Movie, City, MovieTheatreShow, Theatre, Show
from .serializers import MovieSerializer, CitySerializer, TheatreSerializer, ShowSerializer

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
        theatre_shows_json = get_theatre_shows_json(theatre_show_list)
        movie_details_json = MovieSerializer(requested_movie).data
        movie_details_json["theatres"] = theatre_shows_json
        return JsonResponse(movie_details_json, safe=False)
    elif requested_city is None:
        return JsonResponse({"message": f"{city_name} is not registered"})
    elif requested_movie is None:
        return JsonResponse({"message": f"{movie_name} movie is not available"})

    return JsonResponse({"message": "Something went wrong"})


def get_theatre_shows_json(list_of_theatre_and_show):
    theatre_shows_map = [
        {'theatre_id': id, 'show_id': [d['show_id'] for d in list_of_theatre_and_show if d['theatre_id'] == id]}
        for id in set(map(lambda d: d['theatre_id'], list_of_theatre_and_show))]
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
    return theatres_list


def book_ticket(request, city, movie, theatre, show):
    if request.user.is_authenticated:
        # Normalizing user input data
        city_name, movie_name, theatre_name, show_name = city.title(), movie.title(), theatre.title(), show.title()
        city = City.objects.filter(name=city_name).first()
        movie = Movie.objects.filter(name=movie_name).first()
        theatre = Theatre.objects.filter(name=theatre_name).first()
        show = Show.objects.filter(name=show_name).first()
        movie_show = MovieTheatreShow.objects.filter(
            city=city, movie=movie, theatre=theatre, show=show).first()
        if movie_show:
            if movie_show.show.available_seats >= 1:
                movie_show.show.available_seats -= 1
                movie_show.show.save()
                return JsonResponse({"message": "You have successfully booked ticket for this show"})
            else:
                return JsonResponse({"message": "There are no Seats available for this Show"})
        else:
            return JsonResponse({"message": "Booking failed as the selected preferences are incorrect/in valid"})
    logging.warning("Unauthorized attempt to book ticket")
    return JsonResponse({"message": "Kindly login to continue booking for your favorite movie now"},
                        status=status.HTTP_401_UNAUTHORIZED)