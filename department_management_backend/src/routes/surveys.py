from flask import Blueprint, request, jsonify
from department_management_backend.src.models.surveys import Survey, SurveyQuestion, SurveyResponse, QuestionAnswer
from department_management_backend.src.database import db
import json

surveys_bp = Blueprint("surveys", __name__)

@surveys_bp.route("/surveys", methods=["POST"])
def create_survey():
    data = request.get_json()
    new_survey = Survey(
        title=data["title"],
        description=data.get("description"),
        is_active=data.get("is_active", True)
    )
    db.session.add(new_survey)
    db.session.commit()

    for q in data.get("questions", []):
        new_question = SurveyQuestion(
            survey_id=new_survey.id,
            question_text=q["question_text"],
            question_type=q["question_type"],
            options=json.dumps(q["options"]) if "options" in q else None
        )
        db.session.add(new_question)
    db.session.commit()
    return jsonify({"message": "Survey created successfully", "survey_id": new_survey.id}), 201

@surveys_bp.route("/surveys/<int:survey_id>/respond", methods=["POST"])
def respond_to_survey(survey_id):
    data = request.get_json()
    new_response = SurveyResponse(
        survey_id=survey_id,
        trainee_id=data.get("trainee_id"),
        trainer_id=data.get("trainer_id")
    )
    db.session.add(new_response)
    db.session.commit()

    for qa in data.get("answers", []):
        new_answer = QuestionAnswer(
            response_id=new_response.id,
            question_id=qa["question_id"],
            answer_text=qa.get("answer_text"),
            answer_value=qa.get("answer_value")
        )
        db.session.add(new_answer)
    db.session.commit()
    return jsonify({"message": "Survey response submitted successfully"}), 201

@surveys_bp.route("/surveys", methods=["GET"])
def get_surveys():
    surveys = Survey.query.all()
    output = []
    for survey in surveys:
        output.append({
            "id": survey.id,
            "title": survey.title,
            "description": survey.description,
            "created_at": survey.created_at.isoformat(),
            "is_active": survey.is_active
        })
    return jsonify(output)


