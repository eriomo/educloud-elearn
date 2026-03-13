from django.db import models
from django.conf import settings

class Assignment(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assignments')
    class_level = models.PositiveIntegerField(help_text="Primary 1-6")
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (P{self.class_level})"

    @property
    def submission_count(self):
        return self.submissions.count()


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    pupil = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    response_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_graded = models.BooleanField(default=False)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'pupil')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.pupil} — {self.assignment.title}"
