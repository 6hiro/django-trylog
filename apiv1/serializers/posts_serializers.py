from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.serializers import SerializerMethodField

from accounts.models import Profile
from posts.models import PostModel, TagModel, CommentModel
from .accounts_serializers import GetUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagModel
        fields = ['id', 'name']


class CreateUpdateDeletePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostModel
        fields = ['id', 'post', 'posted_by', 'liked', 'tags']
        extra_kwargs = {'posted_by': {'read_only': True}}

    def create(self, validated_data):
        tags = []
        # if validated_data.get('tags', None):
        #     validated_data.pop('tags')
        for word in validated_data['post'].split():
            if (word[0] == '#'):
                tag = TagModel.objects.filter(name=word[1:]).first()
                if tag:
                    tags.append(tag.pk)

                else:
                    tag = TagModel(name=word[1:])
                    tag.save()
                    tags.append(tag.pk)
        post = super().create(validated_data)
        post.tags.set(tags)
        return post


class GetParentPostSerializser(serializers.ModelSerializer):
    # post = SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    profile = SerializerMethodField()
    posted_by = GetUserSerializer(read_only=True)
    is_liked = SerializerMethodField()
    count_likes = SerializerMethodField()
    count_comments = SerializerMethodField()
    tags = TagSerializer(many=True)

    class Meta:
        model = PostModel
        fields = ['id', 'post', 'posted_by', 'profile', 'created_at', 'is_shared',
                  'is_liked', 'count_likes', 'count_comments', 'tags']
        extra_kwargs = {'posted_by': {'read_only': True}}

    def get_profile(self, instance):
        if instance.posted_by is None:
            return None

        profile = Profile.objects.get(user=instance.posted_by)

        img = profile.img
        if img:
            img_url = f"http://127.0.0.1:8000{settings.MEDIA_URL}{str(img)}"
        else:
            img_url = None

        return {
            'nick_name': str(profile.nick_name),
            'img': img_url
        }

    def get_is_liked(self, instance):
        # return None
        return instance.liked.filter(id=self.context.get('request').user.id).exists()

    def get_count_likes(self, instance):
        return instance.liked.count()

    def get_count_comments(self, instance):
        return instance.comment.count()


class GetPostSerializer(serializers.ModelSerializer):
    post = SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    profile = SerializerMethodField()
    posted_by = GetUserSerializer(read_only=True)
    is_liked = SerializerMethodField()
    count_likes = SerializerMethodField()
    count_comments = SerializerMethodField()

    tags = TagSerializer(many=True)

    parent = GetParentPostSerializser(read_only=True)

    class Meta:
        model = PostModel
        fields = ['id', 'post', 'posted_by', 'profile', 'created_at', 'is_shared',
                  'is_liked', 'count_likes', 'count_comments', 'tags', 'parent']
        extra_kwargs = {'posted_by': {'read_only': True}}

    def get_profile(self, instance):
        if instance.posted_by is None:
            return None

        profile = Profile.objects.get(user=instance.posted_by)

        img = profile.img
        if img:
            img_url = f"http://127.0.0.1:8000{settings.MEDIA_URL}{str(img)}"
        else:
            img_url = None

        return {
            'nick_name': str(profile.nick_name),
            'img': img_url
        }

    def get_post(self, instance):
        post = instance.post
        if instance.is_shared:
            post = instance.parent.post
        return post

    def get_is_liked(self, instance):
        # return None
        return instance.liked.filter(id=self.context.get('request').user.id).exists()

    def get_count_likes(self, instance):
        return instance.liked.count()

    def get_count_comments(self, instance):
        return instance.comment.count()


class CommentSerializer(serializers.ModelSerializer):
    commented_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M", read_only=True)
    profile = SerializerMethodField()
    commented_by = GetUserSerializer(read_only=True)

    class Meta:
        model = CommentModel
        fields = ['id', 'comment', 'commented_by',
                  'profile', 'commented_at', 'post']
        extra_kwargs = {'commented_by': {'read_only': True}}

    def get_profile(self, instance):
        if instance.commented_by is None:
            return None

        profile = Profile.objects.get(user=instance.commented_by)

        img = profile.img
        if img:
            img_url = f"http://127.0.0.1:8000{settings.MEDIA_URL}{str(img)}"
        else:
            img_url = None

        return {
            'nick_name': str(profile.nick_name),
            'img': img_url
        }
