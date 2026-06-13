# assessments/views_mastery.py
import os
import random
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from lessons.models import Subject
from .models import (CEQuestion, StudentWeakPoint,
                     TopicLearningSession, MiniTestResult, TopicNote)

logger = logging.getLogger(__name__)


# ── Groq note generation ──────────────────────────────────────────────────────
def _generate_note(topic, base_note, wrong_question=None):
    try:
        from groq import Groq
        api_key = os.environ.get('GROQ_API_KEY', '')
        if not api_key:
            return base_note

        wrong_q_text = ''
        if wrong_question:
            wrong_q_text = (
                f'\n\nThe pupil got this question wrong:\n'
                f'"{wrong_question.question_text}"\n'
                f'A) {wrong_question.option_a}  B) {wrong_question.option_b}  '
                f'C) {wrong_question.option_c}  D) {wrong_question.option_d}\n'
                f'Correct answer: Option {wrong_question.correct_option}'
            )

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{'role': 'user', 'content': (
                f'You are a friendly Nigerian primary school teacher explaining {topic} '
                f'to a Primary 6 pupil preparing for the Common Entrance Examination. '
                f'Write a short, clear explanation using simple English and short sentences. '
                f'Include one worked example from Nigerian life (money, market, school). '
                f'Base your explanation on this curriculum note:\n\n{base_note}'
                f'{wrong_q_text}\n\n'
                f'If a wrong question was provided, add a section called '
                f'"Let us look at your question" with a clear step-by-step solution. '
                f'Keep the whole note under 280 words. Write in plain paragraphs only. '
                f'No bullet points. No markdown.'
            )}],
            max_tokens=500,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f'Groq note generation failed: {e}')
        return base_note


# ── Three-signal mastery check (Bloom 1968; Lord 1980) ───────────────────────
def _check_mastery(mini_result):
    """
    Returns (passed: bool, message: str, signals: dict)
    Three signals ALL must be satisfied:
      1. Accuracy >= 60%
      2. At least 3 consecutive correct answers
      3. At least 1 Medium-level question correct
    """
    answers = mini_result.answers

    # Signal 1 — accuracy
    acc_met = mini_result.accuracy >= 60

    # Signal 2 — consecutive run
    max_run = current_run = 0
    for a in answers:
        if a.get('correct'):
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    run_met = max_run >= 3

    # Signal 3 — at least 1 medium correct
    med_met = any(
        a.get('correct') and a.get('difficulty') in ('medium', 'hard')
        for a in answers
    )

    passed = acc_met and run_met and med_met

    if not acc_met:
        msg = f'Your score was {mini_result.accuracy}% — you need at least 60% to move on. Read the note again carefully.'
    elif not run_met:
        msg = f'Good score! But you need at least 3 correct answers in a row (your best run was {max_run}). Read the note and try again.'
    elif not med_met:
        msg = 'Well done on the easy questions! You need to answer at least one standard-level question correctly to show real understanding.'
    else:
        msg = 'Excellent! You have mastered this topic.'

    signals = {
        'accuracy':    {'value': f'{mini_result.accuracy}%', 'needed': '60%',  'met': acc_met},
        'consecutive': {'value': f'{max_run} in a row',      'needed': '3 in a row', 'met': run_met},
        'medium':      {'value': 'Yes' if med_met else 'No', 'needed': '1 standard question', 'met': med_met},
    }
    return passed, msg, signals


# ── Views ─────────────────────────────────────────────────────────────────────

@login_required
def learn_start(request):
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        messages.error(request, 'No subject specified.')
        return redirect('adaptive_home')

    subject = get_object_or_404(Subject, pk=subject_id)

    # Weak = accuracy < 40%. Order: highest accuracy first (easiest to fix — Bandura 1997)
    all_wps = StudentWeakPoint.objects.filter(
        pupil=request.user, subject=subject, total_attempted__gt=0
    )
    weak_topics = sorted(
        [wp for wp in all_wps if wp.total_correct / wp.total_attempted < 0.40],
        key=lambda wp: -wp.total_correct / wp.total_attempted
    )

    if not weak_topics:
        messages.info(request, 'No weak topics to work on right now. Keep practising!')
        return redirect('adaptive_home')

    # Close any existing open session
    TopicLearningSession.objects.filter(
        pupil=request.user, subject=subject
    ).exclude(status='complete').update(status='complete')

    session = TopicLearningSession.objects.create(
        pupil=request.user,
        subject=subject,
        weak_topics=[wp.topic for wp in weak_topics],
        current_index=0,
        status='reading',
    )
    return redirect('learn_note', session_id=session.id)


@login_required
def learn_note(request, session_id):
    session = get_object_or_404(TopicLearningSession, pk=session_id, pupil=request.user)

    if session.status == 'complete':
        return render(request, 'assessments/learn_complete.html', {'session': session})

    topic = session.current_topic()
    if not topic:
        session.status = 'complete'; session.save()
        return render(request, 'assessments/learn_complete.html', {'session': session})

    # Generate note if needed for this topic
    if not session.generated_note:
        try:
            tn = TopicNote.objects.get(topic__iexact=topic)
            base = tn.lecture_notes or tn.scheme_of_work or f'Study guide for {topic}.'
        except TopicNote.DoesNotExist:
            base = (f'{topic} is an important topic in the Common Entrance Examination. '
                    f'Make sure you understand the basic concept and practise questions carefully.')

        wrong_q = CEQuestion.objects.filter(
            subject=session.subject, topic__iexact=topic
        ).order_by('?').first()

        session.wrong_question = wrong_q
        session.generated_note = _generate_note(topic, base, wrong_q)
        session.status = 'reading'
        session.save()

    attempt = session.mini_test_results.filter(topic=topic).count() + 1

    return render(request, 'assessments/learn_note.html', {
        'session':       session,
        'topic':         topic,
        'note':          session.generated_note,
        'attempt':       attempt,
        'topic_number':  session.current_index + 1,
        'total_topics':  len(session.weak_topics),
        'subject':       session.subject,
    })


@login_required
def learn_test(request, session_id):
    session = get_object_or_404(TopicLearningSession, pk=session_id, pupil=request.user)
    topic = session.current_topic()
    if not topic:
        return redirect('learn_result', session_id=session_id)

    base_qs = CEQuestion.objects.filter(subject=session.subject, topic__iexact=topic)
    easy_qs   = list(base_qs.filter(difficulty_predicted='easy').order_by('?')[:3])
    medium_qs = list(base_qs.filter(difficulty_predicted='medium').order_by('?')[:2])

    # Pad if not enough
    have = len(easy_qs) + len(medium_qs)
    if have < 5:
        extra = list(base_qs.exclude(
            pk__in=[q.pk for q in easy_qs + medium_qs]
        ).order_by('?')[:5 - have])
        easy_qs += extra

    questions = (easy_qs + medium_qs)[:5]
    random.shuffle(questions)

    if not questions:
        messages.warning(request, f'Not enough questions in {topic} yet. Moving on.')
        session.advance()
        if session.status == 'complete':
            return render(request, 'assessments/learn_complete.html', {'session': session})
        return redirect('learn_note', session_id=session_id)

    request.session[f'mini_qids_{session_id}'] = [q.pk for q in questions]
    session.status = 'testing'; session.save()

    attempt = session.mini_test_results.filter(topic=topic).count() + 1

    return render(request, 'assessments/learn_test.html', {
        'session':       session,
        'topic':         topic,
        'questions':     [{'obj': q, 'choices': [
                              ('A', q.option_a), ('B', q.option_b),
                              ('C', q.option_c), ('D', q.option_d),
                          ]} for q in questions],
        'attempt':       attempt,
        'topic_number':  session.current_index + 1,
        'total_topics':  len(session.weak_topics),
        'subject':       session.subject,
    })


@login_required
def learn_answer(request, session_id):
    if request.method != 'POST':
        return redirect('learn_test', session_id=session_id)

    session  = get_object_or_404(TopicLearningSession, pk=session_id, pupil=request.user)
    topic    = session.current_topic()
    qids     = request.session.get(f'mini_qids_{session_id}', [])
    score    = 0
    answers  = []

    for qid in qids:
        try:
            q = CEQuestion.objects.get(pk=qid)
        except CEQuestion.DoesNotExist:
            continue
        user_ans = request.POST.get(f'answer_{qid}', '').strip().upper()
        correct  = (user_ans == q.correct_option.upper())
        if correct:
            score += 1

        wp, _ = StudentWeakPoint.objects.get_or_create(
            pupil=request.user, subject=session.subject, topic=topic,
            defaults={'total_attempted': 0, 'total_correct': 0}
        )
        wp.total_attempted += 1
        if correct:
            wp.total_correct += 1
        wp.save()

        answers.append({
            'qid':        qid,
            'correct':    correct,
            'difficulty': q.difficulty_predicted or 'easy',
            'user_ans':   user_ans,
            'right_ans':  q.correct_option,
            'question':   q.question_text[:100],
        })

    attempt_num = session.mini_test_results.filter(topic=topic).count() + 1
    mini = MiniTestResult.objects.create(
        session=session, topic=topic,
        attempt_number=attempt_num,
        answers=answers, score=score, total=len(qids),
    )
    passed, _, _ = _check_mastery(mini)
    mini.passed = passed; mini.save()

    return redirect('learn_result', session_id=session_id)


@login_required
def learn_result(request, session_id):
    session = get_object_or_404(TopicLearningSession, pk=session_id, pupil=request.user)
    topic   = session.current_topic()

    latest = session.mini_test_results.filter(topic=topic).order_by('-taken_at').first()
    if not latest:
        return redirect('learn_note', session_id=session_id)

    passed, message, signals = _check_mastery(latest)

    if request.method == 'POST':
        if 'advance' in request.POST and passed:
            has_more = session.advance()
            if has_more:
                return redirect('learn_note', session_id=session_id)
            return render(request, 'assessments/learn_complete.html', {'session': session})
        if 'retry' in request.POST and not passed:
            session.generated_note = ''
            session.status = 'reading'
            session.save()
            return redirect('learn_note', session_id=session_id)

    next_topic = (session.weak_topics[session.current_index + 1]
                  if session.current_index + 1 < len(session.weak_topics) else None)

    return render(request, 'assessments/learn_result.html', {
        'session':       session,
        'topic':         topic,
        'latest':        latest,
        'passed':        passed,
        'message':       message,
        'signals':       signals,
        'review':        latest.answers,
        'attempt':       latest.attempt_number,
        'next_topic':    next_topic,
        'subject':       session.subject,
        'topic_number':  session.current_index + 1,
        'total_topics':  len(session.weak_topics),
    })
