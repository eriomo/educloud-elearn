from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0001_initial'),
    ]

    operations = [
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
    ]
