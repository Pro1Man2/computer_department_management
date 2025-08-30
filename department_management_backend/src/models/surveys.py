from department_management_backend.src.database import db

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)

class SurveyQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey("survey.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False) # e.g., 'text', 'radio', 'checkbox', 'rating'
    options = db.Column(db.Text, nullable=True) # JSON string for options

class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey("survey.id"), nullable=False)
    trainee_id = db.Column(db.Integer, nullable=True) # Can be null for anonymous surveys
    trainer_id = db.Column(db.Integer, nullable=True)
    submitted_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey("survey_response.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("survey_question.id"), nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    answer_value = db.Column(db.Integer, nullable=True) # For rating questions


