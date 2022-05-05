from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Profile


class UserModelTests(TestCase):

    def test_is_empty(self):
        """初期状態では何も登録されていないことをチェック"""
        saved_posts = get_user_model().objects.all()
        self.assertEqual(saved_posts.count(), 0)

    def test_is_count_one(self):
        """1つレコードを適当に作成すると、レコードが1つだけカウントされることをテスト"""
        user = get_user_model().objects.create_user(
            username="username",
            email="test@test.test",
            password="testpassword"
        )
        user.save()
        saved_posts = get_user_model().objects.all()
        self.assertEqual(saved_posts.count(), 1)

    def test_saving_and_retrieving_post(self):
        """内容を指定してデータを保存し、すぐに取り出した時に保存した時と同じ値が返されることをテスト"""
        user = get_user_model().objects.create_user(
            username="username",
            email="test@test.test",
            password="testpassword"
        )
        user.save()

        saved_users = get_user_model().objects.all()
        actual_user = saved_users[0]

        self.assertEqual(actual_user.username, "username")
        self.assertEqual(actual_user.email, "test@test.test")
        # .check_password(password_to_check) will return True if the password is correct.
        self.assertEqual(actual_user.check_password("testpassword"), True)
