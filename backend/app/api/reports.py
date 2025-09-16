from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.report import Report, ReportStatus, ReportReason, ReportTargetType
from app.models.audit_log import AuditLog
from datetime import datetime
import uuid

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/', methods=['POST'])
@jwt_required()
def create_report():
    """Create a new report"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['target_type', 'target_id', 'reason']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate target_type
    try:
        target_type = ReportTargetType(data['target_type'])
    except ValueError:
        return jsonify({'error': 'Invalid target type'}), 400
    
    # Validate reason
    try:
        reason = ReportReason(data['reason'])
    except ValueError:
        return jsonify({'error': 'Invalid reason'}), 400
    
    # Validate target_id format
    try:
        target_uuid = uuid.UUID(data['target_id'])
    except ValueError:
        return jsonify({'error': 'Invalid target ID format'}), 400
    
    # Check if user already reported this target
    existing_report = Report.query.filter_by(
        reporter_id=current_user_id,
        target_type=target_type,
        target_id=target_uuid
    ).first()
    
    if existing_report:
        return jsonify({'error': 'You have already reported this content'}), 400
    
    # Create report
    report = Report.create_report(
        reporter_id=current_user_id,
        target_type=target_type,
        target_id=target_uuid,
        reason=reason,
        description=data.get('description')
    )
    
    # Log the report creation
    AuditLog.log_action(
        actor_id=current_user_id,
        action="create_report",
        target_type="report",
        target_id=report.id,
        action_metadata={
            "target_type": target_type.value,
            "target_id": str(target_uuid),
            "reason": reason.value
        }
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Report created successfully',
        'report': report.to_dict()
    }), 201

@reports_bp.route('/', methods=['GET'])
@jwt_required()
def get_reports():
    """Get reports (moderator only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user.can_moderate():
        return jsonify({'error': 'Unauthorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)
    
    # Get reports
    if status:
        try:
            report_status = ReportStatus(status)
            reports = Report.query.filter_by(status=report_status).order_by(
                Report.created_at.desc()
            ).offset((page - 1) * per_page).limit(per_page).all()
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
    else:
        reports = Report.query.order_by(Report.created_at.desc()).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
    
    return jsonify({
        'reports': [report.to_dict() for report in reports],
        'page': page,
        'per_page': per_page
    }), 200

@reports_bp.route('/<report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get a specific report"""
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        return jsonify({'error': 'Invalid report ID format'}), 400
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    report = Report.query.get_or_404(report_uuid)
    
    # Check if user can view this report
    if report.reporter_id != current_user_id and not current_user.can_moderate():
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(report.to_dict()), 200

@reports_bp.route('/<report_id>/assign', methods=['PUT'])
@jwt_required()
def assign_report(report_id):
    """Assign report to a moderator"""
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        return jsonify({'error': 'Invalid report ID format'}), 400
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user.can_moderate():
        return jsonify({'error': 'Unauthorized'}), 403
    
    report = Report.query.get_or_404(report_uuid)
    
    if report.status != ReportStatus.PENDING:
        return jsonify({'error': 'Report is not pending'}), 400
    
    # Assign to current user
    report.assign_to_moderator(current_user_id)
    
    # Log the assignment
    AuditLog.log_action(
        actor_id=current_user_id,
        action="assign_report",
        target_type="report",
        target_id=report_uuid,
        action_metadata={"assigned_to": current_user_id}
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Report assigned successfully',
        'report': report.to_dict()
    }), 200

@reports_bp.route('/<report_id>/resolve', methods=['PUT'])
@jwt_required()
def resolve_report(report_id):
    """Resolve a report"""
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        return jsonify({'error': 'Invalid report ID format'}), 400
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user.can_moderate():
        return jsonify({'error': 'Unauthorized'}), 403
    
    report = Report.query.get_or_404(report_uuid)
    
    if report.status == ReportStatus.RESOLVED:
        return jsonify({'error': 'Report is already resolved'}), 400
    
    data = request.get_json()
    action_taken = data.get('action_taken')
    moderator_notes = data.get('moderator_notes')
    
    if not action_taken:
        return jsonify({'error': 'action_taken is required'}), 400
    
    # Resolve the report
    report.resolve(action_taken, moderator_notes)
    
    # Log the resolution
    AuditLog.log_action(
        actor_id=current_user_id,
        action="resolve_report",
        target_type="report",
        target_id=report_uuid,
        action_metadata={
            "action_taken": action_taken,
            "moderator_notes": moderator_notes
        }
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Report resolved successfully',
        'report': report.to_dict()
    }), 200

@reports_bp.route('/<report_id>/reject', methods=['PUT'])
@jwt_required()
def reject_report(report_id):
    """Reject a report"""
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        return jsonify({'error': 'Invalid report ID format'}), 400
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user.can_moderate():
        return jsonify({'error': 'Unauthorized'}), 403
    
    report = Report.query.get_or_404(report_uuid)
    
    if report.status == ReportStatus.REJECTED:
        return jsonify({'error': 'Report is already rejected'}), 400
    
    data = request.get_json()
    moderator_notes = data.get('moderator_notes')
    
    # Reject the report
    report.reject(moderator_notes)
    
    # Log the rejection
    AuditLog.log_action(
        actor_id=current_user_id,
        action="reject_report",
        target_type="report",
        target_id=report_uuid,
        action_metadata={"moderator_notes": moderator_notes}
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Report rejected successfully',
        'report': report.to_dict()
    }), 200

@reports_bp.route('/my-reports', methods=['GET'])
@jwt_required()
def get_my_reports():
    """Get reports created by current user"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    reports = Report.query.filter_by(reporter_id=current_user_id).order_by(
        Report.created_at.desc()
    ).offset((page - 1) * per_page).limit(per_page).all()
    
    return jsonify({
        'reports': [report.to_dict() for report in reports],
        'page': page,
        'per_page': per_page
    }), 200

@reports_bp.route('/assigned-to-me', methods=['GET'])
@jwt_required()
def get_assigned_reports():
    """Get reports assigned to current user"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user.can_moderate():
        return jsonify({'error': 'Unauthorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    reports = Report.get_reports_by_moderator(current_user_id, per_page, (page - 1) * per_page)
    
    return jsonify({
        'reports': [report.to_dict() for report in reports],
        'page': page,
        'per_page': per_page
    }), 200

