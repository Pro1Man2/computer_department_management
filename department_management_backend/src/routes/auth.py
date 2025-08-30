from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from datetime import datetime
import re
from functools import wraps

from src.models.auth import db, User, UserRole, UserPermission, AuditLog, Permission, init_default_roles_permissions

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """ديكوريتر للتحقق من وجود token صالح"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token مطلوب'}), 401
        
        try:
            # إزالة "Bearer " من بداية التوكن
            if token.startswith('Bearer '):
                token = token[7:]
            
            current_user = User.verify_token(token, current_app.config['SECRET_KEY'])
            if not current_user:
                return jsonify({'message': 'Token غير صالح'}), 401
            
            if not current_user.is_active:
                return jsonify({'message': 'الحساب غير مفعل'}), 401
            
        except Exception as e:
            return jsonify({'message': 'Token غير صالح'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def permission_required(permission):
    """ديكوريتر للتحقق من وجود صلاحية معينة"""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if not current_user.has_permission(permission):
                log_audit(current_user.id, 'PERMISSION_DENIED', 'permission', permission.value, 
                         f'محاولة وصول غير مصرح به للصلاحية: {permission.value}')
                return jsonify({'message': 'ليس لديك صلاحية للوصول لهذا المورد'}), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated
    return decorator

def log_audit(user_id, action, resource=None, resource_id=None, details=None):
    """تسجيل العمليات في سجل المراجعة"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"خطأ في تسجيل المراجعة: {e}")

def validate_password(password):
    """التحقق من قوة كلمة المرور"""
    if len(password) < 8:
        return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
    
    if not re.search(r"[A-Z]", password):
        return False, "كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل"
    
    if not re.search(r"[a-z]", password):
        return False, "كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل"
    
    if not re.search(r"\d", password):
        return False, "كلمة المرور يجب أن تحتوي على رقم واحد على الأقل"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل"
    
    return True, "كلمة مرور قوية"

@auth_bp.route('/login', methods=['POST'])
def login():
    """تسجيل الدخول"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # البحث عن المستخدم
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            log_audit(user.id if user else None, 'LOGIN_FAILED', 'user', username, 
                     f'محاولة تسجيل دخول فاشلة لاسم المستخدم: {username}')
            return jsonify({'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
        
        if not user.is_active:
            log_audit(user.id, 'LOGIN_FAILED', 'user', username, 'محاولة تسجيل دخول لحساب غير مفعل')
            return jsonify({'message': 'الحساب غير مفعل'}), 401
        
        # تحديث آخر تسجيل دخول
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # إنشاء التوكن
        token = user.generate_token(current_app.config['SECRET_KEY'])
        
        log_audit(user.id, 'LOGIN_SUCCESS', 'user', username, 'تسجيل دخول ناجح')
        
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@auth_bp.route('/register', methods=['POST'])
@token_required
@permission_required(Permission.MANAGE_USERS)
def register(current_user):
    """تسجيل مستخدم جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['username', 'email', 'password', 'full_name', 'national_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} مطلوب'}), 400
        
        # التحقق من قوة كلمة المرور
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # التحقق من عدم وجود المستخدم مسبقاً
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'اسم المستخدم موجود مسبقاً'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        if User.query.filter_by(national_id=data['national_id']).first():
            return jsonify({'message': 'رقم الهوية موجود مسبقاً'}), 400
        
        # إنشاء المستخدم الجديد
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            national_id=data['national_id'],
            phone=data.get('phone'),
            department=data.get('department'),
            specialization=data.get('specialization'),
            position=data.get('position'),
            hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else None
        )
        
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # للحصول على ID المستخدم
        
        # إضافة الأدوار إذا تم تحديدها
        if data.get('roles'):
            for role in data['roles']:
                user_role = UserRole(user_id=user.id, role=role, assigned_by=current_user.id)
                db.session.add(user_role)
        
        # إضافة الصلاحيات الإضافية إذا تم تحديدها
        if data.get('permissions'):
            for permission in data['permissions']:
                user_permission = UserPermission(user_id=user.id, permission=permission, assigned_by=current_user.id)
                db.session.add(user_permission)
        
        db.session.commit()
        
        log_audit(current_user.id, 'USER_CREATED', 'user', str(user.id), 
                 f'تم إنشاء مستخدم جديد: {user.username}')
        
        return jsonify({
            'message': 'تم إنشاء المستخدم بنجاح',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """الحصول على معلومات المستخدم الحالي"""
    return jsonify({
        'user': current_user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """تحديث معلومات المستخدم الحالي"""
    try:
        data = request.get_json()
        
        # الحقول المسموح بتحديثها
        allowed_fields = ['full_name', 'email', 'phone']
        
        for field in allowed_fields:
            if field in data:
                setattr(current_user, field, data[field])
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_audit(current_user.id, 'PROFILE_UPDATED', 'user', str(current_user.id), 
                 'تم تحديث الملف الشخصي')
        
        return jsonify({
            'message': 'تم تحديث الملف الشخصي بنجاح',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """تغيير كلمة المرور"""
    try:
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'message': 'كلمة المرور الحالية والجديدة مطلوبتان'}), 400
        
        # التحقق من كلمة المرور الحالية
        if not current_user.check_password(data['current_password']):
            log_audit(current_user.id, 'PASSWORD_CHANGE_FAILED', 'user', str(current_user.id), 
                     'محاولة تغيير كلمة مرور بكلمة مرور حالية خاطئة')
            return jsonify({'message': 'كلمة المرور الحالية غير صحيحة'}), 400
        
        # التحقق من قوة كلمة المرور الجديدة
        is_valid, message = validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # تحديث كلمة المرور
        current_user.set_password(data['new_password'])
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_audit(current_user.id, 'PASSWORD_CHANGED', 'user', str(current_user.id), 
                 'تم تغيير كلمة المرور بنجاح')
        
        return jsonify({'message': 'تم تغيير كلمة المرور بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@auth_bp.route('/users', methods=['GET'])
@token_required
@permission_required(Permission.VIEW_USERS)
def get_users(current_user):
    """الحصول على قائمة المستخدمين"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.contains(search),
                    User.full_name.contains(search),
                    User.email.contains(search),
                    User.national_id.contains(search)
                )
            )
        
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@auth_bp.route('/init-system', methods=['POST'])
def init_system():
    """تهيئة النظام وإنشاء المدير الأول"""
    try:
        # التحقق من عدم وجود مستخدمين مسبقاً
        if User.query.count() > 0:
            return jsonify({'message': 'النظام مهيأ مسبقاً'}), 400
        
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['username', 'email', 'password', 'full_name', 'national_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} مطلوب'}), 400
        
        # التحقق من قوة كلمة المرور
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # تهيئة الأدوار والصلاحيات الافتراضية
        init_default_roles_permissions()
        
        # إنشاء المدير الأول
        admin_user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            national_id=data['national_id'],
            phone=data.get('phone'),
            department='قسم تقنية الحاسب الآلي والمعلومات',
            position='رئيس القسم'
        )
        
        admin_user.set_password(data['password'])
        
        db.session.add(admin_user)
        db.session.flush()
        
        # إضافة دور رئيس القسم
        admin_role = UserRole(
            user_id=admin_user.id, 
            role='department_head',
            assigned_by=admin_user.id
        )
        db.session.add(admin_role)
        
        db.session.commit()
        
        log_audit(admin_user.id, 'SYSTEM_INITIALIZED', 'system', 'init', 
                 'تم تهيئة النظام وإنشاء المدير الأول')
        
        return jsonify({
            'message': 'تم تهيئة النظام بنجاح',
            'user': admin_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

