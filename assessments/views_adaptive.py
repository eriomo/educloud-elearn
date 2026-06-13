# assessments/views_adaptive.py

import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg

from lessons.models import Subject
from .models import CEQuestion, StudentWeakPoint


def _score_to_difficulty(score_float):
    if score_float < 0.65:
        return 'easy'
    if score_float < 1.35:
        return 'medium'
    return 'hard'


def _pick_question(subject, difficulty, asked_ids, weak_topics):
    """
    Pick the next question. Priority:
    1. Unseen question in a weak topic at the current difficulty
    2. Any unseen question at the current difficulty
    3. Any unseen question (any difficulty) — fallback
    4. Reset asked list and start over if everything seen
    """
    base_qs = CEQuestion.objects.filter(subject=subject).exclude(pk__in=asked_ids)

    # Priority 1 — weak topic + correct difficulty
    if weak_topics:
        qs = list(base_qs.filter(difficulty_predicted=difficulty, topic__in=weak_topics))
        if qs:
            return random.choice(qs)

    # Priority 2 — correct difficulty, any topic
    qs = list(base_qs.filter(difficulty_predicted=difficulty))
    if qs:
        return random.choice(qs)

    # Priority 3 — any difficulty, any topic
    qs = list(base_qs)
    if qs:
        return random.choice(qs)

    # Priority 4 — all seen, reset
    return None  # caller handles reset


@login_required
def adaptive_home(request):
    subjects_qs = (
        Subject.objects
        .filter(ce_questions__isnull=False)
        .annotate(question_count=Count('ce_questions'))
        .order_by('name', '-question_count')
    )
    # One card per subject name — the one with most questions
    seen = set()
    subjects = []
    for s in subjects_qs:
        if s.name not in seen:
            seen.add(s.name)
            subjects.append(s)

    # Attach previous session stats per subject for the pupil
    for s in subjects:
        wps = StudentWeakPoint.objects.filter(pupil=request.user, subject=s)
        total_att = sum(w.total_attempted for w in wps)
        total_cor = sum(w.total_correct for w in wps)
        s.prev_accuracy = round(total_cor / total_att * 100) if total_att else None
        s.sessions_done = PracticeResult.objects.filter(
            pupil=request.user, subject=s
        ).count() if hasattr(request.user, 'practiceresult_set') else 0

    return render(request, 'assessments/adaptive_home.html', {'subjects': subjects})


@login_required
def adaptive_start(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)

    if CEQuestion.objects.filter(subject=subject).count() == 0:
        messages.error(request, f'No questions available for {subject.name} yet.')
        return redirect('adaptive_home')

    # Find the pupil's weakest topics for this subject to prioritise
    weak_topics = list(
        StudentWeakPoint.objects.filter(
            pupil=request.user,
            subject=subject,
            total_attempted__gt=0
        ).order_by('total_correct')
        .values_list('topic', flat=True)[:3]
    )

    request.session['adaptive'] = {
        'subject_id': subject_id,
        'subject_name': subject.name,
        'score_float': 1.0,   # start at medium
        'score': 0,
        'total': 0,
        'asked_ids': [],
        'weak_topics': weak_topics,
        'topic_results': {},  # topic -> {correct, total}
    }
    return redirect('adaptive_answer', subject_id=subject_id)


@login_required
def adaptive_answer(request, subject_id):
    session = request.session.get('adaptive')
    if not session or session.get('subject_id') != subject_id:
        return redirect('adaptive_start', subject_id=subject_id)

    subject = get_object_or_404(Subject, pk=subject_id)
    MAX_Q = 20

    # ── POST: process submitted answer ───────────────────────────────────────
    if request.method == 'POST':
        qid = int(request.POST.get('question_id', 0))
        user_answer = request.POST.get('answer', '').strip().upper()

        try:
            question = CEQuestion.objects.get(pk=qid)
        except CEQuestion.DoesNotExist:
            return redirect('adaptive_answer', subject_id=subject_id)

        correct = (user_answer == question.correct_option.upper())
        topic = question.topic or 'General Mathematics'

        # Update difficulty score
        sf = session['score_float']
        sf = sf + 0.35 if correct else sf - 0.35
        session['score_float'] = max(0.0, min(2.0, sf))

        # Update per-topic tracking in session
        tr = session.get('topic_results', {})
        if topic not in tr:
            tr[topic] = {'correct': 0, 'total': 0}
        tr[topic]['total'] += 1
        if correct:
            tr[topic]['correct'] += 1
        session['topic_results'] = tr

        # Update StudentWeakPoint in DB
        wp, _ = StudentWeakPoint.objects.get_or_create(
            pupil=request.user, subject=subject, topic=topic,
            defaults={'total_attempted': 0, 'total_correct': 0}
        )
        wp.total_attempted += 1
        if correct:
            wp.total_correct += 1
        wp.save()

        if correct:
            session['score'] = session.get('score', 0) + 1
        session['total'] = session.get('total', 0) + 1
        session['asked_ids'] = session.get('asked_ids', []) + [qid]

        # Recalculate weak topics from this session's results
        tr = session['topic_results']
        session['weak_topics'] = [
            t for t, v in sorted(tr.items(), key=lambda x: x[1]['correct'] / max(x[1]['total'], 1))
            if v['total'] >= 2 and v['correct'] / v['total'] < 0.5
        ][:3]

        request.session.modified = True

        if session['total'] >= MAX_Q:
            return _finish(request, subject, session)

        return redirect('adaptive_answer', subject_id=subject_id)

    # ── GET: show next question ───────────────────────────────────────────────
    if session.get('total', 0) >= MAX_Q:
        return _finish(request, subject, session)

    current_difficulty = _score_to_difficulty(session.get('score_float', 1.0))
    asked = session.get('asked_ids', [])
    weak_topics = session.get('weak_topics', [])

    question = _pick_question(subject, current_difficulty, asked, weak_topics)

    if question is None:
        # Reset asked list and try again
        session['asked_ids'] = []
        request.session.modified = True
        question = _pick_question(subject, current_difficulty, [], weak_topics)

    if question is None:
        messages.error(request, 'No questions available for this subject.')
        return redirect('adaptive_home')

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
        'q_number': session.get('total', 0) + 1,
        'max_q': MAX_Q,
    })


def _finish(request, subject, session):
    score = session.get('score', 0)
    total = session.get('total', 0)
    pct = round(score / total * 100) if total else 0

    # Build topic breakdown from this session
    tr = session.get('topic_results', {})
    topic_data = []
    for topic, v in tr.items():
        acc = round(v['correct'] / v['total'] * 100) if v['total'] else 0
        topic_data.append({'topic': topic, 'correct': v['correct'], 'total': v['total'], 'accuracy': acc})
    topic_data.sort(key=lambda x: x['accuracy'])

    weak   = [t for t in topic_data if t['accuracy'] < 50][:3]
    strong = [t for t in topic_data if t['accuracy'] >= 70][:3]

    # Build study plan
    study_plan = []
    for t in weak:
        study_plan.append(
            f"Focus on {t['topic']} — you got {t['correct']} out of {t['total']} correct ({t['accuracy']}%). "
            f"Try easier questions on this topic first."
        )
    if not weak:
        study_plan.append(
            'Great session — you performed well across all topics. '
            'Keep pushing with harder questions to build exam confidence.'
        )

    # Overall StudentWeakPoint summary for all-time progress
    all_wps = StudentWeakPoint.objects.filter(
        pupil=request.user, subject=subject, total_attempted__gt=0
    ).order_by('total_correct')

    all_time = []
    for wp in all_wps:
        acc = round(wp.total_correct / wp.total_attempted * 100)
        all_time.append({'topic': wp.topic, 'accuracy': acc,
                         'correct': wp.total_correct, 'total': wp.total_attempted})

    if 'adaptive' in request.session:
        del request.session['adaptive']

    return render(request, 'assessments/adaptive_result.html', {
        'score': score,
        'total': total,
        'percentage': pct,
        'subject_name': subject.name,
        'subject_id': subject.id,
        'weak_topics': weak,
        'strong_topics': strong,
        'study_plan': study_plan,
        'all_time': all_time,
    })


# Import here to avoid circular imports — only needed in adaptive_home stats
try:
    from .models import PracticeResult
except ImportError:
    pass
