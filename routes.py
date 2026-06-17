from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from backend.extensions import db
from backend.models import Skill

skills_bp = Blueprint('skills', __name__)


@skills_bp.route('', methods=['GET'])
@jwt_required()
def list_skills():
    """List all skills with optional filters."""
    category = request.args.get('category')
    search = request.args.get('search')

    query = Skill.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Skill.name.ilike(f'%{search}%'))

    skills = query.order_by(Skill.category, Skill.name).all()
    return jsonify([s.to_dict() for s in skills]), 200


@skills_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    cats = db.session.query(Skill.category).distinct().all()
    return jsonify([c[0] for c in cats if c[0]]), 200


@skills_bp.route('/<int:skill_id>', methods=['GET'])
@jwt_required()
def get_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    return jsonify(skill.to_dict()), 200


@skills_bp.route('', methods=['POST'])
@jwt_required()
def create_skill():
    """Create a new skill (admin only)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    name = data.get('name', '').strip()
    category = data.get('category', 'technical')

    if not name:
        return jsonify({'error': 'Skill name required'}), 400

    if category not in ['technical', 'analytics', 'soft', 'domain']:
        return jsonify({'error': 'Invalid category'}), 400

    if Skill.query.filter_by(name=name).first():
        return jsonify({'error': 'Skill already exists'}), 409

    skill = Skill(name=name, category=category, description=data.get('description'))
    db.session.add(skill)
    db.session.commit()

    return jsonify({'message': 'Skill created', 'skill': skill.to_dict()}), 201


@skills_bp.route('/<int:skill_id>', methods=['PUT'])
@jwt_required()
def update_skill(skill_id):
    """Update a skill (admin only)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    skill = Skill.query.get_or_404(skill_id)
    data = request.get_json()

    if 'name' in data:
        skill.name = data['name']
    if 'category' in data:
        skill.category = data['category']
    if 'description' in data:
        skill.description = data['description']
    if 'is_active' in data:
        skill.is_active = data['is_active']

    db.session.commit()
    return jsonify({'message': 'Skill updated', 'skill': skill.to_dict()}), 200


@skills_bp.route('/<int:skill_id>', methods=['DELETE'])
@jwt_required()
def delete_skill(skill_id):
    """Soft-delete a skill (admin only)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    skill = Skill.query.get_or_404(skill_id)
    skill.is_active = False
    db.session.commit()
    return jsonify({'message': 'Skill deactivated'}), 200


@skills_bp.route('/stats', methods=['GET'])
@jwt_required()
def skill_stats():
    """Skill distribution stats across employees."""
    from backend.models import EmployeeSkill
    stats = db.session.query(
        Skill.name, Skill.category,
        db.func.count(EmployeeSkill.id).label('employee_count')
    ).join(EmployeeSkill).group_by(Skill.id).order_by(
        db.desc('employee_count')
    ).limit(20).all()

    return jsonify([{
        'skill': s.name,
        'category': s.category,
        'employee_count': s.employee_count
    } for s in stats]), 200
