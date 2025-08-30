from flask import Blueprint, request, jsonify, current_app, send_file
from datetime import datetime, date, timedelta
import os
import pandas as pd
from werkzeug.utils import secure_filename
import json

from src.models.quality import (
    db, QualityStandard, QualityIndicator, QualityMeasurement,
    ReportTemplate, GeneratedReport, RayatImport, KPI, KPIValue,
    init_default_quality_standards, init_default_kpis
)
from src.routes.auth import token_required, permission_required, log_audit, Permission

quality_bp = Blueprint('quality', __name__)

# إعدادات رفع الملفات
UPLOAD_FOLDER = 'uploads/rayat'
ALLOWED_EXTENSIONS = {'pdf', 'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """التأكد من وجود مجلد الرفع"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@quality_bp.route('/standards', methods=['GET'])
@token_required
@permission_required(Permission.VIEW_QUALITY)
def get_quality_standards(current_user):
    """الحصول على معايير الجودة"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        query = QualityStandard.query
        
        if category:
            query = query.filter(QualityStandard.category == category)
        
        if search:
            query = query.filter(
                db.or_(
                    QualityStandard.name.contains(search),
                    QualityStandard.code.contains(search),
                    QualityStandard.description.contains(search)
                )
            )
        
        standards = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'standards': [standard.to_dict() for standard in standards.items],
            'total': standards.total,
            'pages': standards.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/standards', methods=['POST'])
@token_required
@permission_required(Permission.MANAGE_QUALITY)
def create_quality_standard(current_user):
    """إنشاء معيار جودة جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['code', 'name', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} مطلوب'}), 400
        
        # التحقق من عدم وجود المعيار مسبقاً
        if QualityStandard.query.filter_by(code=data['code']).first():
            return jsonify({'message': 'رمز المعيار موجود مسبقاً'}), 400
        
        standard = QualityStandard(
            code=data['code'],
            name=data['name'],
            description=data.get('description'),
            category=data['category'],
            target_value=data.get('target_value'),
            measurement_unit=data.get('measurement_unit'),
            measurement_method=data.get('measurement_method'),
            responsible_person=data.get('responsible_person')
        )
        
        db.session.add(standard)
        db.session.commit()
        
        log_audit(current_user.id, 'QUALITY_STANDARD_CREATED', 'quality_standard', str(standard.id),
                 f'تم إنشاء معيار جودة جديد: {standard.name}')
        
        return jsonify({
            'message': 'تم إنشاء معيار الجودة بنجاح',
            'standard': standard.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/kpis', methods=['GET'])
@token_required
@permission_required(Permission.VIEW_QUALITY)
def get_kpis(current_user):
    """الحصول على مؤشرات الأداء الرئيسية"""
    try:
        category = request.args.get('category', '')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = KPI.query
        
        if category:
            query = query.filter(KPI.category == category)
        
        if active_only:
            query = query.filter(KPI.is_active == True)
        
        kpis = query.all()
        
        # إضافة آخر قيمة لكل مؤشر
        kpis_data = []
        for kpi in kpis:
            kpi_dict = kpi.to_dict()
            
            # الحصول على آخر قيمة
            latest_value = KPIValue.query.filter_by(kpi_id=kpi.id)\
                .order_by(KPIValue.measurement_date.desc()).first()
            
            if latest_value:
                kpi_dict['latest_value'] = latest_value.to_dict()
            else:
                kpi_dict['latest_value'] = None
            
            kpis_data.append(kpi_dict)
        
        return jsonify({'kpis': kpis_data}), 200
        
    except Exception as e:
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/kpis/<int:kpi_id>/values', methods=['GET'])
@token_required
@permission_required(Permission.VIEW_QUALITY)
def get_kpi_values(current_user, kpi_id):
    """الحصول على قيم مؤشر أداء محدد"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 50, type=int)
        
        query = KPIValue.query.filter_by(kpi_id=kpi_id)
        
        if start_date:
            query = query.filter(KPIValue.measurement_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(KPIValue.measurement_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        values = query.order_by(KPIValue.measurement_date.desc()).limit(limit).all()
        
        return jsonify({
            'values': [value.to_dict() for value in values]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/kpis/<int:kpi_id>/values', methods=['POST'])
@token_required
@permission_required(Permission.MANAGE_QUALITY)
def add_kpi_value(current_user, kpi_id):
    """إضافة قيمة جديدة لمؤشر أداء"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('measurement_date') or data.get('value') is None:
            return jsonify({'message': 'تاريخ القياس والقيمة مطلوبان'}), 400
        
        # التحقق من وجود المؤشر
        kpi = KPI.query.get(kpi_id)
        if not kpi:
            return jsonify({'message': 'مؤشر الأداء غير موجود'}), 404
        
        measurement_date = datetime.strptime(data['measurement_date'], '%Y-%m-%d').date()
        
        # التحقق من عدم وجود قيمة في نفس التاريخ
        existing = KPIValue.query.filter_by(
            kpi_id=kpi_id,
            measurement_date=measurement_date
        ).first()
        
        if existing:
            return jsonify({'message': 'يوجد قيمة مسجلة في هذا التاريخ مسبقاً'}), 400
        
        kpi_value = KPIValue(
            kpi_id=kpi_id,
            measurement_date=measurement_date,
            value=data['value'],
            target_value=data.get('target_value', kpi.target_value),
            notes=data.get('notes'),
            data_source=data.get('data_source'),
            calculated_by=current_user.id
        )
        
        db.session.add(kpi_value)
        db.session.commit()
        
        log_audit(current_user.id, 'KPI_VALUE_ADDED', 'kpi_value', str(kpi_value.id),
                 f'تم إضافة قيمة جديدة لمؤشر الأداء: {kpi.name}')
        
        return jsonify({
            'message': 'تم إضافة قيمة المؤشر بنجاح',
            'value': kpi_value.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/rayat/upload', methods=['POST'])
@token_required
@permission_required(Permission.MANAGE_QUALITY)
def upload_rayat_file(current_user):
    """رفع ملف من نظام رايات"""
    try:
        ensure_upload_folder()
        
        if 'file' not in request.files:
            return jsonify({'message': 'لم يتم اختيار ملف'}), 400
        
        file = request.files['file']
        import_type = request.form.get('import_type', 'general')
        
        if file.filename == '':
            return jsonify({'message': 'لم يتم اختيار ملف'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'message': 'نوع الملف غير مدعوم'}), 400
        
        # حفظ الملف
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # إنشاء سجل الاستيراد
        rayat_import = RayatImport(
            file_name=file.filename,
            file_type=filename.rsplit('.', 1)[1].lower(),
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            import_type=import_type,
            imported_by=current_user.id
        )
        
        db.session.add(rayat_import)
        db.session.commit()
        
        log_audit(current_user.id, 'RAYAT_FILE_UPLOADED', 'rayat_import', str(rayat_import.id),
                 f'تم رفع ملف رايات: {file.filename}')
        
        # هنا يمكن إضافة معالجة الملف في الخلفية
        # process_rayat_file.delay(rayat_import.id)
        
        return jsonify({
            'message': 'تم رفع الملف بنجاح',
            'import': rayat_import.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/rayat/imports', methods=['GET'])
@token_required
@permission_required(Permission.VIEW_QUALITY)
def get_rayat_imports(current_user):
    """الحصول على قائمة استيرادات رايات"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        import_type = request.args.get('import_type', '')
        status = request.args.get('status', '')
        
        query = RayatImport.query
        
        if import_type:
            query = query.filter(RayatImport.import_type == import_type)
        
        if status:
            query = query.filter(RayatImport.status == status)
        
        imports = query.order_by(RayatImport.imported_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'imports': [imp.to_dict() for imp in imports.items],
            'total': imports.total,
            'pages': imports.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/reports/templates', methods=['GET'])
@token_required
@permission_required(Permission.VIEW_REPORTS)
def get_report_templates(current_user):
    """الحصول على قوالب التقارير"""
    try:
        category = request.args.get('category', '')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = ReportTemplate.query
        
        if category:
            query = query.filter(ReportTemplate.category == category)
        
        if active_only:
            query = query.filter(ReportTemplate.is_active == True)
        
        templates = query.all()
        
        return jsonify({
            'templates': [template.to_dict() for template in templates]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/reports/generate', methods=['POST'])
@token_required
@permission_required(Permission.GENERATE_REPORTS)
def generate_report(current_user):
    """إنشاء تقرير جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('template_id') or not data.get('title'):
            return jsonify({'message': 'معرف القالب والعنوان مطلوبان'}), 400
        
        # التحقق من وجود القالب
        template = ReportTemplate.query.get(data['template_id'])
        if not template:
            return jsonify({'message': 'قالب التقرير غير موجود'}), 404
        
        # إنشاء سجل التقرير
        report = GeneratedReport(
            template_id=data['template_id'],
            title=data['title'],
            description=data.get('description'),
            generated_by=current_user.id
        )
        
        if data.get('parameters'):
            report.set_parameters(data['parameters'])
        
        db.session.add(report)
        db.session.commit()
        
        log_audit(current_user.id, 'REPORT_GENERATED', 'generated_report', str(report.id),
                 f'تم إنشاء تقرير جديد: {report.title}')
        
        # هنا يمكن إضافة معالجة التقرير في الخلفية
        # generate_report_task.delay(report.id)
        
        return jsonify({
            'message': 'تم بدء إنشاء التقرير',
            'report': report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/reports', methods=['GET'])
@token_required
@permission_required(Permission.VIEW_REPORTS)
def get_generated_reports(current_user):
    """الحصول على التقارير المُنشأة"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        
        query = GeneratedReport.query
        
        if status:
            query = query.filter(GeneratedReport.status == status)
        
        # المدربون يرون تقاريرهم فقط
        if not current_user.has_permission(Permission.MANAGE_QUALITY):
            query = query.filter(GeneratedReport.generated_by == current_user.id)
        
        reports = query.order_by(GeneratedReport.generated_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'reports': [report.to_dict() for report in reports.items],
            'total': reports.total,
            'pages': reports.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/dashboard/summary', methods=['GET'])
@token_required
@permission_required(Permission.VIEW_QUALITY)
def get_quality_dashboard_summary(current_user):
    """الحصول على ملخص لوحة تحكم الجودة"""
    try:
        # إحصائيات عامة
        total_standards = QualityStandard.query.filter_by(is_active=True).count()
        total_kpis = KPI.query.filter_by(is_active=True).count()
        total_measurements = QualityMeasurement.query.count()
        
        # آخر القياسات
        recent_measurements = QualityMeasurement.query\
            .order_by(QualityMeasurement.created_at.desc())\
            .limit(5).all()
        
        # مؤشرات الأداء الحرجة
        critical_kpis = []
        kpis = KPI.query.filter_by(is_active=True).all()
        
        for kpi in kpis:
            latest_value = KPIValue.query.filter_by(kpi_id=kpi.id)\
                .order_by(KPIValue.measurement_date.desc()).first()
            
            if latest_value and kpi.critical_threshold:
                if latest_value.value <= kpi.critical_threshold:
                    critical_kpis.append({
                        'kpi': kpi.to_dict(),
                        'latest_value': latest_value.to_dict()
                    })
        
        # استيرادات رايات الأخيرة
        recent_imports = RayatImport.query\
            .order_by(RayatImport.imported_at.desc())\
            .limit(5).all()
        
        return jsonify({
            'summary': {
                'total_standards': total_standards,
                'total_kpis': total_kpis,
                'total_measurements': total_measurements,
                'critical_kpis_count': len(critical_kpis)
            },
            'recent_measurements': [m.to_dict() for m in recent_measurements],
            'critical_kpis': critical_kpis,
            'recent_imports': [imp.to_dict() for imp in recent_imports]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

@quality_bp.route('/init-defaults', methods=['POST'])
@token_required
@permission_required(Permission.MANAGE_QUALITY)
def initialize_defaults(current_user):
    """تهيئة البيانات الافتراضية للجودة"""
    try:
        # تهيئة معايير الجودة الافتراضية
        init_default_quality_standards()
        
        # تهيئة مؤشرات الأداء الافتراضية
        init_default_kpis()
        
        log_audit(current_user.id, 'QUALITY_DEFAULTS_INITIALIZED', 'system', 'quality',
                 'تم تهيئة البيانات الافتراضية للجودة')
        
        return jsonify({
            'message': 'تم تهيئة البيانات الافتراضية بنجاح'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الخادم: {str(e)}'}), 500

