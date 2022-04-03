# import uuid
# from django.db import models
# from django.contrib.auth import get_user_model


# STATE = (('public', '公開'), ('private', '非公開'))


# class TagModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=255)

#     def __str__(self):
#         return self.name


# class PostModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
#     post = models.TextField('投稿', max_length=255)
#     posted_by = models.ForeignKey(
#         get_user_model(), on_delete=models.CASCADE, related_name='posted_by')
#     is_public = models.CharField('公開・非公開', max_length=50, choices=STATE)
#     # is_public = models.BooleanField('公開可能か', default=False)
#     created_at = models.DateTimeField('登録日時', auto_now_add=True)
#     updated_at = models.DateTimeField('更新日時', auto_now=True)
#     tags = models.ManyToManyField(TagModel, blank=True, related_name='tags')
#     liked = models.ManyToManyField(
#         get_user_model(), blank=True, related_name='like')

#     class Meta:
#         ordering = ['-created_at', ]

#     def __str__(self):
#         return self.post


# class CommentModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     comment = models.CharField(max_length=200)
#     commented_by = models.ForeignKey(
#         get_user_model(), related_name='user_comment',
#         on_delete=models.CASCADE
#     )
#     commented_at = models.DateTimeField('登録日時', auto_now_add=True)
#     post = models.ForeignKey(
#         PostModel, on_delete=models.CASCADE, related_name='comment')

#     class Meta:
#         ordering = ['-commented_at', ]

#     def __str__(self):
#         return self.comment
