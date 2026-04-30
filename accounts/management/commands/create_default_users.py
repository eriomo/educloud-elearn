from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

DEFAULT_USERS = [
    {
        'username': 'admin',
        'password': 'Admin1234!',
        'email': 'admin@educloud.com',
        'is_superuser': True,
        'is_staff': True,
        'is_admin': True,
    },
    {
        'username': 'teacher1',
        'password': 'Teacher1234!',
        'email': 'teacher1@educloud.com',
        'is_teacher': True,
    },
    {
        'username': 'teacher2',
        'password': 'Teacher1234!',
        'email': 'teacher2@educloud.com',
        'is_teacher': True,
    },
    {
        'username': 'student1',
        'password': 'Student1234!',
        'email': 'student1@educloud.com',
        'is_pupil': True,
    },
    {
        'username': 'student2',
        'password': 'Student1234!',
        'email': 'student2@educloud.com',
        'is_pupil': True,
    },
    {
        'username': 'student3',
        'password': 'Student1234!',
        'email': 'student3@educloud.com',
        'is_pupil': True,
    },
]


class Command(BaseCommand):
    help = 'Creates default users if they do not exist'

    def handle(self, *args, **kwargs):
        for user_data in DEFAULT_USERS:
            username = user_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password=user_data['password'],
                    email=user_data.get('email', ''),
                )
                user.is_superuser = user_data.get('is_superuser', False)
                user.is_staff = user_data.get('is_staff', False)

                if hasattr(user, 'is_admin'):
                    user.is_admin = user_data.get('is_admin', False)
                if hasattr(user, 'is_teacher'):
                    user.is_teacher = user_data.get('is_teacher', False)
                if hasattr(user, 'is_pupil'):
                    user.is_pupil = user_data.get('is_pupil', False)

                user.save()
                self.stdout.write(f'Created user: {username}')
            else:
                self.stdout.write(f'User already exists: {username}')
