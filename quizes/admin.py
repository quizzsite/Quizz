from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Quiz, Question, Choice, Material, Topic

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Topic)

class MaterialAdmin(SummernoteModelAdmin):
    summernote_fields = ('text',)

admin.site.register(Material, MaterialAdmin)
