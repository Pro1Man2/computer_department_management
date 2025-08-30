from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    DEPARTMENT_HEAD = "department_head"
    COMMITTEE_MEMBER = "committee_member"
    TRAINER = "trainer"
    SCHEDULE_SUPERVISOR = "schedule_supervisor"
    TRAINEE_SUPERVISOR = "trainee_supervisor"
    QUALITY_COMMITTEE = "quality_committee"
    ACADEMIC_GUIDANCE = "academic_guidance"
    TALENT_COMMITTEE = "talent_committee"
    SAFETY_COMMITTEE = "safety_committee"

class Permission(Enum):
    # إدارة المستخدمين
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    
    # إدارة التقارير
    GENERATE_REPORTS = "generate_reports"
    VIEW_REPORTS = "view_reports"
    
    # إدارة المبادرات
    MANAGE_INITIATIVES = "manage_initiatives"
    VIEW_INITIATIVES = "view_initiatives"
    
    # إدارة سلوكيات المتدربين
    MANAGE_TRAINEE_BEHAVIOR = "manage_trainee_behavior"
    VIEW_TRAINEE_BEHAVIOR = "view_trainee_behavior"
    
    # إدارة الجودة
    MANAGE_QUALITY = "manage_quality"
    VIEW_QUALITY = "view_quality"
    
    # إدارة الجداول
    MANAGE_SCHEDULES = "manage_schedules"
    VIEW_SCHEDULES = "view_schedules"
    
    # إدارة المتدربين
    MANAGE_TRAINEES = "manage_trainees"
    VIEW_TRAINEES = "view_trainees"
    
    # إدارة الاستبيانات
    MANAGE_SURVEYS = "manage_surveys"
    VIEW_SURVEYS = "view_surveys"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    position = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    roles = db.relationship('UserRole', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    permissions = db.relationship('UserPermission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """تشفير كلمة المرور"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        """التحقق من وجود دور معين"""
        return self.roles.filter_by(role=role.value).first() is not None
    
    def has_permission(self, permission):
        """التحقق من وجود صلاحية معينة"""
        # التحقق من الصلاحيات المباشرة
        if self.permissions.filter_by(permission=permission.value).first():
            return True
        
        # التحقق من الصلاحيات المرتبطة بالأدوار
        for user_role in self.roles:
            role_permissions = RolePermission.query.filter_by(role=user_role.role).all()
            for role_perm in role_permissions:
                if role_perm.permission == permission.value:
                    return True
        
        return False
    
    def generate_token(self, secret_key, expires_in=3600):
        """إنشاء JWT token"""
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_token(token, secret_key):
        """التحقق من JWT token"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return User.query.get(payload['user_id'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def to_dict(self):
        """تحويل المستخدم إلى قاموس"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'national_id': self.national_id,
            'phone': self.phone,
            'department': self.department,
            'specialization': self.specialization,
            'position': self.position,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'roles': [role.role for role in self.roles],
            'permissions': [perm.permission for perm in self.permissions]
        }

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class UserPermission(db.Model):
    __tablename__ = 'user_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission = db.Column(db.String(50), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    permission = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100))
    resource_id = db.Column(db.String(50))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat()
        }

def init_default_roles_permissions():
    """تهيئة الأدوار والصلاحيات الافتراضية"""
    
    # صلاحيات رئيس القسم - صلاحيات كاملة
    department_head_permissions = [perm.value for perm in Permission]
    
    # صلاحيات لجنة الجودة
    quality_committee_permissions = [
        Permission.MANAGE_QUALITY.value,
        Permission.VIEW_QUALITY.value,
        Permission.GENERATE_REPORTS.value,
        Permission.VIEW_REPORTS.value,
        Permission.VIEW_TRAINEES.value,
        Permission.VIEW_SURVEYS.value
    ]
    
    # صلاحيات لجنة الإرشاد الأكاديمي
    academic_guidance_permissions = [
        Permission.MANAGE_TRAINEE_BEHAVIOR.value,
        Permission.VIEW_TRAINEE_BEHAVIOR.value,
        Permission.MANAGE_TRAINEES.value,
        Permission.VIEW_TRAINEES.value,
        Permission.VIEW_REPORTS.value
    ]
    
    # صلاحيات لجنة رعاية الموهوبين
    talent_committee_permissions = [
        Permission.VIEW_TRAINEES.value,
        Permission.MANAGE_INITIATIVES.value,
        Permission.VIEW_INITIATIVES.value,
        Permission.VIEW_REPORTS.value
    ]
    
    # صلاحيات المدربين
    trainer_permissions = [
        Permission.VIEW_TRAINEES.value,
        Permission.MANAGE_TRAINEE_BEHAVIOR.value,
        Permission.VIEW_TRAINEE_BEHAVIOR.value,
        Permission.VIEW_SCHEDULES.value,
        Permission.VIEW_SURVEYS.value
    ]
    
    # صلاحيات مشرف الجداول
    schedule_supervisor_permissions = [
        Permission.MANAGE_SCHEDULES.value,
        Permission.VIEW_SCHEDULES.value,
        Permission.VIEW_TRAINEES.value,
        Permission.VIEW_REPORTS.value
    ]
    
    # صلاحيات مشرف المتدربين
    trainee_supervisor_permissions = [
        Permission.MANAGE_TRAINEES.value,
        Permission.VIEW_TRAINEES.value,
        Permission.MANAGE_TRAINEE_BEHAVIOR.value,
        Permission.VIEW_TRAINEE_BEHAVIOR.value,
        Permission.VIEW_REPORTS.value
    ]
    
    # إنشاء الأدوار والصلاحيات
    role_permission_mapping = {
        UserRole.DEPARTMENT_HEAD.value: department_head_permissions,
        UserRole.QUALITY_COMMITTEE.value: quality_committee_permissions,
        UserRole.ACADEMIC_GUIDANCE.value: academic_guidance_permissions,
        UserRole.TALENT_COMMITTEE.value: talent_committee_permissions,
        UserRole.TRAINER.value: trainer_permissions,
        UserRole.SCHEDULE_SUPERVISOR.value: schedule_supervisor_permissions,
        UserRole.TRAINEE_SUPERVISOR.value: trainee_supervisor_permissions
    }
    
    for role, permissions in role_permission_mapping.items():
        for permission in permissions:
            existing = RolePermission.query.filter_by(role=role, permission=permission).first()
            if not existing:
                role_perm = RolePermission(role=role, permission=permission)
                db.session.add(role_perm)
    
    db.session.commit()

