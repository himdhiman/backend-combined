from django.contrib.auth import get_user_model
import random, jwt
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from datetime import date
from authentication.models import UserProfile


def get_jwt_token(user):
    tokens = {
        "refresh": str(RefreshToken.for_user(user)),
        "access": str(RefreshToken.for_user(user).access_token),
    }
    decode_JWT_refresh = jwt.decode(tokens["refresh"], settings.SECRET_KEY, "HS256")
    decode_JWT_access = jwt.decode(tokens["access"], settings.SECRET_KEY, "HS256")

    decode_JWT_refresh["email"] = user.email
    decode_JWT_refresh["is_admin"] = user.is_admin
    decode_JWT_refresh["is_verified"] = user.is_verified
    decode_JWT_refresh["first_name"] = user.first_name
    decode_JWT_refresh["last_name"] = user.last_name
    decode_JWT_refresh["username"] = user.username
    decode_JWT_refresh["profile_pic"] = user.profile_pic

    decode_JWT_access["email"] = user.email
    decode_JWT_access["is_admin"] = user.is_admin
    decode_JWT_access["is_verified"] = user.is_verified
    decode_JWT_access["first_name"] = user.first_name
    decode_JWT_access["last_name"] = user.last_name
    decode_JWT_access["username"] = user.username
    decode_JWT_access["profile_pic"] = user.profile_pic

    tokens["refresh"] = jwt.encode(decode_JWT_refresh, settings.SECRET_KEY, "HS256")
    tokens["access"] = jwt.encode(decode_JWT_access, settings.SECRET_KEY, "HS256")

    user.last_login = date.today()
    user.save()
    return tokens


def generate_username(name):
    User = get_user_model()
    username = "".join(name.split(" ")).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(provider, user_id, email, name, pic):
    User = get_user_model()
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():
        if provider == filtered_user_by_email[0].auth_provider:
            user = filtered_user_by_email[0]
            return get_jwt_token(user)
        else:
            raise AuthenticationFailed(
                detail="Please continue your login using "
                + filtered_user_by_email[0].auth_provider
            )
    else:
        if name:
            splitted_name = name.split(" ")
            user = {
                "username": generate_username(name),
                "email": email,
                "password": settings.SECRET_KEY,
                "first_name": splitted_name[0],
                "last_name": splitted_name[-1],
            }
        else:
            user = {
                "username": user_id,
                "email": email,
                "password": settings.SECRET_KEY,
                "first_name": user_id,
                "last_name": user_id,
            }
        try:
            user = User.objects.create_user(**user)
            user.is_verified = True
            user.profile_pic = pic
            user.auth_provider = provider
            user.save()
        except:
            user["username"] = user["username"] + str(random.randint(0, 1000))
            user = User.objects.create_user(**user)
            user.is_verified = True
            user.profile_pic = pic
            user.auth_provider = provider
            user.save()
        profile_obj = UserProfile(email=user.email)
        profile_obj.save()
        return get_jwt_token(user)
