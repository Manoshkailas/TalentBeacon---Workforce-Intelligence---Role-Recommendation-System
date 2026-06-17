from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from backend.extensions import db
from backend.models import Role, RoleSkill, Skill

roles_bp = Blueprint('roles', __name__)


@roles_bp.route('', methods=['GET'])
@jwt_required()
def list_roles():
    """List all active roles."""
    roles = Role.query.filter_by(is_active=True).all()
    return jsonify([r.to_dict() for r in roles]), 200


@roles_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    """Get a role with all required/desired skills."""
    role = Role.query.get_or_404(role_id)
    return jsonify(role.to_dict(include_skills=True)), 200


@roles_bp.route('', methods=['POST'])
@jwt_required()
def create_role():
    """Create a new job role (admin only)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Role name required'}), 400

    if Role.query.filter_by(name=name).first():
        return jsonify({'error': 'Role already exists'}), 409

    role = Role(
        name=name,
        description=data.get('description'),
        department=data.get('department'),
        seniority_level=data.get('seniority_level', 'mid'),
    )
    db.session.add(role)
    db.session.flush()

    # Add skills if provided
    for skill_data in data.get('skills', []):
        skill_id = skill_data.get('skill_id')
        if skill_id and Skill.query.get(skill_id):
            rs = RoleSkill(
                role_id=role.id,
                skill_id=skill_id,
                requirement_type=skill_data.get('requirement_type', 'required'),
                min_level=skill_data.get('min_level', 'intermediate'),
                weight=skill_data.get('weight', 1.0),
            )
            db.session.add(rs)

    db.session.commit()
    return jsonify({'message': 'Role created', 'role': role.to_dict(include_skills=True)}), 201


@roles_bp.route('/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    """Update a role (admin only)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    role = Role.query.get_or_404(role_id)
    data = request.get_json()

    for field in ['name', 'description', 'department', 'seniority_level']:
        if field in data:
            setattr(role, field, data[field])

    if 'is_active' in data:
        role.is_active = data['is_active']

    db.session.commit()
    return jsonify({'message': 'Role updated', 'role': role.to_dict()}), 200


@roles_bp.route('/<int:role_id>/skills', methods=['POST'])
@jwt_required()
def add_role_skill(role_id):
    """Add a skill requirement to a role (admin only)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    role = Role.query.get_or_404(role_id)
    data = request.get_json()
    skill_id = data.get('skill_id')

    if not skill_id:
        return jsonify({'error': 'skill_id required'}), 400

    Skill.query.get_or_404(skill_id)

    # Check if already exists
    existing = RoleSkill.query.filter_by(role_id=role_id, skill_id=skill_id).first()
    if existing:
        existing.requirement_type = data.get('requirement_type', existing.requirement_type)
        existing.min_level = data.get('min_level', existing.min_level)
        existing.weight = data.get('weight', existing.weight)
        db.session.commit()
        return jsonify({'message': 'Role skill updated', 'role_skill': existing.to_dict()}), 200

    rs = RoleSkill(
        role_id=role_id,
        skill_id=skill_id,
        requirement_type=data.get('requirement_type', 'required'),
        min_level=data.get('min_level', 'intermediate'),
        weight=data.get('weight', 1.0),
    )
    db.session.add(rs)
    db.session.commit()

    return jsonify({'message': 'Role skill added', 'role_skill': rs.to_dict()}), 201


@roles_bp.route('/<int:role_id>/skills/<int:skill_id>', methods=['DELETE'])
@jwt_required()
def remove_role_skill(role_id, skill_id):
    """Remove a skill from a role (admin only)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    rs = RoleSkill.query.filter_by(role_id=role_id, skill_id=skill_id).first_or_404()
    db.session.delete(rs)
    db.session.commit()
    return jsonify({'message': 'Role skill removed'}), 200
