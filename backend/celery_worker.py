# backend/celery_worker.py

import os
import logging
from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import json
import csv
from io import StringIO

from extensions import db
from model import User, Quiz, Admin, Chapter, Subject, Question, Score, UserAnswer
from sqlalchemy import func

# --- Configure Logging for Celery Worker ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reminders.log')
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
# -------------------------------------------

# --- Celery Configuration ---
def create_celery_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # --- MODIFIED: Set CELERY_BROKER_URL and CELERY_RESULT_BACKEND to use DB 0 ---
    app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0') # Keep DB 0
    app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0') # <--- CHANGED TO DB 0
    # -----------------------------------------------------------------------------
    app.config['CELERY_ACCEPT_CONTENT'] = ['json']
    app.config['CELERY_TASK_SERIALIZER'] = 'json'
    app.config['CELERY_RESULT_SERIALIZER'] = 'json'
    app.config['CELERY_TIMEZONE'] = 'Asia/Kolkata'

    app.config['CELERY_BEAT_SCHEDULE'] = {
        'generate-monthly-report': {
            'task': 'celery_worker.generate_monthly_report',
            'schedule': timedelta(seconds=30), # For testing: run every 30 seconds
            'args': (),
            'options': {'expires': 86400}
        },
    }
    app.config['CELERY_ENABLE_UTC'] = True

    db.init_app(app)

    celery_app = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery_app.conf.update(app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery_app.Task = ContextTask

    return celery_app

celery = create_celery_app()

# --- Celery Tasks ---

@celery.task
def export_users_csv():
    try:
        users = User.query.all()
        
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(['User ID', 'Email', 'Full Name', 'Qualification', 'DOB', 'Role', 'Quizzes Taken', 'Average Score'])

        for user in users:
            user_scores = Score.query.filter_by(user_id=user.id).all()
            quizzes_taken = len(user_scores)
            total_score_sum = sum(s.score for s in user_scores)
            avg_score = round(total_score_sum / quizzes_taken, 2) if quizzes_taken > 0 else 0

            writer.writerow([
                user.id,
                user.email,
                user.full_name,
                user.qualification,
                user.dob.isoformat() if user.dob else '',
                user.role,
                quizzes_taken,
                avg_score
            ])
        
        csv_content = output.getvalue()
        output.close()

        logger.info("\n--- GENERATED USER REPORT CSV (in worker) ---")
        logger.info(csv_content)
        logger.info("-------------------------------------------\n")

        return csv_content
    except Exception as e:
        logger.error(f"ERROR: Failed to generate CSV report: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'error', 'message': f'Failed to generate CSV report: {e}'}

@celery.task
def generate_monthly_report():
    logger.info("\n--- Running Monthly Activity Report Task ---")
    
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)

    users = User.query.all()
    
    all_user_reports_html_sections = []

    for user in users:
        user_recent_scores = Score.query.filter(
            Score.user_id == user.id,
            Score.attempt_timestamp >= thirty_days_ago
        ).all()
        
        quizzes_taken_recent = len(user_recent_scores)
        total_score_sum_recent = sum(s.score for s in user_recent_scores)
        avg_score_recent = round(total_score_sum_recent / quizzes_taken_recent, 2) if quizzes_taken_recent > 0 else 0

        quiz_attempts_rows = []
        if user_recent_scores:
            for score in user_recent_scores:
                quiz_title = db.session.get(Quiz, score.quiz_id).title if db.session.get(Quiz, score.quiz_id) else 'Unknown Quiz'
                attempt_time = score.attempt_timestamp.strftime('%Y-%m-%d %H:%M')
                quiz_attempts_rows.append(f"<tr><td>{quiz_title}</td><td>{score.score}</td><td>{attempt_time}</td></tr>")
        else:
            quiz_attempts_rows.append('<tr><td colspan="3">No recent quiz attempts.</td></tr>')

        user_report_section = f"""
        <div class="user-report-section">
            <h3>For {user.full_name} ({user.email})</h3>
            <p><strong>Total Quizzes Taken:</strong> {quizzes_taken_recent}</p>
            <p><strong>Average Score:</strong> {avg_score_recent}%</p>
            
            <h4>Recent Quiz Attempts:</h4>
            <table>
                <thead>
                    <tr>
                        <th>Quiz Title</th>
                        <th>Score</th>
                        <th>Attempted On</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(quiz_attempts_rows)}
                </tbody>
            </table>
        </div>
        <hr style="border-top: 1px solid #4a2d73; margin: 30px 0;">
        """
        all_user_reports_html_sections.append(user_report_section)
        logger.info(f"REPORT GENERATED: Monthly report section for {user.email} prepared.")

    consolidated_report_html = f"""
    <html>
    <head>
        <title>Monthly Activity Report - All Users</title>
        <style>
            body {{ font-family: sans-serif; background-color: #1a0f2d; color: #e0e0e0; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: 20px auto; background-color: #2b1a47; padding: 30px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.5); border: 1px solid #4a2d73; }}
            h2 {{ color: #e060a8; text-shadow: 0 0 5px rgba(224, 96, 168, 0.5); font-weight: bold; text-align: center; margin-bottom: 20px; }}
            h3 {{ color: #5dbeff; margin-top: 30px; border-bottom: 1px solid #4a2d73; padding-bottom: 5px; }}
            h4 {{ color: #c0b0d0; margin-top: 20px; }}
            p {{ color: #c0b0d0; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; border-radius: 8px; overflow: hidden; }}
            th, td {{ border: 1px solid #4a2d73; padding: 12px; text-align: left; color: #e0e0e0; }}
            th {{ background-color: #3d2766; font-weight: bold; color: #e060a8; }}
            tr:nth-child(even) {{ background-color: #332050; }}
            tr:hover {{ background-color: #4a307a; }}
            .footer {{ margin-top: 40px; text-align: center; font-size: 0.9em; color: #6a4a9c; }}
            .user-report-section {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Consolidated Monthly Activity Report</h2>
            <p>Report Period: {thirty_days_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}</p>
            {''.join(all_user_reports_html_sections) if all_user_reports_html_sections else '<p style="text-align: center; color: #c0b0d0;">No users found to generate reports for.</p>'}
            <p class="footer">Generated by Quiz Master. Keep practicing!</p>
        </div>
    </body>
    </html>
    """
    
    logger.info("--- Monthly Activity Report Task Finished. ---")
    return consolidated_report_html
