#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_default_users || echo "Users already exist"
python manage.py seed_topic_keywords || echo "Topic keywords already seeded"
python manage.py load_sample_questions || echo "Questions already loaded"
python manage.py train_difficulty_model || echo "Model training skipped"
