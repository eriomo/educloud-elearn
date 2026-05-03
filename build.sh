#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser --noinput || true
python manage.py create_default_users
python manage.py train_difficulty_model || echo "Model training skipped - will retry on next deploy"
python manage.py load_sample_questions || echo "Questions already loaded"
