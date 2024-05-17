from django.urls import path, include
from .views import GenreListCreate, MovieListCreate, MovieRetrieveUpdateDestroy, ReviewListCreate, ReviewRetrieveUpdateDestroy, \
RegistroView, LoginView, UsuarioView, LogoutView, GenreRetrieveUpdateDestroy, RecommendView

urlpatterns = [

    path('users/', RegistroView.as_view(), name='registro'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/me/', UsuarioView.as_view(), name='usuario'),
    path('users/logout/', LogoutView.as_view(), name='logout'),
    path('genres/', GenreListCreate.as_view(), name='genre-list'),
    path('genres/<int:pk>/', GenreRetrieveUpdateDestroy.as_view(), name='genre-retrieve-update-destroy'),
    path('movies/', MovieListCreate.as_view(), name='movie-list-create'),
    path('movies/<int:pk>/', MovieRetrieveUpdateDestroy.as_view(), name='movie-retrieve-update-destroy'),
    path('reviews/', ReviewListCreate.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewRetrieveUpdateDestroy.as_view(), name='review-retrieve-update-destroy'),
    path('recommend/', RecommendView.as_view(), name='recommend'),

]
