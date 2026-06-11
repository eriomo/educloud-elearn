from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0003_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(db_index=True, max_length=100)),
                ('keyword', models.CharField(max_length=120)),
                ('weight', models.PositiveIntegerField(default=1, help_text='How strongly this keyword points to the topic (1 = normal, 2 = strong, 3 = very strong).')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Topic keyword',
                'verbose_name_plural': 'Topic keywords',
                'ordering': ['topic', 'keyword'],
                'unique_together': {('topic', 'keyword')},
            },
        ),
    ]
