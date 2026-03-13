# EduCloud — Cloud-Based E-Learning Management System for Primary Schools

A Django web application designed for Nigerian primary schools, featuring lesson delivery, automated assessment, a common entrance past questions data bank, assignment management, progress tracking, and a parental access portal.

**Final Year Project — Redeemer's University, Department of Computer Science, 2026**

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+ installed
- pip (Python package manager)

### 2. Setup

```bash
# Clone or extract the project
cd elearn

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Seed the database with demo data
python manage.py seed_data

# Start the development server
python manage.py runserver
```

### 3. Open in Browser
Go to: **http://127.0.0.1:8000**

### 4. Login Credentials (Demo Data)

| Role    | Username       | Password     |
|---------|---------------|--------------|
| Admin   | admin         | admin123     |
| Teacher | teacher1      | teacher123   |
| Parent  | parent1       | parent123    |
| Pupil   | adaeze.obi    | pupil123     |
| Pupil   | emeka.nnamdi  | pupil123     |
| Pupil   | david.johnson | pupil123     |

---

## System Modules

### 1. Lesson Delivery
Teachers upload text, image, audio, and video lessons organised by subject and class level. Pupils access lessons through visual subject cards.

### 2. Automated Quiz & Assessment
Multiple-choice quizzes linked to specific lessons. Auto-graded with instant feedback showing correct and incorrect answers.

### 3. Common Entrance Past Questions Data Bank
Categorised by subject, exam year, and difficulty level. Examination-style practice with cumulative score tracking.

### 4. Assignment Submission
Teachers create and publish assignments with deadlines. Pupils submit responses. Teachers grade and provide written feedback.

### 5. Progress Tracking
Graphical dashboards showing performance across subjects. Chart.js-powered score trends over time.

### 6. Parental Access Portal
Read-only view of a child's grades, practice scores, assignments, and teacher feedback.

---

## User Roles

- **Admin**: Manages user accounts, views system-wide analytics, accesses Django admin
- **Teacher**: Creates lessons, quizzes, assignments, adds CE questions, monitors pupil progress
- **Pupil**: Accesses lessons, takes quizzes, practises CE questions, submits assignments, views progress
- **Parent**: Views linked children's academic performance (read-only)

---

## Tech Stack

| Component      | Technology                    |
|---------------|-------------------------------|
| Backend       | Python 3.11, Django 4.2       |
| Database      | SQLite (dev) / PostgreSQL (prod) |
| Frontend      | Django Templates, Tailwind CSS, Chart.js |
| Deployment    | Render / Heroku / Any WSGI host |
| Static Files  | WhiteNoise                    |

---

## Deploy to Render

1. Push this project to a GitHub repository
2. Go to [render.com](https://render.com) and create a new Web Service
3. Connect your GitHub repo
4. Render will detect `render.yaml` and configure automatically
5. After deployment, open the Render shell and run:
   ```
   python manage.py seed_data
   ```

---

## Adding Your Own Common Entrance Questions

### Option A: Through the Web Interface
Login as a teacher or admin and go to **Add CE Questions** from the navigation.

### Option B: Through Django Admin
Go to `/admin/` and use the CEQuestion admin interface to bulk-add questions.

### Option C: Management Command
Create a script similar to `seed_data.py` to bulk-import questions from a file.

---

## Project Structure

```
elearn/
├── manage.py                   # Django management
├── requirements.txt            # Python dependencies
├── build.sh                    # Render build script
├── render.yaml                 # Render deployment config
├── elearn_project/             # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                   # User auth, roles, dashboards
│   ├── models.py               # Custom User model (Admin/Teacher/Pupil/Parent)
│   ├── views.py                # Login, dashboard views
│   └── management/commands/    # seed_data command
├── lessons/                    # Lesson delivery module
│   ├── models.py               # Subject, Lesson
│   └── views.py                # CRUD views
├── assessments/                # Quiz + CE Past Questions module
│   ├── models.py               # Quiz, Question, CEQuestion, Results
│   └── views.py                # Quiz taking, CE practice, grading
├── assignments/                # Assignment module
│   ├── models.py               # Assignment, Submission
│   └── views.py                # Create, submit, grade
├── analytics/                  # Progress tracking module
│   └── views.py                # Dashboards, chart data API
├── templates/                  # All HTML templates
└── static/css/                 # Stylesheet
```

---

## Database Schema (3NF)

- **Users**: user_id, username, first_name, last_name, role, class_level, parent_link
- **Subjects**: subject_id, name, class_level, color
- **Lessons**: lesson_id, subject_id, topic_title, content_text, content_type, uploaded_by
- **Quizzes**: quiz_id, lesson_id, title, created_by
- **Questions**: question_id, quiz_id, question_text, options A-D, correct_option
- **CEQuestions**: ce_question_id, subject_id, exam_year, difficulty, question_text, options, correct
- **QuizResults**: result_id, pupil_id, quiz_id, score, correct_answers, date_taken
- **PracticeResults**: practice_id, pupil_id, subject_id, score, correct_answers, date_attempted
- **Assignments**: assignment_id, teacher_id, class_level, title, description, deadline
- **Submissions**: submission_id, assignment_id, pupil_id, response_text, grade, feedback
