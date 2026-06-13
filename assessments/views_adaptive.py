# assessments/views_adaptive.py

import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from lessons.models import Subject
from .models import CEQuestion, PracticeResult, StudentWeakPoint

DIFF_BANDS = ['easy', 'medium', 'hard']

def _next_difficulty(score_float):
    if score_float < 0.65:
        return 'easy'
    if score_float < 1.35:
        return 'medium'
    return 'hard'


@login_required
def adaptive_home(request):
    # Use the correct related name: ce_questions (not ceQuestion)
    subjects = Subject.objects.filter(
        ce_questions__isnull=False
    ).distinct().order_by('name')

    for s in subjects:
        s.question_count = CEQuestion.objects.filter(subject=s).count()

    return render(request, 'assessments/adaptive_home.html', {'subjects': subjects})


@login_required
def adaptive_start(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)

    if CEQuestion.objects.filter(subject=subject).count() == 0:
        messages.error(request, f'No questions available for {subject.name} yet.')
        return redirect('adaptive_home')

    request.session['adaptive'] = {
        'subject_id': subject_id,
        'subject_name': subject.name,
        'score_float': 1.0,
        'score': 0,
        'total': 0,
        'asked_ids': [],
    }
    return redirect('adaptive_answer', subject_id=subject_id)


@login_required
def adaptive_answer(request, subject_id):
    session = request.session.get('adaptive')
    if not session or session.get('subject_id') != subject_id:
        return redirect('adaptive_start', subject_id=subject_id)

    subject = get_object_or_404(Subject, pk=subject_id)
    MAX_Q = 15

    # ── POST: process submitted answer ───────────────────────────────────────
    if request.method == 'POST':
        qid = int(request.POST.get('question_id', 0))
        user_answer = request.POST.get('answer', '').strip().upper()

        try:
            question = CEQuestion.objects.get(pk=qid)
        except CEQuestion.DoesNotExist:
            return redirect('adaptive_answer', subject_id=subject_id)

        correct = (user_answer == question.correct_option.upper())

        sf = session['score_float']
        sf = sf + 0.35 if correct else sf - 0.35
        sf = max(0.0, min(2.0, sf))

        topic = question.topic or 'General Mathematics'
        wp, _ = StudentWeakPoint.objects.get_or_create(
            pupil=request.user, subject=subject, topic=topic,
            defaults={'total_attempted': 0, 'total_correct': 0}
        )
        wp.total_attempted += 1
        if correct:
            wp.total_correct += 1
        wp.save()

        session['score_float'] = sf
        if correct:
            session['score'] = session.get('score', 0) + 1
        session['total'] = session.get('total', 0) + 1
        session['asked_ids'] = session.get('asked_ids', []) + [qid]
        request.session.modified = True

        if session['total'] >= MAX_Q:
            return _finish(request, subject, session)

        return redirect('adaptive_answer', subject_id=subject_id)

    # ── GET: show next question ───────────────────────────────────────────────
    if session.get('total', 0) >= MAX_Q:
        return _finish(request, subject, session)

    current_difficulty = _next_difficulty(session.get('score_float', 1.0))
    asked = session.get('asked_ids', [])

    qs = list(CEQuestion.objects.filter(
        subject=subject,
        difficulty_predicted=current_difficulty
    ).exclude(pk__in=asked))

    if not qs:
        qs = list(CEQuestion.objects.filter(subject=subject).exclude(pk__in=asked))
    if not qs:
        session['asked_ids'] = []
        request.session.modified = True
        qs = list(CEQuestion.objects.filter(subject=subject))

    if not qs:
        messages.error(request, 'No questions available for this subject.')
        return redirect('adaptive_home')

    question = random.choice(qs)
    choices = [
        ('A', question.option_a),
        ('B', question.option_b),
        ('C', question.option_c),
        ('D', question.option_d),
    ]

    return render(request, 'assessments/adaptive_question.html', {
        'question': question,
        'choices': choices,
        'session': session,
        'current_difficulty': current_difficulty,
        'subject': subject,
    })


def _finish(request, subject, session):
    score = session.get('score', 0)
    total = session.get('total', 0)
    pct = round(score / total * 100) if total else 0

    all_wps = StudentWeakPoint.objects.filter(
        pupil=request.user, subject=subject, total_attempted__gt=0
    ).order_by('topic')

    topic_data = []
    for wp in all_wps:
        acc = round(wp.total_correct / wp.total_attempted * 100)
        topic_data.append({'topic': wp.topic, 'accuracy': acc})

    weak   = [t for t in topic_data if t['accuracy'] < 40][:3]
    strong = [t for t in topic_data if t['accuracy'] >= 70][:3]

    study_plan = []
    for t in weak:
        study_plan.append(
            f"Revise {t['topic']} — your current accuracy is {t['accuracy']}%. Start with easy questions."
        )
    if not study_plan:
        study_plan.append('You are doing well across all topics. Try harder questions to push your score higher.')

    if 'adaptive' in request.session:
        del request.session['adaptive']

    return render(request, 'assessments/adaptive_result.html', {
        'score': score,
        'total': total,
        'percentage': pct,
        'subject_name': subject.name,
        'weak_topics': weak,
        'strong_topics': strong,
        'study_plan': study_plan,
    })
