from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:subject_id>/lessons/', views.lesson_list, name='lesson_list'),
    path('lesson/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/create/', views.lesson_create, name='lesson_create'),
]
