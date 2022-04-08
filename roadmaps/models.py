import uuid
from django.db import models
from django.contrib.auth import get_user_model
# from datetime import date

STATE = (('public', '公開'), ('private', '非公開'))
PROGRESS = (('left_untouched', '未着手'), ('going', '途中'), ('is_completed', '完了'))


class RoadMapModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenger = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='roadmap')
    title = models.CharField('タイトル', max_length=60)
    overview = models.TextField('概要', max_length=250, null=True, blank=True)
    is_public = models.CharField(
        '公開・非公開', max_length=50, choices=STATE, default='private')
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['-created_at', ]

    def __str__(self):
        return self.title


class StepModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roadmap = models.ForeignKey(
        RoadMapModel, on_delete=models.CASCADE, related_name='step')
    to_learn = models.TextField('やること', max_length=100, blank=True, null=True)
    is_completed = models.CharField('進捗', max_length=50, choices=PROGRESS)
    order = models.IntegerField('順番')
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['order', ]

    def __str__(self):
        return self.to_learn


class LookBackModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step = models.ForeignKey(
        StepModel, on_delete=models.CASCADE, related_name='lookBack')
    learned = models.TextField(
        '学習したこと', max_length=2000, blank=True, null=True)
    # study_time = models.IntegerField('勉強時間')
    # study_at = models.DateField(default=date.today)
    created_at = models.DateTimeField('登録日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.learned
