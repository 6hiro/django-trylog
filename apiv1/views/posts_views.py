from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from accounts.models import Profile
from posts.models import (
    PostModel,
    CommentModel
)
from ..authentication import (
    JWTAuthentication
)
from ..serializers.accounts_serializers import ProfilesSerializer
from ..serializers.posts_serializers import (
    CreateUpdateDeletePostSerializer,
    GetPostSerializer,
    CommentSerializer
)
from ..permissions import IsOwnPostOrReadOnly


class CreateUpdateDeletePostView(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = PostModel.objects.all()
    serializer_class = CreateUpdateDeletePostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsOwnPostOrReadOnly, IsAuthenticated)

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class GetPostView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = PostModel.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    # queryset = PostModel.objects.filter(is_public="public")
    serializer_class = GetPostSerializer
    # permission_classes = (IsOwnPostOrReadOnly,)


class GetPostListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = PostModel.objects.filter(parent=None)
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    # queryset = PostModel.objects.filter(is_public="public")
    serializer_class = GetPostSerializer
    # permission_classes = (IsOwnPostOrReadOnly,)
    # def get_queryset(self):
    #     if self.request.user.is_authenticated:
    #         return PostModel.objects.filter(Q(is_public="public") | Q(posted_by=self.request.user))
    #     return PostModel.objects.filter(is_public="public")


@api_view(['POST'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def share_post(request, post_id):
    parent_obj = PostModel.objects.filter(id=post_id).first()
    new_post = PostModel.objects.create(
        posted_by=request.user, parent=parent_obj)
    serializer = GetPostSerializer(new_post, context={'request': request})
    return Response(serializer.data, status=200)


@api_view(['POST'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def unshare_post(request, post_id):
    parent_obj = PostModel.objects.filter(id=post_id).first()
    if parent_obj.posted_by == request.user:
        parent_obj.delete()
        return Response({'result': 'unshare', 'post_id': post_id}, status=200)
    return Response({'result': 'failed'})


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def post_user(request, id):
    # if request.user.id == id:
    #     posts = get_user_model().objects.get(id=id).posted_by.all()
    # else:
    #     posts = get_user_model().objects.get(id=id).posted_by.filter(is_public="public")
    posts = get_user_model().objects.get(id=id).posted_by.all()

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = GetPostSerializer(
        result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# @api_view(['GET', 'POST'])
# @permission_classes((IsAuthenticated,))
# def get_followee_post(request):
#     posts = PostModel.objects.filter(posted_by__in=request.data["follow"])
#     paginator = PageNumberPagination()
#     paginator.page_size = 10
#     result_page = paginator.paginate_queryset(posts, request)
#     serializer = GetPostSerializer(result_page, many=True)
#     return paginator.get_paginated_response(serializer.data)


class GetFollowUserPost(generics.ListAPIView):
    serializer_class = GetPostSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        # User = get_user_model().objects.get(id=self.request.user.id)
        following = Profile.objects.filter(followers=self.request.user)
        following_list = [str(i)
                          for i in following.values_list("user", flat=True)]
        return PostModel.objects.filter(posted_by__in=following_list)


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def post_search(request, id):
    # try:
    #     posts = PostModel.objects.filter(Q(post__contains=id, is_public="public") | Q(
    #         post__contains=id, posted_by=request.user))
    # except Exception as e:
    #     posts = PostModel.objects.filter(post__contains=id, is_public="public")
    posts = PostModel.objects.filter(post__contains=id)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = GetPostSerializer(
        result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def post_hashtag(request, id):
    posts = PostModel.objects.filter(tags=id)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = GetPostSerializer(
        result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def like_post(request, id):
    # いいねをするもしくは外すUser
    user = request.user
    try:
        # いいねされるまたは外されるPost
        post_to_like = PostModel.objects.get(id=id)

        if user in post_to_like.liked.all():
            post_to_like.liked.remove(user)
            post_to_like.save()

            return Response({'result': 'unlike', 'post': post_to_like.id, 'unliked_by': user.id})
        else:
            post_to_like.liked.add(user)
            post_to_like.save()
            return Response({'result': 'like', 'post': post_to_like.id, 'liked_by': user.id})
    except Exception as e:
        message = {'detail': f'{e}'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def get_profiles_like_post(request, id):
    # liked_by = Profile.objects.filter(user_id__in=request.data["liked_by"])
    user_id_list = PostModel.objects.filter(
        id=id).first().liked.all().values_list('id', flat=True)
    profiles_liked = Profile.objects.filter(user_id__in=user_id_list)
    serializer = ProfilesSerializer(profiles_liked, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def get_favorite_post(request, id):
    posts = PostModel.objects.filter(liked=id)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = GetPostSerializer(
        result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def comments(request, id):
    comments = CommentModel.objects.filter(post=id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    queryset = CommentModel.objects.all()
    serializer_class = CommentSerializer
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(commented_by=self.request.user)
