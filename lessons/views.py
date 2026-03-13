from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Subject, Lesson


@login_required
def subject_list(request):
    if request.user.is_pupil:
        subjects = Subject.objects.filter(class_level=request.user.class_level)
    else:
        subjects = Subject.objects.all()
    return render(request, 'lessons/subject_list.html', {'subjects': subjects})


@login_required
def lesson_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    lessons = subject.lessons.filter(is_published=True)
    return render(request, 'lessons/lesson_list.html', {'subject': subject, 'lessons': lessons})


@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    return render(request, 'lessons/lesson_detail.html', {'lesson': lesson})


@login_required
def lesson_create(request):
    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('dashboard')
    subjects = Subject.objects.all()
    if request.method == 'POST':
        subject = get_object_or_404(Subject, id=request.POST.get('subject'))
        lesson = Lesson.objects.create(
            subject=subject,
            topic_title=request.POST.get('topic_title', ''),
            content_text=request.POST.get('content_text', ''),
            content_type=request.POST.get('content_type', 'text'),
            content_file=request.FILES.get('content_file'),
            uploaded_by=request.user,
        )
        messages.success(request, f'Lesson "{lesson.topic_title}" created.')
        return redirect('lesson_list', subject_id=subject.id)
    return render(request, 'lessons/lesson_create.html', {'subjects': subjects})
