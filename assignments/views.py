from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission


@login_required
def assignment_list(request):
    if request.user.is_pupil:
        assignments = Assignment.objects.filter(class_level=request.user.class_level, is_published=True)
    elif request.user.is_teacher:
        assignments = Assignment.objects.filter(teacher=request.user)
    else:
        assignments = Assignment.objects.all()
    return render(request, 'assignments/assignment_list.html', {'assignments': assignments})


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submission = None
    if request.user.is_pupil:
        submission = Submission.objects.filter(assignment=assignment, pupil=request.user).first()
    submissions = assignment.submissions.all() if (request.user.is_teacher or request.user.is_admin) else None
    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment, 'submission': submission, 'submissions': submissions,
    })


@login_required
def assignment_create(request):
    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('dashboard')
    if request.method == 'POST':
        Assignment.objects.create(
            teacher=request.user,
            class_level=int(request.POST.get('class_level', 1)),
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            deadline=request.POST.get('deadline'),
        )
        messages.success(request, 'Assignment created.')
        return redirect('assignment_list')
    return render(request, 'assignments/assignment_create.html')


@login_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if not request.user.is_pupil:
        return redirect('dashboard')
    if request.method == 'POST':
        Submission.objects.update_or_create(
            assignment=assignment, pupil=request.user,
            defaults={'response_text': request.POST.get('response_text', '')},
        )
        messages.success(request, 'Assignment submitted.')
        return redirect('assignment_detail', pk=pk)
    return render(request, 'assignments/submit_assignment.html', {'assignment': assignment})


@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('dashboard')
    if request.method == 'POST':
        submission.grade = float(request.POST.get('grade', 0))
        submission.feedback = request.POST.get('feedback', '')
        submission.is_graded = True
        submission.save()
        messages.success(request, f'Graded submission by {submission.pupil.get_full_name()}.')
        return redirect('assignment_detail', pk=submission.assignment.pk)
    return render(request, 'assignments/grade_submission.html', {'submission': submission})
