from flask import Blueprint, jsonify

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard/kpis", methods=["GET"])
def get_kpis():
    # Placeholder for fetching KPI data
    # This would involve querying various models (e.g., Quality, BehaviorRecord, SurveyResponse)
    # and performing aggregations.
    kpis = {
        "graduation_rate": "85%",
        "success_rate_critical_courses": "70%",
        "trainer_satisfaction": "4.5/5",
        "trainee_satisfaction": "4.2/5",
        "behavior_incidents_per_month": 15
    }
    return jsonify(kpis)

@dashboard_bp.route("/dashboard/statistics", methods=["GET"])
def get_statistics():
    # Placeholder for fetching general statistics
    statistics = {
        "total_trainees": 1425,
        "total_trainers": 48,
        "trainees_by_specialization": {
            "Programming": 443,
            "Technical Support": 455,
            "Networking": 527
        },
        "critical_courses_enrollment": {
            "Operating Systems 1": 300, # Example data
            "Algorithms and Logic": 250 # Example data
        }
    }
    return jsonify(statistics)


