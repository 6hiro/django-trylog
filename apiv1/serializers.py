from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.serializers import SerializerMethodField
from .authentication import (
    create_access_token,
    create_refresh_token,
)

from accounts.models import Profile
# from post.models import PostModel, TagModel, CommentModel
# from roadmap.models import RoadMapModel, StepModel, LookBackModel


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True, style={'input_type': 'password'}
    )

    class Meta:
        # get_user_modelは現在有効なユーザーモデル（今回はカスタムしたUserモデル）を取得できる
        model = get_user_model()
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=255, min_length=3, write_only=True)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = get_user_model().objects.get(email=obj['email'])

        return {
            'access_token': create_access_token(str(user.id)),
            'refresh_token': create_refresh_token(str(user.id))
        }

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        # if the given credentials are valid, return a User object.
        # if the given credentials are not valid, return None.
        user = auth.authenticate(email=email, password=password)

        if user is None:
            raise AuthenticationFailed('Invalid Credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        # 返り値は、serializer.validated_dataで確認できる？
        return {
            'email': user.email,
        }


class ProfileSerializer(serializers.ModelSerializer):
    following = SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'nick_name', 'user',
                  'created_at', 'img', 'followers', 'following')
        extra_kwargs = {'user': {'read_only': True}}

    def get_following(self, obj):

        if obj.user is None:
            return None
        else:
            following = Profile.objects.filter(
                followers=obj.user).values()
            following_list = []
            for i in range(len(following)):
                following_list.append(following[i]['user_id'])
            return following_list
