import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Quiz, Question, QuizResult, CEQuestion, PracticeResult
from lessons.models import Subject, Lesson


# ── Regular Quizzes ──────────────────────────────────────
@login_required
def quiz_list(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    quizzes = lesson.quizzes.filter(is_published=True)
    return render(request, 'assessments/quiz_list.html', {'lesson': lesson, 'quizzes': quizzes})


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    if request.method == 'POST':
        correct = 0
        total = questions.count()
        answers = {}
        for q in questions:
            selected = request.POST.get(f'q_{q.id}', '')
            answers[str(q.id)] = {
                'selected': selected,
                'correct': q.correct_option,
                'is_correct': selected == q.correct_option,
            }
            if selected == q.correct_option:
                correct += 1

        score = round((correct / total) * 100, 2) if total else 0
        result = QuizResult.objects.create(
            pupil=request.user, quiz=quiz, score=score,
            total_questions=total, correct_answers=correct, answers_json=answers,
        )
        return redirect('quiz_result', result_id=result.id)

    return render(request, 'assessments/take_quiz.html', {'quiz': quiz, 'questions': questions})


@login_required
def quiz_result(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id)
    questions = result.quiz.questions.all()
    return render(request, 'assessments/quiz_result.html', {'result': result, 'questions': questions})


# ── Quiz creation (teacher) ──────────────────────────────
@login_required
def quiz_create(request, lesson_id):
    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('dashboard')
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        quiz = Quiz.objects.create(
            lesson=lesson, title=request.POST.get('title', ''), created_by=request.user,
        )
        idx = 0
        while f'q_text_{idx}' in request.POST:
            Question.objects.create(
                quiz=quiz,
                question_text=request.POST.get(f'q_text_{idx}', ''),
                option_a=request.POST.get(f'q_a_{idx}', ''),
                option_b=request.POST.get(f'q_b_{idx}', ''),
                option_c=request.POST.get(f'q_c_{idx}', ''),
                option_d=request.POST.get(f'q_d_{idx}', ''),
                correct_option=request.POST.get(f'q_correct_{idx}', 'A'),
                order=idx,
            )
            idx += 1
        messages.success(request, f'Quiz "{quiz.title}" created with {idx} questions.')
        return redirect('lesson_detail', pk=lesson.id)

    return render(request, 'assessments/quiz_create.html', {'lesson': lesson})


# ── Common Entrance Practice ─────────────────────────────
@login_required
def ce_subject_list(request):
    subjects = Subject.objects.values('name').distinct()
    years = CEQuestion.objects.values_list('exam_year', flat=True).distinct().order_by('-exam_year')
    return render(request, 'assessments/ce_subject_list.html', {'subjects': subjects, 'years': years})


@login_required
def ce_practice(request):
    subject_name = request.GET.get('subject', '')
    year = request.GET.get('year', '')
    difficulty = request.GET.get('difficulty', '')

    qs = CEQuestion.objects.all()
    if subject_name:
        qs = qs.filter(subject__name=subject_name)
    if year:
        qs = qs.filter(exam_year=int(year))
    if difficulty:
        qs = qs.filter(difficulty_level=difficulty)

    questions = list(qs)
    random.shuffle(questions)
    questions = questions[:20]  # Max 20 per session

    if request.method == 'POST':
        correct = 0
        total = 0
        answers = {}
        q_ids = request.POST.getlist('question_ids')
        for qid in q_ids:
            q = CEQuestion.objects.filter(id=int(qid)).first()
            if not q:
                continue
            total += 1
            selected = request.POST.get(f'q_{qid}', '')
            is_correct = selected == q.correct_option
            answers[qid] = {
                'selected': selected,
                'correct': q.correct_option,
                'question': q.question_text[:80],
                'is_correct': is_correct,
            }
            if is_correct:
                correct += 1

        score = round((correct / total) * 100, 2) if total else 0
        subject_obj = CEQuestion.objects.filter(id=int(q_ids[0])).first().subject if q_ids else None
        result = PracticeResult.objects.create(
            pupil=request.user, subject=subject_obj, score=score,
            total_questions=total, correct_answers=correct, answers_json=answers,
        )
        return redirect('ce_result', result_id=result.id)

    return render(request, 'assessments/ce_practice.html', {
        'questions': questions,
        'subject_name': subject_name,
        'year': year,
        'difficulty': difficulty,
    })


@login_required
def ce_result(request, result_id):
    result = get_object_or_404(PracticeResult, id=result_id)
    return render(request, 'assessments/ce_result.html', {'result': result})


# ── CE question management (teacher/admin) ───────────────
@login_required
def ce_add_question(request):
    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('dashboard')
    subjects = Subject.objects.all()
    if request.method == 'POST':
        subject = get_object_or_404(Subject, id=request.POST.get('subject'))
        CEQuestion.objects.create(
            subject=subject,
            exam_year=int(request.POST.get('exam_year', 2024)),
            question_text=request.POST.get('question_text', ''),
            option_a=request.POST.get('option_a', ''),
            option_b=request.POST.get('option_b', ''),
            option_c=request.POST.get('option_c', ''),
            option_d=request.POST.get('option_d', ''),
            correct_option=request.POST.get('correct_option', 'A'),
            difficulty_level=request.POST.get('difficulty_level', 'medium'),
        )
        messages.success(request, 'Question added to the data bank.')
        return redirect('ce_add_question')
    return render(request, 'assessments/ce_add_question.html', {'subjects': subjects})
