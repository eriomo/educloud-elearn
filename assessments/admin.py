from django.contrib import admin
from .models import Quiz, Question, QuizResult, CEQuestion, PracticeResult

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'created_by', 'is_published')
    inlines = [QuestionInline]

@admin.register(CEQuestion)
class CEQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'subject', 'exam_year', 'difficulty_level', 'correct_option')
    list_filter = ('subject', 'exam_year', 'difficulty_level')

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('pupil', 'quiz', 'score', 'date_taken')

@admin.register(PracticeResult)
class PracticeResultAdmin(admin.ModelAdmin):
    list_display = ('pupil', 'subject', 'score', 'date_attempted')
