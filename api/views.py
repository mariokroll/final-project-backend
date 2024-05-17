from rest_framework import generics  # type: ignore
from rest_framework import permissions  # type: ignore
from rest_framework import generics, status  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.authtoken.models import Token  # type: ignore
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from api.models import Movie, Genre, Reviews, Usuario
from django.db.models import Avg
from api.serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    GenreListSerializer,
    ReviewListSerializer,
    ReviewDetailSerializer,
    UsuarioSerializer,
    LoginSerializer,
)
import torch
from api.recommender import RecommenderSystem


def get_matrix():
    tensor = torch.zeros((Usuario.objects.all().count(), Movie.objects.all().count()))
    user_dict = {user.id: index for index, user in enumerate(Usuario.objects.all())}
    movie_dict = {movie.id: index for index, movie in enumerate(Movie.objects.all())}
    for review in Reviews.objects.all():
        tensor[user_dict[review.user.id]][movie_dict[review.movie.id]] = review.rating
    return tensor, user_dict, movie_dict


recommender = RecommenderSystem()
# Does it only once in a session. Matrix is not going to change substantially.


USER_ADMIN = "admin@django.com"
PASSWORD_ADMIN = "@Dmin2003"


class RegistroView(generics.ListCreateAPIView):
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()
    pagination_class = None

    def handle_exception(self, exc):
        if isinstance(exc, IntegrityError):
            return Response(
                {"error": "Email already exists"}, status=status.HTTP_409_CONFLICT
            )
        return super().handle_exception(exc)


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            # define una respuesta que incluya la cookie de sesión
            response = Response(status=status.HTTP_201_CREATED)
            response.set_cookie(
                key="session",
                value=token.key,
                secure=True,
                httponly=True,
                samesite="none",
            )
            return response
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class UsuarioView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = UsuarioSerializer

    def get_object(self):
        user = Token.objects.get(key=self.request.COOKIES.get("session")).user
        return user

    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return super().handle_exception(exc)


class LogoutView(generics.DestroyAPIView):
    def delete(self, request):
        try:
            token = Token.objects.get(key=request.COOKIES.get("session"))
            token.delete()
            response = Response({"status": "success"})
            response.delete_cookie("session")
            return response
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class GenreListCreate(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreListSerializer
    pagination_class = None


class GenreRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreListSerializer


class MovieListCreate(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieListSerializer

    def perform_create(self, serializer):
        user = Token.objects.get(key=self.request.COOKIES.get("session")).user
        if str(user) != USER_ADMIN:  # Only admin can update movies.
            raise PermissionError
        serializer.save()

    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist) or isinstance(exc, PermissionError):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return super().handle_exception(exc)

    def get_queryset(self):
        queryset = Movie.objects.all()
        genre = self.request.query_params.get("genre", None)
        title = self.request.query_params.get("title", None)
        rating = self.request.query_params.get("rating", None)
        description = self.request.query_params.get("description", None)
        order = self.request.query_params.get("order", None)
        director = self.request.query_params.get("director", None)

        allowed_params = {
            "genre",
            "title",
            "rating",
            "description",
            "order",
            "director",
            "page",
        }
        request_params = set(self.request.query_params.keys())
        if not request_params.issubset(allowed_params):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if genre is not None:
            queryset = queryset.filter(genre=genre)
        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        if rating is not None:
            queryset = queryset.filter(rating__gte=rating)
        if description is not None:
            queryset = queryset.filter(description__icontains=description)
        if order is not None:
            queryset = queryset.order_by("rating")[::-1]
        if director is not None:
            queryset = queryset.filter(director__icontains=director)
        return queryset


class MovieRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer

    def perform_update(self, serializer):
        user = Token.objects.get(key=self.request.COOKIES.get("session")).user
        if str(user) != USER_ADMIN:  # Only admin can update movies.
            raise PermissionError
        serializer.save()

    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist) or isinstance(exc, PermissionError):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return super().handle_exception(exc)

    def delete(self, request, *args, **kwargs):
        user = Token.objects.get(key=request.COOKIES.get("session")).user
        if str(user) != USER_ADMIN:  # Only admin can update movies.
            raise PermissionError
        return super().delete(request)


class ReviewListCreate(generics.ListCreateAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewListSerializer

    def perform_create(self, serializer):
        user = Token.objects.get(key=self.request.COOKIES.get("session")).user
        movie = Movie.objects.get(pk=self.request.data["movie"])
        if Reviews.objects.filter(user=user, movie=movie).exists():
            raise IntegrityError
        serializer.save(user=user)
        movie.rating = Reviews.objects.filter(movie=movie).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        movie.save()

    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        elif isinstance(exc, IntegrityError):
            return Response(
                {"error": "User already reviewed this movie"},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            return super().handle_exception(exc)

    def get_queryset(
        self,
    ):  # Para poder acceder a todas las críticas de una película y mostrarlas.
        queryset = Reviews.objects.all()
        movie = self.request.query_params.get("movie", None)
        order = self.request.query_params.get("order", None)
        if movie is not None:
            queryset = queryset.filter(movie=movie)
        if order is not None:
            queryset = queryset.order_by("rating")[::-1]
        return queryset


class ReviewRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewDetailSerializer

    def perform_update(self, serializer):
        user = self._check_user()
        serializer.save(user=user)
        movie = Movie.objects.get(pk=self.request.data["movie"])
        movie.rating = Reviews.objects.filter(movie=movie).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        movie.save()

    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist) or isinstance(exc, PermissionError):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return super().handle_exception(exc)

    def _check_user(self) -> Token.user:
        user = Token.objects.get(key=self.request.COOKIES.get("session")).user
        old_user = Reviews.objects.get(pk=self.kwargs["pk"]).user
        if user != old_user:
            raise PermissionError
        return user

    def delete(self, request, *args, **kwargs):
        self._check_user()
        return super().delete(request)


class RecommendView(generics.RetrieveAPIView):
    def get(self, request):
        tensor, user_dict, movie_dict = get_matrix()
        recommender.fit(tensor)
        user = Token.objects.get(
            key=request.COOKIES.get("session")
        ).user  # Get the user
        recommend = recommender.forward(user_dict[user.id])
        recommend_id = list(movie_dict.keys())[
            list(movie_dict.values()).index(recommend)
        ]
        return Response({"movie": recommend_id})

    def handle_exception(self, exc):  # Only recommend if user is logged in.
        if isinstance(exc, ObjectDoesNotExist):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return super().handle_exception(exc)
