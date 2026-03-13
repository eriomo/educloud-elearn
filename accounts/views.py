from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserCreateForm
from .models import User
from lessons.models import Subject, Lesson
from assessments.models import Quiz, QuizResult, CEQuestion, PracticeResult
from assignments.models import Assignment, Submission
from django.db.models import Avg, Count


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    ctx = {'user': user}

    if user.is_pupil:
        subjects = Subject.objects.filter(class_level=user.class_level)
        recent_results = QuizResult.objects.filter(pupil=user).order_by('-date_taken')[:5]
        practice_results = PracticeResult.objects.filter(pupil=user).order_by('-date_attempted')[:5]
        pending_assignments = Assignment.objects.filter(
            class_level=user.class_level
        ).exclude(submissions__pupil=user)
        ctx.update({
            'subjects': subjects,
            'recent_results': recent_results,
            'practice_results': practice_results,
            'pending_assignments': pending_assignments,
        })
        return render(request, 'accounts/dashboard_pupil.html', ctx)

    elif user.is_teacher:
        subjects = Subject.objects.all()
        my_lessons = Lesson.objects.filter(uploaded_by=user).order_by('-date_uploaded')[:10]
        my_assignments = Assignment.objects.filter(teacher=user).order_by('-created_at')[:10]
        recent_submissions = Submission.objects.filter(
            assignment__teacher=user, is_graded=False
        ).order_by('-submitted_at')[:10]
        ctx.update({
            'subjects': subjects,
            'my_lessons': my_lessons,
            'my_assignments': my_assignments,
            'recent_submissions': recent_submissions,
        })
        return render(request, 'accounts/dashboard_teacher.html', ctx)

    elif user.is_parent:
        children = User.objects.filter(parent_link=user, role='pupil')
        children_data = []
        for child in children:
            avg_score = QuizResult.objects.filter(pupil=child).aggregate(avg=Avg('score'))['avg']
            practice_avg = PracticeResult.objects.filter(pupil=child).aggregate(avg=Avg('score'))['avg']
            recent = QuizResult.objects.filter(pupil=child).order_by('-date_taken')[:5]
            recent_practice = PracticeResult.objects.filter(pupil=child).order_by('-date_attempted')[:5]
            children_data.append({
                'child': child,
                'avg_score': avg_score,
                'practice_avg': practice_avg,
                'recent_results': recent,
                'recent_practice': recent_practice,
            })
        ctx['children_data'] = children_data
        return render(request, 'accounts/dashboard_parent.html', ctx)

    else:  # admin
        total_pupils = User.objects.filter(role='pupil').count()
        total_teachers = User.objects.filter(role='teacher').count()
        total_lessons = Lesson.objects.count()
        total_questions = CEQuestion.objects.count()
        ctx.update({
            'total_pupils': total_pupils,
            'total_teachers': total_teachers,
            'total_lessons': total_lessons,
            'total_questions': total_questions,
        })
        return render(request, 'accounts/dashboard_admin.html', ctx)


@login_required
def manage_users(request):
    if not (request.user.is_admin or request.user.is_superuser):
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('manage_users')
    else:
        form = UserCreateForm()
    users = User.objects.all().order_by('role', 'last_name')
    return render(request, 'accounts/manage_users.html', {'form': form, 'users': users})
