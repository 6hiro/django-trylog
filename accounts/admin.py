from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from . import models


class UserAdmin(BaseUserAdmin):
    # リストページの並び順
    ordering = ['date_joined']
    # Userのリストページのに表示する項目
    list_display = ['email', 'date_joined', 'username']
    # Userの詳細ページのレイアウト
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        (_('Personal Info'), {'fields': ()}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_verified'
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    # Userの追加ページのレイアウト
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserToken)
admin.site.register(models.Reset)
admin.site.register(models.Profile)
