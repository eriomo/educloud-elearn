from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0005_topickeyword'),
        ('lessons', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(db_index=True, max_length=100, unique=True)),
                ('scheme_of_work', models.TextField(blank=True)),
                ('lecture_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['topic'], 'verbose_name': 'Topic note', 'verbose_name_plural': 'Topic notes'},
        ),
        migrations.CreateModel(
            name='TopicLearningSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weak_topics', models.JSONField(default=list)),
                ('current_index', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(
                    choices=[('reading','Reading lecture note'),('testing','Taking mini-test'),('complete','All weak topics mastered')],
                    default='reading', max_length=20)),
                ('generated_note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pupil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='learning_sessions', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    to='lessons.subject')),
                ('wrong_question', models.ForeignKey(blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL, to='assessments.cequestion')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='MiniTestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('attempt_number', models.PositiveIntegerField(default=1)),
                ('answers', models.JSONField(default=list)),
                ('score', models.PositiveIntegerField(default=0)),
                ('total', models.PositiveIntegerField(default=5)),
                ('passed', models.BooleanField(default=False)),
                ('taken_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='mini_test_results', to='assessments.topiclearningsession')),
            ],
            options={'ordering': ['attempt_number']},
        ),
    ]
