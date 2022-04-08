from django.db.models import Q
from rest_framework import generics, status, viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from accounts.models import Profile
from roadmaps.models import (
    RoadMapModel,
    StepModel,
    LookBackModel
)
from ..authentication import (
    JWTAuthentication
)
from ..serializers.roadmaps_serializers import (
    RoadMapSerializer,
    StepSerializer,
    LookBackSerializer
)
from ..permissions import (
    IsOwnRoadmapOrReadOnly,
    IsOwnStepOrReadOnly,
    IsOwnLookBackOrReadOnly
)


class RoadMapViewSet(viewsets.ModelViewSet):
    queryset = RoadMapModel.objects.all()
    serializer_class = RoadMapSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated, IsOwnRoadmapOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(challenger=self.request.user)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return RoadMapModel.objects.filter(Q(is_public="public") | Q(challenger=self.request.user))
        return RoadMapModel.objects.filter(is_public="public")


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def roadmap_user(request, id):
    if request.user.id == id:
        roadmaps = RoadMapModel.objects.filter(challenger=request.user)
    else:
        roadmaps = RoadMapModel.objects.filter(
            challenger=id, is_public="public")
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(roadmaps, request)
    serializer = RoadMapSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# @api_view(['GET', 'POST'])
# @permission_classes((IsAuthenticated,))
# def get_followee_roadmap(request):
#     roadmaps = RoadMapModel.objects.filter(
#         challenger__in=request.data["follow"])
#     paginator = PageNumberPagination()
#     paginator.page_size = 10
#     result_page = paginator.paginate_queryset(roadmaps, request)
#     serializer = RoadMapSerializer(result_page, many=True)
#     return paginator.get_paginated_response(serializer.data)

class GetFollowUserRoadmap(generics.ListAPIView):
    serializer_class = RoadMapSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        # User = get_user_model().objects.get(id=self.request.user.id)
        following = Profile.objects.filter(followers=self.request.user)
        following_list = [str(i)
                          for i in following.values_list("user", flat=True)]
        return RoadMapModel.objects.filter(challenger__in=following_list)


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def roadmap_search(request, id):
    try:
        roadmaps = RoadMapModel.objects.filter(Q(title__contains=id, is_public="public") | Q(
            title__contains=id, challenger=request.user) | Q(overview__contains=id, is_public="public") | Q(
            overview__contains=id, challenger=request.user))
    except Exception as e:
        roadmaps = RoadMapModel.objects.filter(
            post__contains=id, is_public="public")
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(roadmaps, request)
    serializer = RoadMapSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


class StepViewSet(viewsets.ModelViewSet):
    queryset = StepModel.objects.all()
    serializer_class = StepSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated, IsOwnStepOrReadOnly,)

    def perform_create(self, serializer):
        roadmap = RoadMapModel.objects.get(id=self.request.data["roadmap"])
        steps = roadmap.step.all()
        order_list = [step.order for step in steps]
        max_order = max(order_list, default=0)
        serializer.save(
            roadmap=roadmap, order=(max_order+1))

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return StepModel.objects.filter(Q(roadmap__is_public="public") | Q(roadmap__challenger__id=self.request.user.id))
        return StepModel.objects.filter(roadmap__is_public="public")


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def steps(request, id):
    steps = StepModel.objects.filter(Q(roadmap__is_public="public") | Q(
        roadmap__challenger__id=request.user.id), roadmap__id=id)
    serializer = StepSerializer(steps, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def change_step_order(request):
    roadmap = RoadMapModel.objects.get(id=request.data[0]["roadmap"])

    if request.user == roadmap.challenger:
        serializer = StepSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        old_steps = StepModel.objects.filter(
            roadmap__id=request.data[0]["roadmap"])
        new_steps = request.data
        update_list = []
        for i in range(len(old_steps)):
            new_step = list(filter(lambda x: x["id"] ==
                                   str(old_steps[i].id), new_steps))[0]
            if old_steps[i].order != new_step["order"]:
                old_steps[i].order = new_step["order"]
                update_list.append(old_steps[i])

        StepModel.objects.bulk_update(update_list, fields=["order"])
        return Response(serializer.data)
    return Response(status=status.HTTP_403_FORBIDDEN)


class LookBackViewSet(viewsets.ModelViewSet):
    queryset = LookBackModel.objects.all()
    serializer_class = LookBackSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated, IsOwnLookBackOrReadOnly,)

    def perform_create(self, serializer):
        step = StepModel.objects.get(
            id=self.request.data["step"])
        serializer.save(step=step)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return LookBackModel.objects.filter(Q(step__roadmap__is_public="public") | Q(
                step__roadmap__challenger__id=self.request.user.id))
        return LookBackModel.objects.filter(step__roadmap__is_public="public")


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def lookbacks(request, id):
    lookbacks = LookBackModel.objects.filter(Q(step__roadmap__is_public="public") | Q(
        step__roadmap__challenger__id=request.user.id), step__id=id)
    serializer = LookBackSerializer(lookbacks, many=True)
    return Response(serializer.data)
