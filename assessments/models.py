from django.db import models
from django.conf import settings
from lessons.models import Subject, Lesson


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    DIFFICULTY_CHOICES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])
    order = models.PositiveIntegerField(default=0)
    difficulty_predicted = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES, default='medium', blank=True)
    topic = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question_text[:60]


class QuizResult(models.Model):
    pupil = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    total_questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField()
    answers_json = models.JSONField(default=dict, blank=True)
    ai_feedback = models.JSONField(default=dict, blank=True)
    date_taken = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_taken']

    def __str__(self):
        return f"{self.pupil} — {self.quiz} — {self.score}%"

    @property
    def percentage(self):
        return round((self.correct_answers / self.total_questions) * 100, 1) if self.total_questions else 0


class CEQuestion(models.Model):
    DIFFICULTY_CHOICES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='ce_questions')
    exam_year = models.PositiveIntegerField()
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])
    difficulty_level = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES, default='medium')
    difficulty_predicted = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES, default='', blank=True)
    topic = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['subject', 'exam_year']

    def __str__(self):
        return f"[{self.exam_year}] {self.question_text[:50]}"


class PracticeResult(models.Model):
    pupil = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practice_results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    total_questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField()
    answers_json = models.JSONField(default=dict, blank=True)
    ai_feedback = models.JSONField(default=dict, blank=True)
    date_attempted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_attempted']

    @property
    def percentage(self):
        return round((self.correct_answers / self.total_questions) * 100, 1) if self.total_questions else 0


class StudentWeakPoint(models.Model):
    """Tracks a student's performance per topic across all attempts"""
    pupil = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weak_points')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    total_attempted = models.PositiveIntegerField(default=0)
    total_correct = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['pupil', 'subject', 'topic']
        ordering = ['topic']

    @property
    def accuracy(self):
        return round((self.total_correct / self.total_attempted) * 100, 1) if self.total_attempted else 0

    @property
    def status(self):
        acc = self.accuracy
        if acc < 40:
            return 'weak'
        elif acc < 70:
            return 'needs_improvement'
        else:
            return 'strong'

    def __str__(self):
        return f"{self.pupil} | {self.topic} | {self.accuracy}%"
