import jwt
import datetime
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
# from accounts.models import User
from django.contrib.auth import get_user_model


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')
            id = decode_access_token(token)

            user = get_user_model().objects.get(pk=id)

            return (user, None)

        raise exceptions.AuthenticationFailed('unauthenticated')


def create_access_token(id, exp=30):
    return jwt.encode({
        'user_id': id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=exp),
        'iat': datetime.datetime.utcnow()
        # }, 'access_secret', algorithm='HS256')
    }, settings.SECRET_KEY, algorithm='HS256')


def decode_access_token(token):
    # print(token)
    try:
        # payload = jwt.decode(token, 'access_secret', algorithms='HS256')
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')

        return payload['user_id']
    except:
        raise exceptions.AuthenticationFailed('unauthenticated')


def create_refresh_token(id):
    return jwt.encode({
        'user_id': id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }, 'refresh_secret', algorithm='HS256')


def decode_refresh_token(token):
    try:
        payload = jwt.decode(token, 'refresh_secret', algorithms='HS256')

        return payload['user_id']
    except:
        raise exceptions.AuthenticationFailed('unauthenticated')
