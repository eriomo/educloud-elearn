from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('teacher', 'Teacher'),
        ('pupil', 'Pupil'),
        ('parent', 'Parent'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='pupil')
    class_level = models.PositiveIntegerField(null=True, blank=True, help_text="Primary 1-6")
    parent_link = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='children', limit_choices_to={'role': 'parent'},
        help_text="Link pupil to parent account"
    )
    avatar_color = models.CharField(max_length=7, default='#2B6B8A')

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_pupil(self):
        return self.role == 'pupil'

    @property
    def is_parent(self):
        return self.role == 'parent'
