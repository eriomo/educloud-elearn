from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Count, F
from accounts.models import User
from assessments.models import QuizResult, PracticeResult
from lessons.models import Subject
from assignments.models import Submission


@login_required
def progress_overview(request):
    """Progress dashboard for the logged-in pupil, or teacher/admin class overview."""
    user = request.user

    if user.is_pupil:
        quiz_results = QuizResult.objects.filter(pupil=user)
        practice_results = PracticeResult.objects.filter(pupil=user)
        subjects = Subject.objects.filter(class_level=user.class_level)

        subject_scores = []
        for subj in subjects:
            quiz_avg = quiz_results.filter(quiz__lesson__subject=subj).aggregate(avg=Avg('score'))['avg']
            practice_avg = practice_results.filter(subject=subj).aggregate(avg=Avg('score'))['avg']
            subject_scores.append({
                'subject': subj,
                'quiz_avg': round(quiz_avg or 0, 1),
                'practice_avg': round(practice_avg or 0, 1),
                'quiz_count': quiz_results.filter(quiz__lesson__subject=subj).count(),
                'practice_count': practice_results.filter(subject=subj).count(),
            })

        graded_submissions = Submission.objects.filter(pupil=user, is_graded=True)
        return render(request, 'analytics/progress_pupil.html', {
            'subject_scores': subject_scores,
            'quiz_results': quiz_results[:20],
            'practice_results': practice_results[:20],
            'graded_submissions': graded_submissions,
            'total_quizzes': quiz_results.count(),
            'total_practice': practice_results.count(),
            'overall_avg': quiz_results.aggregate(avg=Avg('score'))['avg'] or 0,
        })

    elif user.is_teacher or user.is_admin:
        class_level = int(request.GET.get('class', 1))
        pupils = User.objects.filter(role='pupil', class_level=class_level)
        pupil_data = []
        for p in pupils:
            avg = QuizResult.objects.filter(pupil=p).aggregate(avg=Avg('score'))['avg']
            practice_avg = PracticeResult.objects.filter(pupil=p).aggregate(avg=Avg('score'))['avg']
            pupil_data.append({
                'pupil': p,
                'quiz_avg': round(avg or 0, 1),
                'practice_avg': round(practice_avg or 0, 1),
                'quiz_count': QuizResult.objects.filter(pupil=p).count(),
            })
        return render(request, 'analytics/progress_teacher.html', {
            'pupil_data': pupil_data,
            'class_level': class_level,
        })

    return render(request, 'analytics/progress_pupil.html', {})


@login_required
def pupil_detail(request, pupil_id):
    """Teacher/admin view of a specific pupil's detailed progress."""
    if not (request.user.is_teacher or request.user.is_admin or request.user.is_parent):
        return render(request, 'accounts/dashboard_pupil.html')
    pupil = get_object_or_404(User, id=pupil_id, role='pupil')
    quiz_results = QuizResult.objects.filter(pupil=pupil).order_by('-date_taken')
    practice_results = PracticeResult.objects.filter(pupil=pupil).order_by('-date_attempted')
    subjects = Subject.objects.filter(class_level=pupil.class_level)

    subject_scores = []
    for subj in subjects:
        q_avg = quiz_results.filter(quiz__lesson__subject=subj).aggregate(avg=Avg('score'))['avg']
        p_avg = practice_results.filter(subject=subj).aggregate(avg=Avg('score'))['avg']
        subject_scores.append({
            'subject': subj,
            'quiz_avg': round(q_avg or 0, 1),
            'practice_avg': round(p_avg or 0, 1),
        })

    return render(request, 'analytics/pupil_detail.html', {
        'pupil': pupil,
        'quiz_results': quiz_results[:20],
        'practice_results': practice_results[:20],
        'subject_scores': subject_scores,
    })


@login_required
def chart_data(request, pupil_id=None):
    """JSON endpoint for Chart.js graphs."""
    target = get_object_or_404(User, id=pupil_id) if pupil_id else request.user
    results = QuizResult.objects.filter(pupil=target).order_by('date_taken')[:30]
    practice = PracticeResult.objects.filter(pupil=target).order_by('date_attempted')[:30]
    return JsonResponse({
        'quiz_labels': [r.date_taken.strftime('%d %b') for r in results],
        'quiz_scores': [float(r.score) for r in results],
        'practice_labels': [r.date_attempted.strftime('%d %b') for r in practice],
        'practice_scores': [float(r.score) for r in practice],
    })
