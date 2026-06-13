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


class TopicKeyword(models.Model):
    topic = models.CharField(max_length=100, db_index=True)
    keyword = models.CharField(max_length=120)
    weight = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['topic', 'keyword']
        ordering = ['topic', 'keyword']
        verbose_name = 'Topic keyword'
        verbose_name_plural = 'Topic keywords'

    def __str__(self):
        return f"{self.topic} <- '{self.keyword}' (x{self.weight})"


class TopicNote(models.Model):
    topic = models.CharField(max_length=100, unique=True, db_index=True)
    scheme_of_work = models.TextField(blank=True)
    lecture_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['topic']
        verbose_name = 'Topic note'
        verbose_name_plural = 'Topic notes'

    def __str__(self):
        return f"Note: {self.topic}"


class TopicLearningSession(models.Model):
    """
    Tracks a pupil's mastery-learning journey through their weak topics.
    Created automatically when a pupil finishes an adaptive session with weak topics.
    Implements Bloom's Mastery Learning (1968): the pupil must demonstrate mastery
    of one topic before advancing to the next.
    Topics are ordered easiest-to-fix first (Bandura, 1997 — self-efficacy through
    early success).
    """
    STATUS_CHOICES = [
        ('reading',  'Reading lecture note'),
        ('testing',  'Taking mini-test'),
        ('complete', 'All weak topics mastered'),
    ]

    pupil          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='learning_sessions')
    subject        = models.ForeignKey(Subject, on_delete=models.CASCADE)
    weak_topics    = models.JSONField(default=list)
    current_index  = models.PositiveIntegerField(default=0)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reading')
    wrong_question = models.ForeignKey(CEQuestion, on_delete=models.SET_NULL,
                                       null=True, blank=True)
    generated_note = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def current_topic(self):
        if self.current_index < len(self.weak_topics):
            return self.weak_topics[self.current_index]
        return None

    def advance(self):
        self.current_index += 1
        if self.current_index >= len(self.weak_topics):
            self.status = 'complete'
        else:
            self.status = 'reading'
        self.generated_note = ''
        self.wrong_question = None
        self.save()
        return self.status != 'complete'

    def __str__(self):
        return f"{self.pupil.username} — {self.subject.name} mastery session"


class MiniTestResult(models.Model):
    """
    Records each mini-test attempt within a TopicLearningSession.
    The mastery engine uses three signals to decide readiness to advance
    (Bloom, 1968; Lord, 1980):
      1. Accuracy >= 60%
      2. At least 3 consecutive correct answers
      3. At least 1 Medium-level question correct
    """
    session        = models.ForeignKey(TopicLearningSession, on_delete=models.CASCADE,
                                       related_name='mini_test_results')
    topic          = models.CharField(max_length=100)
    attempt_number = models.PositiveIntegerField(default=1)
    answers        = models.JSONField(default=list)
    score          = models.PositiveIntegerField(default=0)
    total          = models.PositiveIntegerField(default=5)
    passed         = models.BooleanField(default=False)
    taken_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['attempt_number']

    @property
    def accuracy(self):
        return round(self.score / self.total * 100) if self.total else 0

    def __str__(self):
        return f"{self.session.pupil.username} | {self.topic} | attempt {self.attempt_number} | {'PASS' if self.passed else 'FAIL'}"
