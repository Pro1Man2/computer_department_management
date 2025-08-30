from flask import Blueprint, request, jsonify
from department_management_backend.src.models.behavior_records import BehaviorRecord
from department_management_backend.src.database import db

behavior_records_bp = Blueprint("behavior_records", __name__)

@behavior_records_bp.route("/behavior_records", methods=["POST"])
def add_behavior_record():
    data = request.get_json()
    new_record = BehaviorRecord(
        trainee_id=data["trainee_id"],
        behavior_type=data["behavior_type"],
        description=data.get("description"),
        recorded_by_trainer_id=data["recorded_by_trainer_id"]
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify({"message": "Behavior record added successfully"}), 201

@behavior_records_bp.route("/behavior_records", methods=["GET"])
def get_behavior_records():
    records = BehaviorRecord.query.all()
    output = []
    for record in records:
        output.append({
            "id": record.id,
            "trainee_id": record.trainee_id,
            "behavior_type": record.behavior_type,
            "description": record.description,
            "date_recorded": record.date_recorded.isoformat(),
            "recorded_by_trainer_id": record.recorded_by_trainer_id
        })
    return jsonify(output)


