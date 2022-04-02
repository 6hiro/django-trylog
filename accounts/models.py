from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
# from rest_framework_simplejwt.tokens import RefreshToken
import uuid
import os


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('The given email must be set')

        # e-mail addressの正規化
        email = self.normalize_email(email)
        user = self.model(email=email)
        # passwordをハッシュ化してから設定
        user.set_password(password)
        # self._dbは、settings.pyで設定したdefaultのデータベース
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True

        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=50, unique=True)
    # ユーザー登録の確認メールのURLが押されると、is_verifiedがTrueになる。
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    # 登録時にユーザー名の代わりにメールアドレスを利用する
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()


class Reset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)


def upload_avatar_path(instance, filename):

    profile_avarar_name_0 = 'avatars/profile_{0}_0.jpg'.format(
        str(instance.id))
    profile_avarar_name_1 = 'avatars/profile_{0}_1.jpg'.format(
        str(instance.id))
    full_path_0 = os.path.join(settings.MEDIA_ROOT, profile_avarar_name_0)
    full_path_1 = os.path.join(settings.MEDIA_ROOT, profile_avarar_name_1)

    if os.path.exists(full_path_0):
        os.remove(full_path_0)
        return profile_avarar_name_1
    elif os.path.exists(full_path_1):
        os.remove(full_path_1)
        return profile_avarar_name_0
    else:
        return profile_avarar_name_0


class Profile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    nick_name = models.CharField(max_length=20)
    user = models.OneToOneField(
        get_user_model(), related_name='profile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(blank=True, null=True,
                            upload_to=upload_avatar_path)
    followers = models.ManyToManyField(
        get_user_model(), related_name="following", blank=True)
    bio = models.TextField(default="", blank=True, null=True)

    def __str__(self):
        return self.nick_name
