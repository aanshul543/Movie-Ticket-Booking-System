from django.db import models
from django.utils.datetime_safe import datetime

# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=30, unique=True)
    state = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class Theatre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Movie(models.Model):
    name = models.CharField(max_length=30, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    def __str__(self):
        return self.name

class Show(models.Model):
    name = models.CharField(max_length=30, unique=True)
    start_time = models.DateTimeField(default=datetime.now, blank=False)
    end_time = models.DateTimeField(default=datetime.now, blank=False)
    total_seats = models.IntegerField(default=100)
    available_seats = models.IntegerField(default=100)
    def __str__(self):
        return self.name

class MovieTheatreShow(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

class BookedTickets(models.Model):
    username = models.CharField(max_length=50)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    booked_seats = models.IntegerField()