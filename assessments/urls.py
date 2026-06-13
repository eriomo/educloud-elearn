from django.urls import path
from . import views
from . import views_adaptive
from . import views_mastery

urlpatterns = [
    path('lesson/<int:lesson_id>/quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/result/<int:result_id>/', views.quiz_result, name='quiz_result'),
    path('lesson/<int:lesson_id>/quiz/create/', views.quiz_create, name='quiz_create'),
    path('common-entrance/', views.ce_subject_list, name='ce_subject_list'),
    path('common-entrance/practice/', views.ce_practice, name='ce_practice'),
    path('common-entrance/result/<int:result_id>/', views.ce_result, name='ce_result'),
    path('common-entrance/add/', views.ce_add_question, name='ce_add_question'),
    path('my-report/', views.student_report, name='student_report'),

    # Adaptive Practice
    path('adaptive/', views_adaptive.adaptive_home, name='adaptive_home'),
    path('adaptive/<int:subject_id>/start/', views_adaptive.adaptive_start, name='adaptive_start'),
    path('adaptive/<int:subject_id>/answer/', views_adaptive.adaptive_answer, name='adaptive_answer'),

    # Mastery Learning
    path('learn/', views_mastery.learn_start, name='learn_start'),
    path('learn/<int:session_id>/note/', views_mastery.learn_note, name='learn_note'),
    path('learn/<int:session_id>/test/', views_mastery.learn_test, name='learn_test'),
    path('learn/<int:session_id>/answer/', views_mastery.learn_answer, name='learn_answer'),
    path('learn/<int:session_id>/result/', views_mastery.learn_result, name='learn_result'),
]
