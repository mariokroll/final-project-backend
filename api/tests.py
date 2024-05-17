from django.test import TestCase
from api.models import Usuario, Genre, Movie, Reviews
from django.db.utils import IntegrityError, DataError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import api.serializers as serializers 
from api.views import ReviewListCreate, LoginView, UsuarioView, LogoutView
from django.core.validators import MinValueValidator
from rest_framework.test import APIClient
from django.urls import reverse

"""
    En este archivo se realizarán los test unitarios para las clases Usuario, Genre, Movie y Reviews
    Nos centraremos en los métodos de validación de los campos de los modelos. Nos vamos a centrar en que 
    los parametros pasados a los distintos campos sean válidos y que se lancen las excepciones correspondientes
    en caso de que no lo sean. 
    
"""
  
class UsuarioTestCase(TestCase):

    def test_validate_password_valid(self):
       password = 'Password1234'
       user = serializers.UsuarioSerializer(
           data = {
                'nombre': 'test',
                'tel': '123456789',
                'email': 'antonio@gmail.com',
                'password': password
            }
       )
       
       self.assertEqual(user.validate_password(password), password)

    def test_validate_password_invalid(self):
        password = 'password1234'
        user = serializers.UsuarioSerializer(
            data = {
                'nombre': 'test',
                'tel': '123456789',
                'email': 'antio@gmail.com',
                'password': password
            }
        )

        
        with self.assertRaises(Exception):
            user.validate_password(password)


class GenreTestCase(TestCase):

    def test_genre_str(self):
        genre = Genre(name='comedy')
        self.assertEqual(str(genre), 'comedy')


class MovieTestCase(TestCase):
        
        def setUp(self):
            self.client = APIClient()
    
        def test_movie_str(self):
            genre = Genre.objects.create(name='comedy')
            movie = Movie(
                title='test',
                director='test',
                description='test',
                genre=genre,
                year=2020,
                rating=5
            )
            self.assertEqual(str(movie), 'test')

        def test_movie_year_min(self):
            genre = Genre.objects.create(name='comedy')
            data = {
                "title": "test123456",
                "director": "test",
                "description": "test",
                "genre": genre.id,
                "year": 1899,
                "rating": 5
            }

            movie_ser = serializers.MovieListSerializer(data=data)
            movie_ser.is_valid()
            self.assertEqual(movie_ser.errors.keys(), {'year'})

                
                 
        def test_movie_year_max(self):

            genre = Genre.objects.create(name='comedy')

            data = {
                "title": "PEPEPE",
                "director": "test",
                "description": "test",
                "genre": genre.id,
                "year": 2025,
                "rating": 5
            }
            movie_ser = serializers.MovieListSerializer(data=data) 
            movie_ser.is_valid()
            self.assertEqual(movie_ser.errors.keys(), {'year'})

        def test_movie_rating_min(self):
            genre = Genre.objects.create(name='comedy')
            data = {
                "title": "PEPEPE",
                "director": "test",
                "description": "test",
                "genre": genre.id,
                "year": 2020,
                "rating": -7
            }
            movie_ser = serializers.MovieListSerializer(data=data)
            movie_ser.is_valid()
            self.assertEqual(movie_ser.errors.keys(), {'rating'})
        
        def test_movie_rating_max(self):
            genre = Genre.objects.create(name='comedy')
            data = {
                "title": "PEPEPE",
                "director": "test",
                "description": "test",
                "genre": genre.id,
                "year": 2020,
                "rating": 15
            }
            movie_ser = serializers.MovieListSerializer(data=data)
            movie_ser.is_valid()
            self.assertEqual(movie_ser.errors.keys(), {'rating'})
        
        def test_get_movie_list(self):
            url = reverse('movie-list-create')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        def get_movie_from_pk(self):
            url = reverse('movie-retrieve-update-destroy', kwargs={'pk': 1})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)



class ReviewTestCase(TestCase): 
    # Vamos a realizar los test unitarios para la clase Reviews 

    def test_review_rating_min(self):
        genre = Genre.objects.create(name='comedy')
        data_user = {
                'nombre': 'test',
                'tel': '123456789',
                'email': 'antonnn@gmail.com',
                'password': 'Password1234'
        }
        user_ser = serializers.UsuarioSerializer(data=data_user)
        movie_data = {
                "title": "test123456",
                "director": "test",
                "description": "test",
                "genre": genre.id,
                "year": 2020,
                "rating": 5
            }
        movie_ser = serializers.MovieListSerializer(data=movie_data)

        if user_ser.is_valid() and movie_ser.is_valid():
            user_ser.save()
            movie_ser.save()
            data_logging_user = {
                'email': 'antonnn@gmail.com',
                'password': 'Password1234'
            }
            login_ser = serializers.LoginSerializer(data=data_logging_user)
            if login_ser.is_valid():
                # accedemos al id de la pelicula 
                id_movie = Movie.objects.get(title='test123456').id
                data_review = {
                    'user': 1, 
                    'movie': id_movie,
                    'review': 'test',
                    'rating': -7
                }
                review_ser = serializers.ReviewListSerializer(data=data_review)
                review_ser.is_valid()
                self.assertEqual(review_ser.errors.keys(), {'rating'})

    def test_review_rating_max(self):

        genre = Genre.objects.create(name='comedy')
        data_user = {
                'nombre': 'testmax',
                'tel': '123456789',
                'email': 'anton@gmail.com',
                'password': 'Password1234'
        }
        user_ser = serializers.UsuarioSerializer(data=data_user)

        movie_data = {
                "title": "testMax",
                "director": "test",
                "description": "test",
                "genre": 1,
                "year": 2020,
                "rating": 5
            }
        movie_ser = serializers.MovieListSerializer(data=movie_data)

        if user_ser.is_valid() and movie_ser.is_valid(): # comprobación extra para asegurarnos de que los datos son válidos
            user_ser.save()
            movie_ser.save()
            data_logging_user = {
                'email': 'anton@gmail.com',
                'password': 'Password1234'
            }
            login_ser = serializers.LoginSerializer(data=data_logging_user)
            if login_ser.is_valid():
                # accedemos al id de la pelicula 
                id_movie = Movie.objects.get(title='testMax').id
                data_review = {
                    'user': 1, # este campo no importa, pues al final y al cabo la review la hará el usuario que ha iniciado sesión
                    'movie': id_movie,
                    'review': 'test',
                    'rating': 15
                }
                review_ser = serializers.ReviewListSerializer(data=data_review)
                review_ser.is_valid()
                self.assertEqual(review_ser.errors.keys(), {'rating'})
