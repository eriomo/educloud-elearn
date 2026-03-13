from django.contrib import admin
from .models import Subject, Lesson

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_level', 'color')
    list_filter = ('class_level',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('topic_title', 'subject', 'content_type', 'uploaded_by', 'date_uploaded')
    list_filter = ('subject__class_level', 'content_type')
