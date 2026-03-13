from django.contrib import admin
from .models import Assignment, Submission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'class_level', 'deadline', 'is_published')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('pupil', 'assignment', 'submitted_at', 'is_graded', 'grade')
