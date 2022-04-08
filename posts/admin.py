from django.contrib import admin
from .models import PostModel, TagModel, CommentModel


class PostModelAdmin(admin.ModelAdmin):
    list_display = ('post', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(PostModel, PostModelAdmin)
admin.site.register(TagModel)
admin.site.register(CommentModel)
