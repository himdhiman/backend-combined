from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from authentication import github, models, google
from authentication.register import register_social_user
from rest_framework.exceptions import AuthenticationFailed
from datetime import date
from django.conf import settings
from authentication.helper import convert_to_list


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(CustomTokenObtainPairSerializer, cls).get_token(user)
        token["user_data"] = {}
        token["user_data"]["email"] = user.email
        token["user_data"]["is_verified"] = user.is_verified
        token["user_data"]["is_admin"] = user.is_admin
        token["user_data"]["first_name"] = user.first_name
        token["user_data"]["last_name"] = user.last_name
        token["user_data"]["username"] = user.username
        token["user_data"]["profile_pic"] = user.profile_pic
        user.last_login = date.today()
        user.save()
        return token


class UserSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = models.CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "username",
            "password",
            "created",
            "updated",
        ]
        read_only_field = ["is_active"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "username",
            "last_login",
            "score",
            "rank",
        ]


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data["sub"]
        except:
            raise serializers.ValidationError(
                "The token is invalid or expired. Please login again."
            )
        if (
            user_data["aud"]
            != "64402702960-mlmnvge26bhhdf6ghgrt6viqbqhv0610.apps.googleusercontent.com"
        ):
            raise AuthenticationFailed("oops, who are you?")
        user_id = user_data["sub"]
        email = user_data["email"]
        name = user_data["name"]
        return register_social_user(
            provider="google",
            pic=user_data["picture"],
            user_id=user_id,
            email=email,
            name=name,
        )


class GithubSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = github.Github.validate(auth_token)
        try:
            user_data["email"]
        except:
            raise serializers.ValidationError(
                "The token is invalid or expired. Please login again."
            )
        user_id = user_data["username"]
        email = user_data["email"]
        name = user_data["name"]
        return register_social_user(
            provider="github",
            user_id=user_id,
            email=email,
            name=name,
            pic=user_data["avatar_url"],
        )


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    mapping_list = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sept",
        "Oct",
        "Nov",
        "Dec",
    ]

    class Meta:
        model = models.UserProfile
        fields = "__all__"

    def to_representation(self, obj):
        primitive_repr = super(UserProfileSerializer, self).to_representation(obj)
        if obj.submissions is not None:
            data = convert_to_list(obj.submissions)
            lst = list()
            for i in data:
                date_temp = i.split("-")
                new_dict = {}
                new_dict["date"] = (
                    date_temp[-1] + f" {self.mapping_list[int(date_temp[-2]) - 1]}"
                )
                new_dict["Questions Solved"] = len(data[i])
                lst.append(new_dict)
            primitive_repr["submissions"] = lst
        return primitive_repr


class StaticDataSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.StaticData
        fields = "__all__"
