"""
Seed the database with demo data for the defence presentation.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from accounts.models import User
from lessons.models import Subject, Lesson
from assessments.models import Quiz, Question, CEQuestion

class Command(BaseCommand):
    help = 'Seeds the database with demo data for the defence presentation'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # ── Create users ─────────────────────────────────
        admin = User.objects.create_superuser(
            username='admin', password='admin123',
            first_name='Admin', last_name='User', role='admin', email='admin@educloud.ng')

        teacher = User.objects.create_user(
            username='teacher1', password='teacher123',
            first_name='Mrs.', last_name='Adeyemi', role='teacher', email='adeyemi@educloud.ng')

        teacher2 = User.objects.create_user(
            username='teacher2', password='teacher123',
            first_name='Mr.', last_name='Okafor', role='teacher', email='okafor@educloud.ng')

        parent = User.objects.create_user(
            username='parent1', password='parent123',
            first_name='Mr.', last_name='Johnson', role='parent', email='johnson@educloud.ng')

        pupils = []
        pupil_names = [
            ('Adaeze', 'Obi', 3), ('Emeka', 'Nnamdi', 3), ('Fatima', 'Bello', 3),
            ('David', 'Johnson', 4), ('Grace', 'Adekunle', 4), ('Ibrahim', 'Musa', 4),
            ('Chioma', 'Eze', 5), ('Samuel', 'Oluwole', 5),
        ]
        for fname, lname, cls in pupil_names:
            p = User.objects.create_user(
                username=f'{fname.lower()}.{lname.lower()}', password='pupil123',
                first_name=fname, last_name=lname, role='pupil',
                class_level=cls, parent_link=parent if lname == 'Johnson' else None,
                avatar_color=['#2B6B8A','#E67E22','#27AE60','#8E44AD','#E74C3C','#3498DB','#1ABC9C','#F39C12'][len(pupils) % 8])
            pupils.append(p)

        self.stdout.write(f'  Created {len(pupils)} pupils, 2 teachers, 1 parent, 1 admin')

        # ── Create subjects ──────────────────────────────
        subject_data = [
            ('Mathematics', '#E74C3C'), ('English Studies', '#3498DB'),
            ('Basic Science', '#27AE60'), ('Social Studies', '#8E44AD'),
            ('General Knowledge', '#F39C12'), ('Quantitative Reasoning', '#1ABC9C'),
        ]
        subjects = {}
        for cls in range(1, 7):
            for name, color in subject_data:
                s = Subject.objects.create(name=name, class_level=cls, color=color)
                subjects[(name, cls)] = s

        self.stdout.write(f'  Created {Subject.objects.count()} subjects')

        # ── Create sample lessons ────────────────────────
        lesson_data = [
            ('Mathematics', 3, 'Addition and Subtraction of 3-Digit Numbers',
             'In this lesson, we will learn how to add and subtract numbers with three digits. '
             'Remember to always start from the ones column (the rightmost digit) and carry over '
             'when the sum is greater than 9.\n\nExample:\n  345 + 278 = 623\n  500 - 167 = 333\n\n'
             'Practice these steps: line up the numbers, add each column starting from the right, '
             'and carry over when needed.'),
            ('Mathematics', 3, 'Introduction to Multiplication',
             'Multiplication is a quick way of adding the same number many times. '
             'For example, 4 x 3 means adding 4 three times: 4 + 4 + 4 = 12.\n\n'
             'The multiplication table helps us remember these results quickly.'),
            ('English Studies', 3, 'Parts of Speech: Nouns and Pronouns',
             'A noun is a word that names a person, place, thing, or idea. '
             'Examples: teacher, school, book, happiness.\n\n'
             'A pronoun is a word used in place of a noun. '
             'Examples: he, she, it, they, we.\n\n'
             'Practice: Identify the nouns and pronouns in this sentence: '
             '"Mary gave her book to the teacher."'),
            ('English Studies', 4, 'Writing Composition: Descriptive Essays',
             'A descriptive essay paints a picture with words. When writing one:\n\n'
             '1. Choose your topic\n2. Use your five senses (sight, sound, smell, taste, touch)\n'
             '3. Use vivid adjectives and adverbs\n4. Organise your ideas in paragraphs\n\n'
             'Topic: "My School"\nThink about what you see, hear, and feel when you arrive at school each morning.'),
            ('Basic Science', 4, 'Living and Non-Living Things',
             'Living things have certain characteristics that non-living things do not have.\n\n'
             'Characteristics of living things:\n- They grow\n- They reproduce\n- They need food and water\n'
             '- They respond to their environment\n- They breathe\n\n'
             'Examples of living things: plants, animals, humans\n'
             'Examples of non-living things: stones, water, chairs'),
            ('Social Studies', 5, 'The Nigerian Government',
             'Nigeria is a federal republic with three levels of government:\n\n'
             '1. Federal Government (headed by the President)\n'
             '2. State Government (headed by the Governor)\n'
             '3. Local Government (headed by the Chairman)\n\n'
             'Each level has specific responsibilities to serve the people.'),
        ]

        for subj_name, cls, title, content in lesson_data:
            Lesson.objects.create(
                subject=subjects[(subj_name, cls)],
                topic_title=title, content_text=content,
                content_type='text', uploaded_by=teacher)

        self.stdout.write(f'  Created {Lesson.objects.count()} lessons')

        # ── Create sample quizzes ────────────────────────
        math_lesson = Lesson.objects.filter(topic_title__contains='Addition').first()
        if math_lesson:
            quiz = Quiz.objects.create(lesson=math_lesson, title='Addition & Subtraction Quiz', created_by=teacher)
            quiz_questions = [
                ('What is 345 + 278?', '613', '623', '633', '523', 'B'),
                ('What is 500 - 167?', '343', '333', '337', '367', 'B'),
                ('What is 129 + 371?', '490', '510', '500', '400', 'C'),
                ('What is 800 - 456?', '354', '344', '346', '364', 'B'),
                ('What is 250 + 750?', '900', '1000', '950', '1050', 'B'),
            ]
            for qt, a, b, c, d, correct in quiz_questions:
                Question.objects.create(quiz=quiz, question_text=qt,
                    option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct)

        eng_lesson = Lesson.objects.filter(topic_title__contains='Nouns').first()
        if eng_lesson:
            quiz = Quiz.objects.create(lesson=eng_lesson, title='Parts of Speech Quiz', created_by=teacher)
            eng_questions = [
                ('Which of these is a noun?', 'quickly', 'beautiful', 'school', 'running', 'C'),
                ('Which word is a pronoun?', 'table', 'she', 'happy', 'slowly', 'B'),
                ('"The dog chased its tail." What is the pronoun?', 'dog', 'chased', 'its', 'tail', 'C'),
                ('Which is a proper noun?', 'city', 'Lagos', 'river', 'country', 'B'),
            ]
            for qt, a, b, c, d, correct in eng_questions:
                Question.objects.create(quiz=quiz, question_text=qt,
                    option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct)

        self.stdout.write(f'  Created {Quiz.objects.count()} quizzes with {Question.objects.count()} questions')

        # ── Create sample CE past questions ──────────────
        ce_data = [
            ('Mathematics', 3, 2023, 'What is 15 x 4?', '50', '60', '55', '65', 'B', 'easy'),
            ('Mathematics', 3, 2023, 'If a boy has 48 oranges and shares equally among 6 friends, how many does each friend get?', '6', '7', '8', '9', 'C', 'medium'),
            ('Mathematics', 3, 2022, 'What is the next number in the sequence: 2, 4, 8, 16, __?', '24', '32', '20', '28', 'B', 'medium'),
            ('Mathematics', 3, 2022, 'What is 1/2 of 100?', '25', '75', '50', '40', 'C', 'easy'),
            ('English Studies', 3, 2023, 'Choose the correct spelling:', 'Beatiful', 'Beautiful', 'Beutiful', 'Beautful', 'B', 'easy'),
            ('English Studies', 3, 2023, 'Which is the past tense of "go"?', 'goed', 'going', 'went', 'gone', 'C', 'easy'),
            ('English Studies', 3, 2022, 'What is the plural of "child"?', 'childs', 'childrens', 'children', 'childes', 'C', 'easy'),
            ('General Knowledge', 3, 2023, 'What is the capital of Nigeria?', 'Lagos', 'Abuja', 'Kano', 'Port Harcourt', 'B', 'easy'),
            ('General Knowledge', 3, 2023, 'How many states are in Nigeria?', '30', '36', '24', '48', 'B', 'medium'),
            ('General Knowledge', 3, 2022, 'Which planet is closest to the Sun?', 'Venus', 'Earth', 'Mercury', 'Mars', 'C', 'medium'),
            ('Quantitative Reasoning', 3, 2023, 'If 3 + ? = 10, what is the missing number?', '5', '6', '7', '8', 'C', 'easy'),
            ('Quantitative Reasoning', 3, 2023, 'Complete the pattern: 5, 10, 15, 20, __', '22', '23', '25', '30', 'C', 'easy'),
        ]

        for subj_name, cls, year, qt, a, b, c, d, correct, diff in ce_data:
            CEQuestion.objects.create(
                subject=subjects[(subj_name, cls)], exam_year=year,
                question_text=qt, option_a=a, option_b=b, option_c=c, option_d=d,
                correct_option=correct, difficulty_level=diff)

        self.stdout.write(f'  Created {CEQuestion.objects.count()} common entrance questions')

        # ── Create some quiz results for demo ────────────
        from assessments.models import QuizResult, PracticeResult
        import random
        from django.utils import timezone
        from datetime import timedelta

        for pupil in pupils:
            for quiz in Quiz.objects.all():
                if random.random() > 0.3:
                    total = quiz.questions.count()
                    correct = random.randint(int(total * 0.4), total)
                    QuizResult.objects.create(
                        pupil=pupil, quiz=quiz, score=round((correct/total)*100, 2),
                        total_questions=total, correct_answers=correct,
                        date_taken=timezone.now() - timedelta(days=random.randint(1, 30)))

            for _ in range(random.randint(1, 4)):
                subj = random.choice(list(subjects.values()))
                total = random.randint(10, 20)
                correct = random.randint(int(total * 0.3), total)
                PracticeResult.objects.create(
                    pupil=pupil, subject=subj, score=round((correct/total)*100, 2),
                    total_questions=total, correct_answers=correct,
                    date_attempted=timezone.now() - timedelta(days=random.randint(1, 30)))

        self.stdout.write(self.style.SUCCESS(
            f'\nDatabase seeded successfully!\n\n'
            f'Login credentials:\n'
            f'  Admin:   admin / admin123\n'
            f'  Teacher: teacher1 / teacher123\n'
            f'  Parent:  parent1 / parent123\n'
            f'  Pupil:   adaeze.obi / pupil123\n'
            f'           emeka.nnamdi / pupil123\n'
            f'           david.johnson / pupil123\n'
        ))
