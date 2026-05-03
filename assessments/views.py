import json
import random
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Quiz, Question, QuizResult, CEQuestion, PracticeResult, StudentWeakPoint
from lessons.models import Subject, Lesson

logger = logging.getLogger(__name__)


# ── Groq AI Feedback ─────────────────────────────────────────────────────

def get_groq_feedback(wrong_questions, subject_name, score, total, correct):
    try:
        from groq import Groq
        client = Groq(api_key=settings.GROQ_API_KEY)

        mistakes_text = ""
        for i, item in enumerate(wrong_questions, 1):
            mistakes_text += (
                f"\n{i}. Question: {item['question']}\n"
                f"   Student answered: {item['student_answer']}\n"
                f"   Correct answer: {item['correct_answer']}\n"
            )

        prompt = f"""You are an expert tutor analysing a primary school student's quiz performance.

Subject: {subject_name}
Score: {correct}/{total} ({score}%)

Questions the student got WRONG:
{mistakes_text if mistakes_text else 'None — the student got everything right!'}

Respond ONLY with a valid JSON object (no markdown, no backticks) using exactly this structure:
{{
  "overall_verdict": "one sentence summary of performance",
  "strengths": ["strength 1", "strength 2"],
  "weakpoints": ["weakness topic 1", "weakness topic 2"],
  "improvement_plan": [
    {{"step": 1, "action": "what to do", "detail": "how to do it"}},
    {{"step": 2, "action": "what to do", "detail": "how to do it"}},
    {{"step": 3, "action": "what to do", "detail": "how to do it"}}
  ],
  "study_tips": ["tip 1", "tip 2", "tip 3"],
  "encouragement": "a warm motivating message addressed to the student"
}}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)

    except Exception as e:
        logger.error(f"Groq feedback error: {e}")
        return {
            "overall_verdict": f"You scored {score}% on this quiz.",
            "strengths": ["You completed the quiz — that takes effort!"],
            "weakpoints": ["Review the questions you missed carefully."],
            "improvement_plan": [
                {"step": 1, "action": "Re-read your lesson notes", "detail": "Focus on topics from the wrong answers."},
                {"step": 2, "action": "Practice similar questions", "detail": "Try the quiz again after reviewing."},
                {"step": 3, "action": "Ask your teacher", "detail": "Ask for help on questions you did not understand."},
            ],
            "study_tips": ["Study in short focused sessions.", "Write key facts by hand.", "Test yourself before sleeping."],
            "encouragement": "Keep going — every attempt makes you better!",
        }


def build_wrong_questions(questions, answers_json, mode="quiz"):
    wrong = []
    if mode == "quiz":
        for q in questions:
            data = answers_json.get(str(q.id), {})
            if not data.get('is_correct'):
                wrong.append({
                    "question": q.question_text[:200],
                    "student_answer": data.get('selected', '—'),
                    "correct_answer": q.correct_option,
                })
    else:
        for qid, data in answers_json.items():
            if not data.get('is_correct'):
                wrong.append({
                    "question": data.get('question', 'Question')[:200],
                    "student_answer": data.get('selected', '—'),
                    "correct_answer": data.get('correct', '—'),
                })
    return wrong


# ── ML Difficulty Classifier ─────────────────────────────────────────────

def classify_question(question_text, opt_a='', opt_b='', opt_c='', opt_d=''):
    try:
        from assessments.ml.classifier import predict_difficulty, predict_topic
        difficulty = predict_difficulty(question_text, opt_a, opt_b, opt_c, opt_d)
        topic = predict_topic(question_text)
        return difficulty, topic
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return 'medium', 'General Mathematics'


# ── Student Weak Point Tracker ────────────────────────────────────────────

def update_weak_points(pupil, subject, answers_json, questions=None, mode='ce'):
    """Update StudentWeakPoint records after a quiz/practice attempt"""
    try:
        from assessments.ml.classifier import predict_topic
        if mode == 'ce':
            for qid, data in answers_json.items():
                q = CEQuestion.objects.filter(id=int(qid)).first()
                if not q:
                    continue
                topic = q.topic or predict_topic(q.question_text)
                wp, _ = StudentWeakPoint.objects.get_or_create(
                    pupil=pupil, subject=subject, topic=topic
                )
                wp.total_attempted += 1
                if data.get('is_correct'):
                    wp.total_correct += 1
                wp.save()
        else:
            if questions:
                for q in questions:
                    data = answers_json.get(str(q.id), {})
                    topic = q.topic or predict_topic(q.question_text)
                    subj = q.quiz.lesson.subject if hasattr(q.quiz.lesson, 'subject') else None
                    if not subj:
                        continue
                    wp, _ = StudentWeakPoint.objects.get_or_create(
                        pupil=pupil, subject=subj, topic=topic
                    )
                    wp.total_attempted += 1
                    if data.get('is_correct'):
                        wp.total_correct += 1
                    wp.save()
    except Exception as e:
        logger.error(f"Weak point update error: {e}")


def get_student_report(pupil):
    """Get a full weak point report for a student"""
    weak_points = StudentWeakPoint.objects.filter(pupil=pupil).order_by('accuracy')
    report = {
        'weak': [],
        'needs_improvement': [],
        'strong': [],
    }
    for wp in weak_points:
        report[wp.status].append(wp)
    return report


# ── Regular Quizzes ───────────────────────────────────────────────────────

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
        wrong = build_wrong_questions(questions, answers, mode="quiz")
        subject_name = quiz.lesson.subject.name if hasattr(quiz.lesson, 'subject') else quiz.lesson.title
        feedback = get_groq_feedback(wrong, subject_name, score, total, correct)

        result = QuizResult.objects.create(
            pupil=request.user, quiz=quiz, score=score,
            total_questions=total, correct_answers=correct,
            answers_json=answers, ai_feedback=feedback,
        )
        update_weak_points(request.user, None, answers, questions=list(questions), mode='quiz')
        return redirect('quiz_result', result_id=result.id)

    return render(request, 'assessments/take_quiz.html', {'quiz': quiz, 'questions': questions})


@login_required
def quiz_result(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id)
    questions = result.quiz.questions.all()
    feedback = result.ai_feedback or {}
    report = get_student_report(request.user)
    return render(request, 'assessments/quiz_result.html', {
        'result': result,
        'questions': questions,
        'feedback': feedback,
        'report': report,
    })


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
            q_text = request.POST.get(f'q_text_{idx}', '')
            opt_a = request.POST.get(f'q_a_{idx}', '')
            opt_b = request.POST.get(f'q_b_{idx}', '')
            opt_c = request.POST.get(f'q_c_{idx}', '')
            opt_d = request.POST.get(f'q_d_{idx}', '')
            difficulty, topic = classify_question(q_text, opt_a, opt_b, opt_c, opt_d)
            Question.objects.create(
                quiz=quiz, question_text=q_text,
                option_a=opt_a, option_b=opt_b,
                option_c=opt_c, option_d=opt_d,
                correct_option=request.POST.get(f'q_correct_{idx}', 'A'),
                order=idx,
                difficulty_predicted=difficulty,
                topic=topic,
            )
            idx += 1
        messages.success(request, f'Quiz "{quiz.title}" created with {idx} questions.')
        return redirect('lesson_detail', pk=lesson.id)

    return render(request, 'assessments/quiz_create.html', {'lesson': lesson})


# ── Common Entrance Practice ──────────────────────────────────────────────

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
    questions = questions[:20]

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
                'topic': q.topic or 'General',
            }
            if is_correct:
                correct += 1

        score = round((correct / total) * 100, 2) if total else 0
        subject_obj = CEQuestion.objects.filter(id=int(q_ids[0])).first().subject if q_ids else None
        subject_label = subject_obj.name if subject_obj else 'Common Entrance'

        wrong = build_wrong_questions(None, answers, mode="ce")
        feedback = get_groq_feedback(wrong, subject_label, score, total, correct)

        result = PracticeResult.objects.create(
            pupil=request.user, subject=subject_obj, score=score,
            total_questions=total, correct_answers=correct,
            answers_json=answers, ai_feedback=feedback,
        )
        update_weak_points(request.user, subject_obj, answers, mode='ce')
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
    feedback = result.ai_feedback or {}
    report = get_student_report(request.user)
    return render(request, 'assessments/ce_result.html', {
        'result': result,
        'feedback': feedback,
        'report': report,
    })


@login_required
def student_report(request):
    report = get_student_report(request.user)
    return render(request, 'assessments/student_report.html', {'report': report})


@login_required
def ce_add_question(request):
    if not (request.user.is_teacher or request.user.is_admin):
        return redirect('dashboard')
    subjects = Subject.objects.all()
    if request.method == 'POST':
        subject = get_object_or_404(Subject, id=request.POST.get('subject'))
        q_text = request.POST.get('question_text', '')
        opt_a = request.POST.get('option_a', '')
        opt_b = request.POST.get('option_b', '')
        opt_c = request.POST.get('option_c', '')
        opt_d = request.POST.get('option_d', '')
        difficulty, topic = classify_question(q_text, opt_a, opt_b, opt_c, opt_d)
        CEQuestion.objects.create(
            subject=subject,
            exam_year=int(request.POST.get('exam_year', 2024)),
            question_text=q_text,
            option_a=opt_a, option_b=opt_b,
            option_c=opt_c, option_d=opt_d,
            correct_option=request.POST.get('correct_option', 'A'),
            difficulty_level=request.POST.get('difficulty_level', difficulty),
            difficulty_predicted=difficulty,
            topic=topic,
        )
        messages.success(request, f'Question added. AI classified it as: {difficulty.upper()} | Topic: {topic}')
        return redirect('ce_add_question')
    return render(request, 'assessments/ce_add_question.html', {'subjects': subjects})
