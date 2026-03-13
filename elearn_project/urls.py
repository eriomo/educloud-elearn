from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('lessons/', include('lessons.urls')),
    path('assessments/', include('assessments.urls')),
    path('assignments/', include('assignments.urls')),
    path('progress/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
