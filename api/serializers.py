import re
from rest_framework import serializers, exceptions  # type: ignore
from api.models import Movie, Genre, Reviews, Usuario, GenreChoices
from django.contrib.auth import authenticate


class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:

        extra_kwargs = {"password": {"write_only": True}}

        model = Usuario
        fields = ("nombre", "tel", "email", "password")

    def validate_password(self, value):

        valid_password = True

        if len(value) < 8:
            valid_password = False

        if not re.match(r"^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z]).*$", value):
            valid_password = False

        if valid_password:
            return value
        else:
            raise exceptions.ValidationError("Invalid password format")

    def create(self, validated_data):
        return Usuario.objects.create_user(
            username=validated_data["email"], **validated_data
        )

    def update(self, instance, validated_data):
        if validated_data.get("password"):
            instance.set_password(validated_data.pop("password"))
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):

        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    raise exceptions.ValidationError("User is inactive")
            else:
                raise exceptions.ValidationError(
                    "Unable to login with provided credentials"
                )
        else:
            raise exceptions.ValidationError('Must include "email" and "password"')
        return data


class GenreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class MovieDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class ReviewListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        extra_kwargs = {"user": {"read_only": True}}
        fields = "__all__"


class ReviewDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        extra_kwargs = {"user": {"read_only": True}}
        fields = "__all__"
