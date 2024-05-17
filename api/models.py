from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum
from django.core.validators import MaxValueValidator, MinValueValidator


# Tenemos el esquema general de la base de datos (Sin usuarios, ni autenticación)
# Las validaciones las hacemos mas tarde. 


class Usuario(AbstractUser):
    
    nombre = models.CharField(max_length=256)
    tel = models.CharField(max_length=32)
    email = models.EmailField()
    password = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

class GenreChoices(Enum):
    FANTASY = 'fantasy'
    HORROR = 'horror'
    ROMANCE = 'romance'
    ACTION = 'action'
    COMEDY = 'comedy'
    DRAMA = 'drama'
    SCIFI = 'sci-fi'

class Genre(models.Model):
    name = models.CharField(max_length=32, choices= [(choice.name,
    choice.value) for choice in GenreChoices], unique=True)
    def __str__(self):
        return self.name    

class Movie(models.Model):
    title = models.CharField(max_length=32, unique=True)
    director = models.CharField(max_length=32)
    description = models.TextField()
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE) # one to many relationship
    year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2024)])
    rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=0.0)
    # Añadir images
    images = models.ImageField(upload_to='images/', default='images/default.png')
    class Meta:
        ordering = ('id',) # order by id

    def __str__(self):
        return self.title
        
    
class Reviews(models.Model):
    # Cuando añadamos usuarios asegurarnos de que solo se puede añadir una review por [usuario, pelicula]
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)    
    review = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.review
    
# comandos desde la shell para crear una pelicula 
# from api.models import Movie, Genre
# g = Genre.objects.create(name='action')
# m = Movie.objects.create(title='The Dark Knight', director='Christopher Nolan', description='Batman', genre=g, year=2008, rating=9.0)
# filtrar por titulo 
# Movie.objects.filter(title='The Dark Knight')