from django.db import models
from django.conf import settings

class Subject(models.Model):
    name = models.CharField(max_length=100)
    class_level = models.PositiveIntegerField(help_text="Primary 1-6")
    icon = models.CharField(max_length=50, default='book', help_text="Icon name for display")
    color = models.CharField(max_length=7, default='#2B6B8A')

    class Meta:
        unique_together = ('name', 'class_level')
        ordering = ['class_level', 'name']

    def __str__(self):
        return f"{self.name} (Primary {self.class_level})"


class Lesson(models.Model):
    CONTENT_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    topic_title = models.CharField(max_length=200)
    content_text = models.TextField(blank=True)
    content_file = models.FileField(upload_to='lessons/', blank=True, null=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='text')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_uploaded']

    def __str__(self):
        return f"{self.topic_title} — {self.subject}"
