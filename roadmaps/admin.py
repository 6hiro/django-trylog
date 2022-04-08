from django.contrib import admin
from .models import RoadMapModel, StepModel, LookBackModel


class RoadMapAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('challenger', 'created_at', 'updated_at')


admin.site.register(RoadMapModel, RoadMapAdmin)
admin.site.register(StepModel)
admin.site.register(LookBackModel)
