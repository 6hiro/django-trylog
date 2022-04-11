import datetime
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.shortcuts import redirect
import jwt
import random
from rest_framework import generics, status, views, viewsets, exceptions, mixins
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header
from rest_framework.permissions import AllowAny, IsAuthenticated
import string

from accounts.models import (
    UserToken,
    Reset,
    Profile
)
from ..authentication import (
    create_access_token,
    decode_access_token,
    decode_refresh_token,
    JWTAuthentication
)
from ..permissions import (
    InOwnOrReadOnly,
    IsOwnProfileOrReadOnly
)
from ..serializers.accounts_serializers import (
    UserSerializer,
    GetUserSerializer,
    LoginSerializer,
    ProfileSerializer,
    ProfilesSerializer
)
from ..utils import Util


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data

            user = get_user_model().objects.get(email=user_data['email'])
            # token = RefreshToken.for_user(user).access_token
            token = create_access_token(str(user.id), exp=60*60*24)

            current_site = get_current_site(request).domain
            relativeLink = reverse('apiv1:email-verify')

            url = 'http://' + current_site + \
                relativeLink + "?token=" + str(token)
            email_body = user.username + \
                'さん、ご登録ありがとうございます。\nメールアドレスに間違いがなければ、以下のリンクからログインしてください。 \n' + url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'メールアドレスを確認してください'}
            Util.send_email(data)

            return Response(user_data, status=status.HTTP_201_CREATED)

        return Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(views.APIView):
    def get(self, request):

        token = request.query_params.get('token')

        try:
            user_id = decode_access_token(str(token))
            user = get_user_model().objects.get(id=user_id)
            if not user.is_verified:
                user.is_verified = True
                user.save()
                Profile.objects.create(user=user, nick_name='ななしさん')

            # return Response({'email': 'Succressfully activated'}, status=status.HTTP_200_OK)
            redirect_url = settings.FRONTEND_URL + "/auth/login"
            # redirect_url = 'http://localhost:3000'
            return redirect(redirect_url)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Acctivation Expired'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        serializers.is_valid()

        user = get_user_model().objects.get(email=request.data['email'])
        # print(serializers.data)
        # print(serializers.validated_data)

        UserToken.objects.create(
            user_id=str(user.id),
            token=serializers.data["tokens"]["refresh_token"],
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
        )

        response = Response()
        # httponly cookie
        response.set_cookie(
            key='refresh_token',
            value=serializers.data["tokens"]["refresh_token"],
            # max_age=60*60*24*7,
            httponly=True,
            secure=True,
            samesite='None'
        )
        response.data = {
            'token': serializers.data["tokens"]["access_token"]
        }

        return response
        # return Response(serializers.data, status=status.HTTP_200_OK)


class RefreshAPIView(views.APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        id = decode_refresh_token(str(refresh_token))
        # print(datetime.datetime.now(tz=datetime.timezone.utc))
        # print('########')
        # print(datetime.datetime.now(
        #     tz=datetime.timezone(datetime.timedelta(hours=+9), 'JST')
        # ))

        if not UserToken.objects.filter(
                user_id=id,
                token=refresh_token,
                expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)
                # expired_at__gt=datetime.datetime.now(
                #     tz=datetime.timezone(datetime.timedelta(hours=+9), 'JST')
                # )
        ).exists():
            raise exceptions.AuthenticationFailed('unauthenticated')

        access_token = create_access_token(str(id))
        return Response({
            'token': access_token
        })


class LogoutAPIView(views.APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        UserToken.objects.filter(token=refresh_token).delete()

        response = Response()
        response.delete_cookie(key='refresh_token')
        response.data = {
            'message': 'success'
        }

        return response


class ForgotAPIView(views.APIView):
    def post(self, request):
        email = request.data['email']
        token = ''.join(random.choice(string.ascii_lowercase +
                        string.digits) for _ in range(10))

        Reset.objects.create(
            email=email,
            token=token
        )

        url = settings.FRONTEND_URL + '/auth/reset-password/' + token

        email_body = 'パスワードをリセットする場合、以下のリンクをクリックしてください。 \n' + url
        data = {'email_body': email_body, 'to_email': email,
                'email_subject': 'パスワードリセット'}
        Util.send_email(data)

        return Response({
            'message': 'success'
        })


class ResetAPIView(views.APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        reset_password = Reset.objects.filter(token=data['token']).first()

        if not reset_password:
            raise exceptions.APIException('Invalid link!')

        user = get_user_model().objects.filter(email=reset_password.email).first()

        if not user:
            raise exceptions.APIException('User not found!')

        user.set_password(data['password'])
        user.save()

        # Resetオブジェクトを削除
        reset_password.delete()

        return Response({
            'message': 'success'
        })


class UserAPIView(views.APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        auth = get_authorization_header(request).split()
        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')
            id = decode_access_token(token)
            user = get_user_model().objects.get(id=id)
            if user:
                serializer = GetUserSerializer(user)
                return Response(serializer.data)

        raise exceptions.AuthenticationFailed('unauthenticated')


class UpdateUserAPIView(generics.UpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = GetUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (InOwnOrReadOnly, IsAuthenticated)


class DeleteUserAPIView(generics.DestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (InOwnOrReadOnly, IsAuthenticated)


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def get_following(request, id):
    following = Profile.objects.filter(followers=id)
    serializers = ProfilesSerializer(following, many=True)
    return Response(serializers.data)


@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def get_followers(request, id):
    user_id_list = Profile.objects.filter(
        id=id).first().followers.all().values_list('id', flat=True)
    followers = Profile.objects.filter(user_id__in=user_id_list)
    serializers = ProfilesSerializer(followers, many=True)
    return Response(serializers.data)


@api_view(['PUT'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsAuthenticated,))
def follow_user(request, id):
    # followする側のUser
    user = request.user
    try:
        # followされる側のUser
        user_to_follow = get_user_model().objects.get(id=id)
        # followされる側のUserのプロフィール（one to one の逆参照）
        user_to_follow_profile = user_to_follow.profile

        if user == user_to_follow:
            return Response({'result': 'You can not follow yourself'})

        if user in user_to_follow_profile.followers.all():
            user_to_follow_profile.followers.remove(user)
            user_to_follow_profile.save()
            return Response({'result': 'unfollow', 'unfollower': user.id, 'unfollowing': user_to_follow.id})
        else:
            user_to_follow_profile.followers.add(user)
            user_to_follow_profile.save()
            return Response({'result': 'follow', 'follower': user.id, 'following': user_to_follow.id})
    except Exception as e:
        message = {'detail': f'{e}'}
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsOwnProfileOrReadOnly,)
    lookup_field = 'user'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MyProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
