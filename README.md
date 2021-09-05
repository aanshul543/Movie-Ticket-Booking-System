# Movie Ticket Booking System APIs

## Process to setting up the project

clone the project into a folder and create a virtual environment
```
virtualenv venv
```

Activate the environment
```
source venv/bin/activate
```

Install all the required dependencies
```
pip install -r requirements.txt
```

### Note : This project is using postgresql as database. You should have installed postgresql in your system. Alternatively you can use any other database and make the database changes in settings.py


Go to the folder where manage.py file placed and run below commands.

```
python manage.py makemigrations
```

```
python manage.py migrate
```

You need to create a super user in order to add movies, theatres and other necessary data.
```
python manage.py createsuperuser
```

Run server.
```
python manage.py runserver
```

I have used swagger for API testing.

### This project is deployed on https://movie-ticketing-system-mts.herokuapp.com/

To add more movies, theatres etc. on this deployed app you need superuser permission.

For superuser permission contact me:

Name: Anshul Agrawal

Mail : aanshul543@gmail.com

Phone : 8952027001