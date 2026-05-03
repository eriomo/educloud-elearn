from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cequestion',
            name='difficulty_predicted',
            field=models.CharField(blank=True, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='', max_length=6),
        ),
        migrations.AddField(
            model_name='cequestion',
            name='topic',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='question',
            name='difficulty_predicted',
            field=models.CharField(blank=True, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium', max_length=6),
        ),
        migrations.AddField(
            model_name='question',
            name='topic',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='ai_feedback',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='practiceresult',
            name='ai_feedback',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.CreateModel(
            name='StudentWeakPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('total_attempted', models.PositiveIntegerField(default=0)),
                ('total_correct', models.PositiveIntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('pupil', models.ForeignKey(on_delete=models.CASCADE, related_name='weak_points', to='accounts.user')),
                ('subject', models.ForeignKey(on_delete=models.CASCADE, to='lessons.subject')),
            ],
            options={
                'ordering': ['topic'],
                'unique_together': {('pupil', 'subject', 'topic')},
            },
        ),
    ]
