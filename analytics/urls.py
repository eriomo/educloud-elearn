from django.urls import path
from . import views

urlpatterns = [
    path('', views.progress_overview, name='progress_overview'),
    path('pupil/<int:pupil_id>/', views.pupil_detail, name='pupil_detail'),
    path('chart-data/', views.chart_data, name='chart_data_self'),
    path('chart-data/<int:pupil_id>/', views.chart_data, name='chart_data'),
]
