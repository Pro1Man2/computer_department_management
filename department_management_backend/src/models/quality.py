from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from enum import Enum
import json

db = SQLAlchemy()

class QualityStandard(db.Model):
    """معايير الجودة"""
    __tablename__ = 'quality_standards'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # رمز المعيار
    name = db.Column(db.String(200), nullable=False)  # اسم المعيار
    description = db.Column(db.Text)  # وصف المعيار
    category = db.Column(db.String(100))  # فئة المعيار
    target_value = db.Column(db.Float)  # القيمة المستهدفة
    measurement_unit = db.Column(db.String(50))  # وحدة القياس
    measurement_method = db.Column(db.Text)  # طريقة القياس
    responsible_person = db.Column(db.String(200))  # المسؤول عن المتابعة
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    indicators = db.relationship('QualityIndicator', backref='standard', lazy='dynamic', cascade='all, delete-orphan')
    measurements = db.relationship('QualityMeasurement', backref='standard', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'target_value': self.target_value,
            'measurement_unit': self.measurement_unit,
            'measurement_method': self.measurement_method,
            'responsible_person': self.responsible_person,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class QualityIndicator(db.Model):
    """مؤشرات الجودة"""
    __tablename__ = 'quality_indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    standard_id = db.Column(db.Integer, db.ForeignKey('quality_standards.id'), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    calculation_formula = db.Column(db.Text)  # صيغة الحساب
    data_source = db.Column(db.String(100))  # مصدر البيانات
    frequency = db.Column(db.String(50))  # تكرار القياس
    target_value = db.Column(db.Float)
    warning_threshold = db.Column(db.Float)  # عتبة التحذير
    critical_threshold = db.Column(db.Float)  # العتبة الحرجة
    weight = db.Column(db.Float, default=1.0)  # الوزن النسبي
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    measurements = db.relationship('QualityMeasurement', backref='indicator', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'standard_id': self.standard_id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'calculation_formula': self.calculation_formula,
            'data_source': self.data_source,
            'frequency': self.frequency,
            'target_value': self.target_value,
            'warning_threshold': self.warning_threshold,
            'critical_threshold': self.critical_threshold,
            'weight': self.weight,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class QualityMeasurement(db.Model):
    """قياسات الجودة"""
    __tablename__ = 'quality_measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    standard_id = db.Column(db.Integer, db.ForeignKey('quality_standards.id'), nullable=False)
    indicator_id = db.Column(db.Integer, db.ForeignKey('quality_indicators.id'), nullable=False)
    measurement_date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    data_source = db.Column(db.String(200))  # مصدر البيانات المحدد
    measured_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'standard_id': self.standard_id,
            'indicator_id': self.indicator_id,
            'measurement_date': self.measurement_date.isoformat(),
            'value': self.value,
            'notes': self.notes,
            'data_source': self.data_source,
            'measured_by': self.measured_by,
            'verified_by': self.verified_by,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat()
        }

class ReportTemplate(db.Model):
    """قوالب التقارير"""
    __tablename__ = 'report_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    template_config = db.Column(db.Text)  # تكوين القالب بصيغة JSON
    output_format = db.Column(db.String(20), default='pdf')  # pdf, excel, word
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    generated_reports = db.relationship('GeneratedReport', backref='template', lazy='dynamic')
    
    def get_config(self):
        """الحصول على تكوين القالب"""
        if self.template_config:
            return json.loads(self.template_config)
        return {}
    
    def set_config(self, config):
        """تحديد تكوين القالب"""
        self.template_config = json.dumps(config, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'template_config': self.get_config(),
            'output_format': self.output_format,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class GeneratedReport(db.Model):
    """التقارير المُنشأة"""
    __tablename__ = 'generated_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('report_templates.id'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.Text)  # معاملات التقرير بصيغة JSON
    file_path = db.Column(db.String(500))  # مسار الملف
    file_size = db.Column(db.Integer)  # حجم الملف بالبايت
    status = db.Column(db.String(20), default='pending')  # pending, generating, completed, failed
    error_message = db.Column(db.Text)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def get_parameters(self):
        """الحصول على معاملات التقرير"""
        if self.parameters:
            return json.loads(self.parameters)
        return {}
    
    def set_parameters(self, params):
        """تحديد معاملات التقرير"""
        self.parameters = json.dumps(params, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'title': self.title,
            'description': self.description,
            'parameters': self.get_parameters(),
            'file_path': self.file_path,
            'file_size': self.file_size,
            'status': self.status,
            'error_message': self.error_message,
            'generated_by': self.generated_by,
            'generated_at': self.generated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class RayatImport(db.Model):
    """استيراد بيانات رايات"""
    __tablename__ = 'rayat_imports'
    
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(300), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, csv
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    import_type = db.Column(db.String(50))  # attendance, grades, schedules, etc.
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    records_processed = db.Column(db.Integer, default=0)
    records_success = db.Column(db.Integer, default=0)
    records_failed = db.Column(db.Integer, default=0)
    error_log = db.Column(db.Text)
    imported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'import_type': self.import_type,
            'status': self.status,
            'records_processed': self.records_processed,
            'records_success': self.records_success,
            'records_failed': self.records_failed,
            'error_log': self.error_log,
            'imported_by': self.imported_by,
            'imported_at': self.imported_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class KPI(db.Model):
    """مؤشرات الأداء الرئيسية"""
    __tablename__ = 'kpis'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # academic, operational, satisfaction, quality
    calculation_method = db.Column(db.Text)  # طريقة الحساب
    data_sources = db.Column(db.Text)  # مصادر البيانات بصيغة JSON
    target_value = db.Column(db.Float)
    warning_threshold = db.Column(db.Float)
    critical_threshold = db.Column(db.Float)
    measurement_frequency = db.Column(db.String(50))  # daily, weekly, monthly, quarterly, yearly
    responsible_person = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    values = db.relationship('KPIValue', backref='kpi', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_data_sources(self):
        """الحصول على مصادر البيانات"""
        if self.data_sources:
            return json.loads(self.data_sources)
        return []
    
    def set_data_sources(self, sources):
        """تحديد مصادر البيانات"""
        self.data_sources = json.dumps(sources, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'calculation_method': self.calculation_method,
            'data_sources': self.get_data_sources(),
            'target_value': self.target_value,
            'warning_threshold': self.warning_threshold,
            'critical_threshold': self.critical_threshold,
            'measurement_frequency': self.measurement_frequency,
            'responsible_person': self.responsible_person,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class KPIValue(db.Model):
    """قيم مؤشرات الأداء"""
    __tablename__ = 'kpi_values'
    
    id = db.Column(db.Integer, primary_key=True)
    kpi_id = db.Column(db.Integer, db.ForeignKey('kpis.id'), nullable=False)
    measurement_date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    target_value = db.Column(db.Float)  # الهدف في هذا التاريخ
    notes = db.Column(db.Text)
    data_source = db.Column(db.String(200))
    calculated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'kpi_id': self.kpi_id,
            'measurement_date': self.measurement_date.isoformat(),
            'value': self.value,
            'target_value': self.target_value,
            'notes': self.notes,
            'data_source': self.data_source,
            'calculated_by': self.calculated_by,
            'verified_by': self.verified_by,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat()
        }

def init_default_quality_standards():
    """تهيئة معايير الجودة الافتراضية"""
    
    default_standards = [
        {
            'code': 'QS001',
            'name': 'نسبة حضور المتدربين',
            'description': 'نسبة حضور المتدربين للمحاضرات النظرية والعملية',
            'category': 'الأداء الأكاديمي',
            'target_value': 85.0,
            'measurement_unit': '%',
            'measurement_method': 'حساب نسبة الحضور من إجمالي الساعات المقررة',
            'responsible_person': 'مشرف المتدربين'
        },
        {
            'code': 'QS002',
            'name': 'نسبة نجاح المتدربين',
            'description': 'نسبة المتدربين الناجحين في المقررات التخصصية',
            'category': 'الأداء الأكاديمي',
            'target_value': 80.0,
            'measurement_unit': '%',
            'measurement_method': 'حساب نسبة الناجحين من إجمالي المتدربين',
            'responsible_person': 'لجنة الجودة'
        },
        {
            'code': 'QS003',
            'name': 'رضا المتدربين',
            'description': 'مستوى رضا المتدربين عن جودة التدريب',
            'category': 'رضا المستفيدين',
            'target_value': 4.0,
            'measurement_unit': 'من 5',
            'measurement_method': 'استبيان رضا المتدربين',
            'responsible_person': 'لجنة الجودة'
        },
        {
            'code': 'QS004',
            'name': 'كفاءة استخدام المعامل',
            'description': 'نسبة استخدام المعامل والقاعات التدريبية',
            'category': 'الكفاءة التشغيلية',
            'target_value': 75.0,
            'measurement_unit': '%',
            'measurement_method': 'حساب ساعات الاستخدام الفعلي من إجمالي الساعات المتاحة',
            'responsible_person': 'مشرف الجداول'
        },
        {
            'code': 'QS005',
            'name': 'نسبة المدربين المؤهلين',
            'description': 'نسبة المدربين الحاصلين على مؤهلات مناسبة',
            'category': 'جودة الموارد البشرية',
            'target_value': 90.0,
            'measurement_unit': '%',
            'measurement_method': 'حساب نسبة المدربين المؤهلين من إجمالي المدربين',
            'responsible_person': 'رئيس القسم'
        }
    ]
    
    for standard_data in default_standards:
        existing = QualityStandard.query.filter_by(code=standard_data['code']).first()
        if not existing:
            standard = QualityStandard(**standard_data)
            db.session.add(standard)
    
    db.session.commit()

def init_default_kpis():
    """تهيئة مؤشرات الأداء الافتراضية"""
    
    default_kpis = [
        {
            'code': 'KPI001',
            'name': 'معدل الحضور الشهري',
            'description': 'متوسط نسبة حضور المتدربين شهرياً',
            'category': 'academic',
            'target_value': 85.0,
            'warning_threshold': 80.0,
            'critical_threshold': 75.0,
            'measurement_frequency': 'monthly',
            'responsible_person': 'مشرف المتدربين'
        },
        {
            'code': 'KPI002',
            'name': 'معدل النجاح الفصلي',
            'description': 'نسبة نجاح المتدربين في نهاية كل فصل تدريبي',
            'category': 'academic',
            'target_value': 80.0,
            'warning_threshold': 75.0,
            'critical_threshold': 70.0,
            'measurement_frequency': 'quarterly',
            'responsible_person': 'لجنة الجودة'
        },
        {
            'code': 'KPI003',
            'name': 'رضا المتدربين',
            'description': 'مؤشر رضا المتدربين عن جودة التدريب',
            'category': 'satisfaction',
            'target_value': 4.0,
            'warning_threshold': 3.5,
            'critical_threshold': 3.0,
            'measurement_frequency': 'quarterly',
            'responsible_person': 'لجنة الجودة'
        },
        {
            'code': 'KPI004',
            'name': 'كفاءة استخدام المرافق',
            'description': 'نسبة استخدام القاعات والمعامل',
            'category': 'operational',
            'target_value': 75.0,
            'warning_threshold': 70.0,
            'critical_threshold': 65.0,
            'measurement_frequency': 'monthly',
            'responsible_person': 'مشرف الجداول'
        },
        {
            'code': 'KPI005',
            'name': 'نسبة التخرج في الوقت المحدد',
            'description': 'نسبة المتدربين الذين يتخرجون في الوقت المحدد',
            'category': 'academic',
            'target_value': 85.0,
            'warning_threshold': 80.0,
            'critical_threshold': 75.0,
            'measurement_frequency': 'yearly',
            'responsible_person': 'رئيس القسم'
        }
    ]
    
    for kpi_data in default_kpis:
        existing = KPI.query.filter_by(code=kpi_data['code']).first()
        if not existing:
            kpi = KPI(**kpi_data)
            db.session.add(kpi)
    
    db.session.commit()

