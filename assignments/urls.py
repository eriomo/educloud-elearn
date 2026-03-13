from django.urls import path
from . import views

urlpatterns = [
    path('', views.assignment_list, name='assignment_list'),
    path('<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('create/', views.assignment_create, name='assignment_create'),
    path('<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
    path('grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
]
