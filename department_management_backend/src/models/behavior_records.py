from department_management_backend.src.database import db

class BehaviorRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainee_id = db.Column(db.Integer, nullable=False) # Assuming trainee_id from Rayat or internal system
    behavior_type = db.Column(db.String(100), nullable=False) # e.g., 'عدم التزام باللبس الرسمي', 'تدخين'
    description = db.Column(db.Text, nullable=True)
    date_recorded = db.Column(db.DateTime, default=db.func.current_timestamp())
    recorded_by_trainer_id = db.Column(db.Integer, nullable=False) # ID of the trainer who recorded the behavior

    def __repr__(self):
        return f'<BehaviorRecord {self.behavior_type} for Trainee {self.trainee_id}>'


