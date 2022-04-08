from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.serializers import SerializerMethodField

from accounts.models import Profile
from roadmaps.models import (
    RoadMapModel,
    StepModel,
    LookBackModel
)
from .accounts_serializers import GetUserSerializer


class RoadMapSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d", read_only=True)
    updated_at = serializers.DateTimeField(
        format="%Y-%m-%d", read_only=True)
    profile = SerializerMethodField()
    challenger = GetUserSerializer(read_only=True)

    class Meta:
        model = RoadMapModel
        fields = ['id', 'title', 'overview', 'challenger',
                  'is_public', 'created_at', 'updated_at',
                  'profile']
        extra_kwargs = {'challenger': {'read_only': True}}

    def get_profile(self, instance):
        if instance.challenger is None:
            return None

        profile = Profile.objects.get(user=instance.challenger)

        img = profile.img
        if img:
            img_url = f"http://127.0.0.1:8000{settings.MEDIA_URL}{str(img)}"
        else:
            img_url = None

        return {
            'nick_name': str(profile.nick_name),
            'img': img_url
        }


class StepSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    # roadmap = RoadMapSerializer(many=True)
    challenger = ReadOnlyField(source='roadmap.challenger.id')

    class Meta:
        model = StepModel
        fields = ['id', 'roadmap', 'challenger', 'to_learn', 'is_completed',
                  'order', 'created_at', 'updated_at']
        extra_kwargs = {'roadmap':  {'read_only': True},
                        'order':  {'read_only': True}}


class LookBackSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    # challenger = ReadOnlyField(source='step.roadmap.challenger.id')

    class Meta:
        model = LookBackModel
        fields = ['id', 'learned', 'step', 'created_at', 'updated_at']
        extra_kwargs = {'step':  {'read_only': True}}
