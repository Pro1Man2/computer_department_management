from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from enum import Enum
import json

db = SQLAlchemy()

class InitiativeStatus(Enum):
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    APPROVED = 'approved'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    ON_HOLD = 'on_hold'

class InitiativeType(Enum):
    ACADEMIC = 'academic'
    TECHNICAL = 'technical'
    ADMINISTRATIVE = 'administrative'
    COMMUNITY = 'community'
    QUALITY = 'quality'

class Initiative(db.Model):
    """المبادرات"""
    __tablename__ = 'initiatives'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.Enum(InitiativeType), nullable=False)
    status = db.Column(db.Enum(InitiativeStatus), default=InitiativeStatus.DRAFT)
    objectives = db.Column(db.Text)  # الأهداف بصيغة JSON
    expected_outcomes = db.Column(db.Text)  # المخرجات المتوقعة
    target_audience = db.Column(db.String(200))  # الجمهور المستهدف
    required_resources = db.Column(db.Text)  # الموارد المطلوبة بصيغة JSON
    budget = db.Column(db.Float, default=0.0)
    actual_cost = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    progress_percentage = db.Column(db.Float, default=0.0)
    success_criteria = db.Column(db.Text)  # معايير النجاح
    risks = db.Column(db.Text)  # المخاطر بصيغة JSON
    mitigation_plans = db.Column(db.Text)  # خطط التخفيف
    
    # المسؤوليات
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # صاحب المبادرة
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # مدير المبادرة
    sponsor_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # راعي المبادرة
    
    # التواريخ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # العلاقات
    tasks = db.relationship('InitiativeTask', backref='initiative', lazy='dynamic', cascade='all, delete-orphan')
    milestones = db.relationship('InitiativeMilestone', backref='initiative', lazy='dynamic', cascade='all, delete-orphan')
    updates = db.relationship('InitiativeUpdate', backref='initiative', lazy='dynamic', cascade='all, delete-orphan')
    team_members = db.relationship('InitiativeTeamMember', backref='initiative', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_objectives(self):
        """الحصول على الأهداف"""
        if self.objectives:
            return json.loads(self.objectives)
        return []
    
    def set_objectives(self, objectives):
        """تحديد الأهداف"""
        self.objectives = json.dumps(objectives, ensure_ascii=False)
    
    def get_required_resources(self):
        """الحصول على الموارد المطلوبة"""
        if self.required_resources:
            return json.loads(self.required_resources)
        return {}
    
    def set_required_resources(self, resources):
        """تحديد الموارد المطلوبة"""
        self.required_resources = json.dumps(resources, ensure_ascii=False)
    
    def get_risks(self):
        """الحصول على المخاطر"""
        if self.risks:
            return json.loads(self.risks)
        return []
    
    def set_risks(self, risks):
        """تحديد المخاطر"""
        self.risks = json.dumps(risks, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type.value if self.type else None,
            'status': self.status.value if self.status else None,
            'objectives': self.get_objectives(),
            'expected_outcomes': self.expected_outcomes,
            'target_audience': self.target_audience,
            'required_resources': self.get_required_resources(),
            'budget': self.budget,
            'actual_cost': self.actual_cost,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'progress_percentage': self.progress_percentage,
            'success_criteria': self.success_criteria,
            'risks': self.get_risks(),
            'mitigation_plans': self.mitigation_plans,
            'owner_id': self.owner_id,
            'manager_id': self.manager_id,
            'sponsor_id': self.sponsor_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by
        }

class InitiativeTask(db.Model):
    """مهام المبادرة"""
    __tablename__ = 'initiative_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    initiative_id = db.Column(db.Integer, db.ForeignKey('initiatives.id'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    progress_percentage = db.Column(db.Float, default=0.0)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    dependencies = db.Column(db.Text)  # المهام التابعة بصيغة JSON
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'initiative_id': self.initiative_id,
            'title': self.title,
            'description': self.description,
            'assigned_to': self.assigned_to,
            'status': self.status,
            'priority': self.priority,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'progress_percentage': self.progress_percentage,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'dependencies': json.loads(self.dependencies) if self.dependencies else [],
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class BehaviorType(Enum):
    POSITIVE = 'positive'
    NEGATIVE = 'negative'

class BehaviorCategory(Enum):
    ACADEMIC = 'academic'
    DISCIPLINARY = 'disciplinary'
    ETHICAL = 'ethical'
    SAFETY = 'safety'
    SOCIAL = 'social'

class BehaviorRecord(db.Model):
    """سجلات السلوك"""
    __tablename__ = 'behavior_records'
    
    id = db.Column(db.Integer, primary_key=True)
    trainee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    behavior_type = db.Column(db.Enum(BehaviorType), nullable=False)
    category = db.Column(db.Enum(BehaviorCategory), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    severity_level = db.Column(db.Integer, default=1)  # 1-5 (1=خفيف، 5=شديد)
    location = db.Column(db.String(200))  # مكان الحادثة
    incident_date = db.Column(db.DateTime, nullable=False)
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    witnesses = db.Column(db.Text)  # الشهود بصيغة JSON
    evidence_files = db.Column(db.Text)  # ملفات الأدلة بصيغة JSON
    action_taken = db.Column(db.Text)  # الإجراء المتخذ
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    follow_up_notes = db.Column(db.Text)
    points_awarded = db.Column(db.Integer, default=0)  # النقاط الممنوحة (للسلوك الإيجابي)
    points_deducted = db.Column(db.Integer, default=0)  # النقاط المخصومة (للسلوك السلبي)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_witnesses(self):
        """الحصول على قائمة الشهود"""
        if self.witnesses:
            return json.loads(self.witnesses)
        return []
    
    def set_witnesses(self, witnesses):
        """تحديد قائمة الشهود"""
        self.witnesses = json.dumps(witnesses, ensure_ascii=False)
    
    def get_evidence_files(self):
        """الحصول على ملفات الأدلة"""
        if self.evidence_files:
            return json.loads(self.evidence_files)
        return []
    
    def set_evidence_files(self, files):
        """تحديد ملفات الأدلة"""
        self.evidence_files = json.dumps(files, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trainee_id': self.trainee_id,
            'behavior_type': self.behavior_type.value if self.behavior_type else None,
            'category': self.category.value if self.category else None,
            'title': self.title,
            'description': self.description,
            'severity_level': self.severity_level,
            'location': self.location,
            'incident_date': self.incident_date.isoformat(),
            'reported_by': self.reported_by,
            'witnesses': self.get_witnesses(),
            'evidence_files': self.get_evidence_files(),
            'action_taken': self.action_taken,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'follow_up_notes': self.follow_up_notes,
            'points_awarded': self.points_awarded,
            'points_deducted': self.points_deducted,
            'is_resolved': self.is_resolved,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Survey(db.Model):
    """الاستبيانات"""
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # course_evaluation, satisfaction, feedback, etc.
    target_audience = db.Column(db.String(200))  # trainees, trainers, staff, all
    is_anonymous = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    max_responses = db.Column(db.Integer)  # الحد الأقصى للاستجابات
    response_count = db.Column(db.Integer, default=0)
    instructions = db.Column(db.Text)  # تعليمات الاستبيان
    thank_you_message = db.Column(db.Text)  # رسالة الشكر
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    questions = db.relationship('SurveyQuestion', backref='survey', lazy='dynamic', cascade='all, delete-orphan')
    responses = db.relationship('SurveyResponse', backref='survey', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'target_audience': self.target_audience,
            'is_anonymous': self.is_anonymous,
            'is_active': self.is_active,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'max_responses': self.max_responses,
            'response_count': self.response_count,
            'instructions': self.instructions,
            'thank_you_message': self.thank_you_message,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class QuestionType(Enum):
    MULTIPLE_CHOICE = 'multiple_choice'
    SINGLE_CHOICE = 'single_choice'
    TEXT = 'text'
    TEXTAREA = 'textarea'
    RATING = 'rating'
    SCALE = 'scale'
    YES_NO = 'yes_no'
    DATE = 'date'
    NUMBER = 'number'

class SurveyQuestion(db.Model):
    """أسئلة الاستبيان"""
    __tablename__ = 'survey_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum(QuestionType), nullable=False)
    options = db.Column(db.Text)  # خيارات الإجابة بصيغة JSON
    is_required = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    conditions = db.Column(db.Text)  # شروط إظهار السؤال بصيغة JSON
    help_text = db.Column(db.Text)  # نص المساعدة
    validation_rules = db.Column(db.Text)  # قواعد التحقق بصيغة JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    answers = db.relationship('SurveyAnswer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_options(self):
        """الحصول على خيارات الإجابة"""
        if self.options:
            return json.loads(self.options)
        return []
    
    def set_options(self, options):
        """تحديد خيارات الإجابة"""
        self.options = json.dumps(options, ensure_ascii=False)
    
    def get_conditions(self):
        """الحصول على شروط إظهار السؤال"""
        if self.conditions:
            return json.loads(self.conditions)
        return {}
    
    def set_conditions(self, conditions):
        """تحديد شروط إظهار السؤال"""
        self.conditions = json.dumps(conditions, ensure_ascii=False)
    
    def get_validation_rules(self):
        """الحصول على قواعد التحقق"""
        if self.validation_rules:
            return json.loads(self.validation_rules)
        return {}
    
    def set_validation_rules(self, rules):
        """تحديد قواعد التحقق"""
        self.validation_rules = json.dumps(rules, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
            'question_text': self.question_text,
            'question_type': self.question_type.value if self.question_type else None,
            'options': self.get_options(),
            'is_required': self.is_required,
            'order_index': self.order_index,
            'conditions': self.get_conditions(),
            'help_text': self.help_text,
            'validation_rules': self.get_validation_rules(),
            'created_at': self.created_at.isoformat()
        }

class SurveyResponse(db.Model):
    """استجابات الاستبيان"""
    __tablename__ = 'survey_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    respondent_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # null للاستبيانات المجهولة
    session_id = db.Column(db.String(100))  # معرف الجلسة للاستبيانات المجهولة
    is_completed = db.Column(db.Boolean, default=False)
    completion_time = db.Column(db.Integer)  # وقت الإكمال بالثواني
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # العلاقات
    answers = db.relationship('SurveyAnswer', backref='response', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
            'respondent_id': self.respondent_id,
            'session_id': self.session_id,
            'is_completed': self.is_completed,
            'completion_time': self.completion_time,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class SurveyAnswer(db.Model):
    """إجابات الاستبيان"""
    __tablename__ = 'survey_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_questions.id'), nullable=False)
    answer_text = db.Column(db.Text)  # الإجابة النصية
    answer_number = db.Column(db.Float)  # الإجابة الرقمية
    answer_date = db.Column(db.Date)  # الإجابة التاريخية
    selected_options = db.Column(db.Text)  # الخيارات المختارة بصيغة JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_selected_options(self):
        """الحصول على الخيارات المختارة"""
        if self.selected_options:
            return json.loads(self.selected_options)
        return []
    
    def set_selected_options(self, options):
        """تحديد الخيارات المختارة"""
        self.selected_options = json.dumps(options, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'response_id': self.response_id,
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'answer_number': self.answer_number,
            'answer_date': self.answer_date.isoformat() if self.answer_date else None,
            'selected_options': self.get_selected_options(),
            'created_at': self.created_at.isoformat()
        }

class Activity(db.Model):
    """الأنشطة والفعاليات"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # academic, cultural, social, volunteer
    type = db.Column(db.String(100))  # workshop, seminar, competition, trip, etc.
    objectives = db.Column(db.Text)  # الأهداف بصيغة JSON
    target_audience = db.Column(db.String(200))
    location = db.Column(db.String(300))
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    registration_start = db.Column(db.DateTime)
    registration_end = db.Column(db.DateTime)
    max_participants = db.Column(db.Integer)
    current_participants = db.Column(db.Integer, default=0)
    registration_requirements = db.Column(db.Text)  # متطلبات التسجيل
    budget = db.Column(db.Float, default=0.0)
    actual_cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='planned')  # planned, active, completed, cancelled
    is_public = db.Column(db.Boolean, default=True)
    requires_approval = db.Column(db.Boolean, default=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    registrations = db.relationship('ActivityRegistration', backref='activity', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_objectives(self):
        """الحصول على الأهداف"""
        if self.objectives:
            return json.loads(self.objectives)
        return []
    
    def set_objectives(self, objectives):
        """تحديد الأهداف"""
        self.objectives = json.dumps(objectives, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'type': self.type,
            'objectives': self.get_objectives(),
            'target_audience': self.target_audience,
            'location': self.location,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat(),
            'registration_start': self.registration_start.isoformat() if self.registration_start else None,
            'registration_end': self.registration_end.isoformat() if self.registration_end else None,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'registration_requirements': self.registration_requirements,
            'budget': self.budget,
            'actual_cost': self.actual_cost,
            'status': self.status,
            'is_public': self.is_public,
            'requires_approval': self.requires_approval,
            'organizer_id': self.organizer_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ActivityRegistration(db.Model):
    """تسجيلات الأنشطة"""
    __tablename__ = 'activity_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='registered')  # registered, approved, rejected, attended, absent
    notes = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'participant_id': self.participant_id,
            'registration_date': self.registration_date.isoformat(),
            'status': self.status,
            'notes': self.notes,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }

def init_default_behavior_templates():
    """تهيئة قوالب السلوكيات الافتراضية"""
    
    # هذه دالة مساعدة لإنشاء قوالب السلوكيات الشائعة
    # يمكن استخدامها لتسهيل تسجيل السلوكيات المتكررة
    pass

def init_default_survey_templates():
    """تهيئة قوالب الاستبيانات الافتراضية"""
    
    # قوالب استبيانات جاهزة مثل تقييم المقررات، رضا المتدربين، إلخ
    pass

