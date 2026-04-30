from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

DEFAULT_USERS = [
    {
        'username': 'admin',
        'password': 'Admin1234!',
        'email': 'admin@educloud.com',
        'role': 'admin',
        'is_superuser': True,
        'is_staff': True,
    },
    {
        'username': 'teacher1',
        'password': 'Teacher1234!',
        'email': 'teacher1@educloud.com',
        'role': 'teacher',
    },
    {
        'username': 'teacher2',
        'password': 'Teacher1234!',
        'email': 'teacher2@educloud.com',
        'role': 'teacher',
    },
    {
        'username': 'student1',
        'password': 'Student1234!',
        'email': 'student1@educloud.com',
        'role': 'pupil',
    },
    {
        'username': 'student2',
        'password': 'Student1234!',
        'email': 'student2@educloud.com',
        'role': 'pupil',
    },
    {
        'username': 'student3',
        'password': 'Student1234!',
        'email': 'student3@educloud.com',
        'role': 'pupil',
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
                    role=user_data.get('role', 'pupil'),
                )
                user.is_superuser = user_data.get('is_superuser', False)
                user.is_staff = user_data.get('is_staff', False)
                user.save()
                self.stdout.write(f'Created user: {username}')
            else:
                self.stdout.write(f'Already exists: {username}')
