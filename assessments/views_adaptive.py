"""
Adaptive Practice Mode.

Instead of the pupil choosing a difficulty level (Easy / Medium / Hard),
the system starts at a middle difficulty and adjusts after every question
based on the pupil's running performance:

  - Each answer moves an internal "difficulty score" (0.0 = easiest,
    2.0 = hardest, starting at 1.0 = medium) up by +0.35 if correct, or
    down by -0.35 if incorrect, clamped to [0, 2].
  - The next question is drawn at random from whichever difficulty band
    the current score falls into (Easy below 0.7, Medium 0.7-1.3, Hard
    above 1.3), and from ANY exam year, so both difficulty and year are
    effectively shuffled question to question.
  - If a pupil keeps failing, the score drifts down and Easy questions
    become more frequent. If a pupil keeps passing, the score drifts up
    and Hard questions become more frequent.

No new database tables are used. In-progress state is kept in the
session; the finished session is saved as a normal PracticeResult (the
same model used by ordinary practice), with the adaptive-specific detail
(difficulty trajectory, per-question breakdown) stored inside the
existing answers_json field. StudentWeakPoint rows are updated exactly as
they are for ordinary practice, so adaptive sessions feed the same
gap-analysis and recommendation logic.
"""
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import CEQuestion, PracticeResult, StudentWeakPoint
from lessons.models import Subject

SESSION_KEY = "adaptive_session"
TOTAL_QUESTIONS = 15
SCORE_STEP = 0.35
SCORE_MIN, SCORE_MAX = 0.0, 2.0
EASY_CEILING = 0.7   # score below this -> easy
HARD_FLOOR = 1.3     # score above this -> hard


def _difficulty_for_score(score):
    if score < EASY_CEILING:
        return "easy"
    if score > HARD_FLOOR:
        return "hard"
    return "medium"


def _pick_question(subject, difficulty, exclude_ids):
    """Pick a random question at the given difficulty, any exam year,
    excluding questions already asked this session. Falls back to any
    difficulty if that band is exhausted."""
    qs = (CEQuestion.objects
          .filter(subject=subject, difficulty_level=difficulty)
          .exclude(id__in=exclude_ids)
          .order_by("?"))
    q = qs.first()
    if q is None:
        # band exhausted (e.g. very few Hard questions) - widen to any difficulty
        qs = (CEQuestion.objects
              .filter(subject=subject)
              .exclude(id__in=exclude_ids)
              .order_by("?"))
        q = qs.first()
    return q


def _question_context(question, subject, qnum, difficulty, last_correct=None):
    return {
        "question": question,
        "subject": subject,
        "qnum": qnum,
        "total": TOTAL_QUESTIONS,
        "difficulty": difficulty,
        "difficulty_label": {"easy": "Easy", "medium": "Medium", "hard": "Hard"}[difficulty],
        "last_correct": last_correct,
        "progress_pct": round(100 * (qnum - 1) / TOTAL_QUESTIONS),
    }


@login_required
def adaptive_home(request):
    """Subject picker for adaptive practice."""
    subjects = Subject.objects.all()
    return render(request, "assessments/adaptive_home.html", {"subjects": subjects})


@login_required
def adaptive_start(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    session = {
        "subject_id": subject.id,
        "score": 1.0,
        "asked_ids": [],
        "answers": [],
        "trajectory": [],
    }
    difficulty = _difficulty_for_score(session["score"])
    question = _pick_question(subject, difficulty, [])
    if question is None:
        return render(request, "assessments/adaptive_home.html", {
            "subjects": Subject.objects.all(),
            "error": f"No questions are available yet for {subject.name}.",
        })

    session["asked_ids"].append(question.id)
    session["trajectory"].append(difficulty)
    request.session[SESSION_KEY] = session

    return render(request, "assessments/adaptive_question.html",
                   _question_context(question, subject, 1, difficulty))


@login_required
def adaptive_answer(request, subject_id):
    session = request.session.get(SESSION_KEY)
    subject = get_object_or_404(Subject, id=subject_id)

    if not session or session.get("subject_id") != subject.id or request.method != "POST":
        return redirect("adaptive_start", subject_id=subject.id)

    question_id = int(request.POST.get("question_id"))
    chosen = request.POST.get("answer", "")
    question = get_object_or_404(CEQuestion, id=question_id)
    is_correct = (chosen == question.correct_option)

    session["answers"].append({
        "question_id": question.id,
        "question_text": question.question_text,
        "topic": question.topic,
        "difficulty": question.difficulty_level,
        "exam_year": question.exam_year,
        "chosen": chosen,
        "correct_option": question.correct_option,
        "is_correct": is_correct,
    })
    session["score"] = max(SCORE_MIN, min(SCORE_MAX,
        session["score"] + (SCORE_STEP if is_correct else -SCORE_STEP)))

    if len(session["asked_ids"]) >= TOTAL_QUESTIONS:
        return _finalize(request, subject, session)

    difficulty = _difficulty_for_score(session["score"])
    next_question = _pick_question(subject, difficulty, session["asked_ids"])
    if next_question is None:
        return _finalize(request, subject, session)

    session["asked_ids"].append(next_question.id)
    session["trajectory"].append(difficulty)
    request.session[SESSION_KEY] = session

    qnum = len(session["asked_ids"])
    return render(request, "assessments/adaptive_question.html",
                   _question_context(next_question, subject, qnum, difficulty, is_correct))


def _finalize(request, subject, session):
    answers = session["answers"]
    total = len(answers)
    correct_count = sum(1 for a in answers if a["is_correct"])
    score_pct = round(100 * correct_count / total, 1) if total else 0.0

    # update per-topic weak points, same as ordinary practice
    topic_stats = {}
    for a in answers:
        att, corr = topic_stats.get(a["topic"], (0, 0))
        topic_stats[a["topic"]] = (att + 1, corr + (1 if a["is_correct"] else 0))

    for topic, (att, corr) in topic_stats.items():
        wp, _ = StudentWeakPoint.objects.get_or_create(
            pupil=request.user, subject=subject, topic=topic,
        )
        wp.total_attempted += att
        wp.total_correct += corr
        wp.save()

    result = PracticeResult.objects.create(
        pupil=request.user,
        subject=subject,
        score=score_pct,
        total_questions=total,
        correct_answers=correct_count,
        answers_json={
            "mode": "adaptive",
            "answers": answers,
            "difficulty_trajectory": session["trajectory"],
            "final_score": round(session["score"], 2),
        },
        ai_feedback={},
    )

    if request.session.get(SESSION_KEY):
        del request.session[SESSION_KEY]

    # weak/needs-improvement/strong verdict per topic, same thresholds as StudentWeakPoint.status
    topic_breakdown = []
    for topic, (att, corr) in topic_stats.items():
        acc = round(100 * corr / att, 1) if att else 0
        status = "weak" if acc < 40 else ("needs_improvement" if acc < 70 else "strong")
        topic_breakdown.append({"topic": topic, "attempted": att, "correct": corr,
                                 "accuracy": acc, "status": status})
    topic_breakdown.sort(key=lambda t: t["accuracy"])

    return render(request, "assessments/adaptive_result.html", {
        "subject": subject,
        "result": result,
        "score_pct": score_pct,
        "correct_count": correct_count,
        "total": total,
        "answers": answers,
        "trajectory": session["trajectory"],
        "topic_breakdown": topic_breakdown,
    })
