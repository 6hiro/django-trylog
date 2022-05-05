import json
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime
from rest_framework import response
from rest_framework.test import APITestCase
from posts.models import PostModel, TagModel
from roadmaps.models import RoadMapModel, StepModel, LookBackModel
from accounts.models import Profile
# from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from ..authentication import (
    create_access_token,
    decode_access_token,
    decode_refresh_token,
    JWTAuthentication
)


class TestRegisterLogin(APITestCase):
    REGISTER_URL = "/api/v1/register/"
    LOGIN_URL = "/api/v1/login/"

    data = {
        "username": "username",
        "email": "demo@demo.demo",
        "password": "registration",
        "password_confirm": "registration"
    }

    def test_registration_success(self):
        response = self.client.post(
            self.REGISTER_URL, self.data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_user_cannot_login_with_unverified(self):
        self.client.post(self.REGISTER_URL, self.data, format="json")
        response = self.client.post(self.LOGIN_URL, self.data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_user_can_login_after_verification(self):
        res = self.client.post(self.REGISTER_URL, self.data, format="json")
        email = res.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()

        response = self.client.post(self.LOGIN_URL, self.data, format="json")
        self.assertEqual(response.status_code, 200)


class TestProfileViewSet(APITestCase):
    PROFILE_URL = "/api/v1/profile/"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="username",
            email="demo@demo.demo",
            password="registration",
        )

    def test_create_success(self):
        user = get_user_model().objects.get(username="username")
        token = create_access_token(str(user.id))
        # response = self.client.get(self.TARGET_URL, HTTP_AUTHORIZATION='JWT {}'.format(token))
        self.client.credentials(HTTP_AUTHORIZATION="Beaer " + token)
        # self.client.force_authenticate(user=self.user)
        params = {
            'nick_name': 'nanashi'
        }

        response = self.client.post(self.PROFILE_URL, params, format='json')
        # print(response.content)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(response.status_code, 201)

    def test_get_detail_success(self):
        user = get_user_model().objects.get(username="username")
        token = create_access_token(str(user.id))
        self.client.credentials(HTTP_AUTHORIZATION="Beaer " + token)

        Profile.objects.create(
            user=self.user,
            nick_name='nanashi'
        )
        response = self.client.get(self.PROFILE_URL+str(self.user.id)+'/')
        # print(response.content)
        self.assertEqual(response.status_code, 200)


class TestMyProfileListView(APITestCase):
    PROFILE_URL = "/api/v1/myprofile/"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="username",
            email="test@test.test",
            password="testpassword"
        )

    def test_get_my_profile_success(self):
        Profile.objects.create(
            user=self.user,
            nick_name='nanashi'
        )
        user = get_user_model().objects.get(username="username")
        token = create_access_token(str(user.id))
        self.client.credentials(HTTP_AUTHORIZATION="Beaer " + token)
        response = self.client.get(self.PROFILE_URL)
        self.assertEqual(response.status_code, 200)
        # print(response.content)
        content = json.loads(response.content)
        # print(content)
        # self.assertEqual(content["results"][0]["nickName"], 'nanashi')
        self.assertEqual(content[0]["nickName"], 'nanashi')


class TestFollowUser(APITestCase):
    TARGET_URL = "/api/v1/follow/"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="username",
            email="test@test.test",
            password="testpassword"
        )
        cls.followedUser = get_user_model().objects.create_user(
            username="followedUser",
            email="followed@followed.followed",
            password="testpassword"
        )
        cls.userProfile = Profile.objects.create(
            user=cls.user,
            nick_name='nanashi'
        )
        cls.followedUserProfile = Profile.objects.create(
            user=cls.followedUser,
            nick_name='followed'
        )

    def test_follow_user_success(self):
        user = get_user_model().objects.get(username="username")
        token = create_access_token(str(user.id))
        # print(token)
        self.client.credentials(HTTP_AUTHORIZATION="Beaer " + token)
        response = self.client.put(
            self.TARGET_URL + str(self.followedUser.id) + "/", {}, format='json')
        # print(self.TARGET_URL + str(self.followedUser.id))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        # print(content)

        self.assertEqual(content["follower"], str(self.user.id))
        self.assertEqual(content["following"], str(self.followedUser.id))

    def test_follow_myself_error(self):
        user = get_user_model().objects.get(username="username")
        token = create_access_token(str(user.id))
        self.client.credentials(HTTP_AUTHORIZATION="Beaer " + token)
        response = self.client.put(
            self.TARGET_URL + str(self.user.id) + '/', {}, format='json')
        # print(response.status_code)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content["result"], 'You can not follow yourself')


class TestCreateUpdateDeletePostView(APITestCase):
    TARGET_URL = "/api/v1/create_update_delete_post/"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="username",
            email="test@test.test",
            password="testpassword"
        )

    def test_create_success(self):
        Profile.objects.create(
            user=self.user,
            nick_name='nanashi'
        )
        user = get_user_model().objects.get(username="username")
        token = create_access_token(str(user.id))
        self.client.credentials(HTTP_AUTHORIZATION="Beaer " + token)

        params = {
            'post': 'test #test',
        }

        response = self.client.post(self.TARGET_URL, params, format='json')
        # print(response.content)
        self.assertEqual(PostModel.objects.count(), 1)
        self.assertEqual(response.status_code, 201)
        post = PostModel.objects.get()
        content = json.loads(response.content)
        # print(content)
        self.assertEqual(content["post"], post.post)
        self.assertEqual(content["id"], str(post.id))

    # def test_create_bad_request(self):
    #     token = str(RefreshToken.for_user(self.user).access_token)
    #     self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
    #     params = {
    #         'post': '',
    #     }
    #     response = self.client.post(self.TARGET_URL, params, format='json')
    #     self.assertEqual(PostModel.objects.count(), 0)
    #     self.assertEqual(response.status_code, 400)


class TestRoadMapViewSet(APITestCase):

    ROADMAP_URL = "/api/v1/roadmap/"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="username",
            email="test@test.test",
            password="testpassword"
        )

    def test_create_success(self):
        Profile.objects.create(
            user=self.user,
            nick_name='nanashi'
        )
        user = get_user_model().objects.get(username="username")
        token = create_access_token(str(user.id))
        self.client.credentials(HTTP_AUTHORIZATION="Beaer " + token)
        params = {
            'title': 'demo_title',
            'overview': 'demo_overview',
            'is_public': 'public'
        }
        response = self.client.post(self.ROADMAP_URL, params, format='json')
        self.assertEqual(RoadMapModel.objects.count(), 1)
        self.assertEqual(response.status_code, 201)
        roadmap = RoadMapModel.objects.get()

        content = json.loads(response.content)
        self.assertEqual(content["title"], roadmap.title)
        self.assertEqual(content["isPublic"], roadmap.is_public)
        self.assertEqual(content["id"], str(roadmap.id))

    def test_create_bad_request(self):
        user = get_user_model().objects.get(username="username")
        token = create_access_token(str(user.id))
        self.client.credentials(HTTP_AUTHORIZATION="Beaer " + token)
        params = {
            'title': '',
            'overview': 'demo_overview',
            'is_public': 'public',
        }
        response = self.client.post(self.ROADMAP_URL, params, format='json')
        self.assertEqual(PostModel.objects.count(), 0)
        self.assertEqual(response.status_code, 400)
