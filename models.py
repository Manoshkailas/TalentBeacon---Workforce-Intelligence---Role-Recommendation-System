from backend.extensions import db
from datetime import datetime
import json


class User(db.Model):
    """Authentication user model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')  # admin, manager, employee
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    employee = db.relationship('Employee', backref='user', uselist=False, foreign_keys=[employee_id])

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'employee_id': self.employee_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Employee(db.Model):
    """Employee profile model."""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    current_role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    years_experience = db.Column(db.Float, default=0)
    performance_rating = db.Column(db.Float, default=3.0)  # 1-5 scale
    hire_date = db.Column(db.Date, nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    current_role = db.relationship('Role', backref='employees', foreign_keys=[current_role_id])
    manager = db.relationship('Employee', remote_side=[id], backref='reports', foreign_keys=[manager_id])
    skills = db.relationship('EmployeeSkill', back_populates='employee', cascade='all, delete-orphan')
    certifications = db.relationship('Certification', back_populates='employee', cascade='all, delete-orphan')
    learning_records = db.relationship('EmployeeLearning', back_populates='employee', cascade='all, delete-orphan')
    assessments = db.relationship('Assessment', back_populates='employee', cascade='all, delete-orphan')
    projects = db.relationship('Project', back_populates='employee', cascade='all, delete-orphan')
    match_history = db.relationship('MatchHistory', back_populates='employee', cascade='all, delete-orphan')
    readiness_scores = db.relationship('ReadinessScore', back_populates='employee', cascade='all, delete-orphan')

    def to_dict(self, include_skills=False):
        data = {
            'id': self.id,
            'employee_code': self.employee_code,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'designation': self.designation,
            'current_role_id': self.current_role_id,
            'years_experience': self.years_experience,
            'performance_rating': self.performance_rating,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'is_active': self.is_active,
        }
        if include_skills:
            data['skills'] = [s.to_dict() for s in self.skills]
        return data

    def __repr__(self):
        return f'<Employee {self.employee_code} - {self.name}>'


class Skill(db.Model):
    """Master skill catalog."""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # technical, analytics, soft
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    employee_skills = db.relationship('EmployeeSkill', back_populates='skill', cascade='all, delete-orphan')
    role_skills = db.relationship('RoleSkill', back_populates='skill', cascade='all, delete-orphan')
    assessments = db.relationship('Assessment', back_populates='skill')
    learning_modules = db.relationship('LearningModule', back_populates='skill')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'is_active': self.is_active,
        }

    def __repr__(self):
        return f'<Skill {self.name} ({self.category})>'


class EmployeeSkill(db.Model):
    """Employee-Skill many-to-many with proficiency."""
    __tablename__ = 'employee_skills'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    proficiency_level = db.Column(db.String(20), nullable=False, default='beginner')
    # beginner=1, intermediate=2, advanced=3, expert=4
    years_with_skill = db.Column(db.Float, default=0)
    last_used = db.Column(db.Date, nullable=True)
    is_self_reported = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', back_populates='skills')
    skill = db.relationship('Skill', back_populates='employee_skills')

    PROFICIENCY_LEVELS = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}

    def proficiency_score(self):
        return self.PROFICIENCY_LEVELS.get(self.proficiency_level, 1)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'skill_category': self.skill.category if self.skill else None,
            'proficiency_level': self.proficiency_level,
            'years_with_skill': self.years_with_skill,
        }

    def __repr__(self):
        return f'<EmployeeSkill emp={self.employee_id} skill={self.skill_id} level={self.proficiency_level}>'


class Role(db.Model):
    """Job role profiles."""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    department = db.Column(db.String(100), nullable=True)
    seniority_level = db.Column(db.String(50), default='mid')  # junior, mid, senior, lead
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    role_skills = db.relationship('RoleSkill', back_populates='role', cascade='all, delete-orphan')
    match_history = db.relationship('MatchHistory', back_populates='role', cascade='all, delete-orphan')
    readiness_scores = db.relationship('ReadinessScore', back_populates='role', cascade='all, delete-orphan')

    def to_dict(self, include_skills=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'department': self.department,
            'seniority_level': self.seniority_level,
            'is_active': self.is_active,
        }
        if include_skills:
            data['required_skills'] = [rs.to_dict() for rs in self.role_skills if rs.requirement_type == 'required']
            data['desired_skills'] = [rs.to_dict() for rs in self.role_skills if rs.requirement_type == 'desired']
        return data

    def __repr__(self):
        return f'<Role {self.name}>'


class RoleSkill(db.Model):
    """Role-Skill requirements."""
    __tablename__ = 'role_skills'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    requirement_type = db.Column(db.String(20), nullable=False, default='required')  # required, desired
    min_level = db.Column(db.String(20), nullable=False, default='intermediate')
    weight = db.Column(db.Float, default=1.0)  # importance weight

    role = db.relationship('Role', back_populates='role_skills')
    skill = db.relationship('Skill', back_populates='role_skills')

    def to_dict(self):
        return {
            'id': self.id,
            'role_id': self.role_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'skill_category': self.skill.category if self.skill else None,
            'requirement_type': self.requirement_type,
            'min_level': self.min_level,
            'weight': self.weight,
        }


class Certification(db.Model):
    """Employee certifications."""
    __tablename__ = 'certifications'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(100), nullable=True)
    issue_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    credential_id = db.Column(db.String(100), nullable=True)
    credential_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    employee = db.relationship('Employee', back_populates='certifications')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': self.name,
            'provider': self.provider,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'credential_id': self.credential_id,
            'is_active': self.is_active,
        }


class LearningModule(db.Model):
    """Available learning modules/courses."""
    __tablename__ = 'learning_modules'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    provider = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    duration_hours = db.Column(db.Float, default=0)
    module_type = db.Column(db.String(50), default='course')  # course, video, certification, workshop
    level = db.Column(db.String(20), default='beginner')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    skill = db.relationship('Skill', back_populates='learning_modules')
    employee_learning = db.relationship('EmployeeLearning', back_populates='module', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'provider': self.provider,
            'url': self.url,
            'duration_hours': self.duration_hours,
            'module_type': self.module_type,
            'level': self.level,
        }


class EmployeeLearning(db.Model):
    """Employee learning completion records."""
    __tablename__ = 'employee_learning'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('learning_modules.id'), nullable=False)
    status = db.Column(db.String(20), default='enrolled')  # enrolled, in_progress, completed
    enrolled_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)  # 0-100

    employee = db.relationship('Employee', back_populates='learning_records')
    module = db.relationship('LearningModule', back_populates='employee_learning')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'module_id': self.module_id,
            'module_title': self.module.title if self.module else None,
            'status': self.status,
            'enrolled_date': self.enrolled_date.isoformat() if self.enrolled_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'score': self.score,
        }


class Assessment(db.Model):
    """Employee skill assessments."""
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 0-100
    max_score = db.Column(db.Float, default=100)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)
    assessor = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    employee = db.relationship('Employee', back_populates='assessments')
    skill = db.relationship('Skill', back_populates='assessments')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'score': self.score,
            'max_score': self.max_score,
            'percentage': round((self.score / self.max_score) * 100, 1) if self.max_score else 0,
            'date_taken': self.date_taken.isoformat() if self.date_taken else None,
        }


class Project(db.Model):
    """Employee project experience."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    role_in_project = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    skills_used = db.Column(db.Text, nullable=True)  # JSON string of skill names
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_ongoing = db.Column(db.Boolean, default=False)

    employee = db.relationship('Employee', back_populates='projects')

    def get_skills_used(self):
        if self.skills_used:
            try:
                return json.loads(self.skills_used)
            except:
                return []
        return []

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': self.name,
            'role_in_project': self.role_in_project,
            'description': self.description,
            'skills_used': self.get_skills_used(),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_ongoing': self.is_ongoing,
        }


class MatchHistory(db.Model):
    """Historical employee-role match scores."""
    __tablename__ = 'match_history'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    match_score = db.Column(db.Float, nullable=False)  # 0-100
    skill_score = db.Column(db.Float, nullable=True)
    cert_score = db.Column(db.Float, nullable=True)
    experience_score = db.Column(db.Float, nullable=True)
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', back_populates='match_history')
    role = db.relationship('Role', back_populates='match_history')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'match_score': self.match_score,
            'skill_score': self.skill_score,
            'cert_score': self.cert_score,
            'experience_score': self.experience_score,
            'computed_at': self.computed_at.isoformat() if self.computed_at else None,
        }


class ReadinessScore(db.Model):
    """Computed employee role readiness scores."""
    __tablename__ = 'readiness_scores'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 0-100
    skills_component = db.Column(db.Float, nullable=True)
    certs_component = db.Column(db.Float, nullable=True)
    assessment_component = db.Column(db.Float, nullable=True)
    experience_component = db.Column(db.Float, nullable=True)
    learning_component = db.Column(db.Float, nullable=True)
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', back_populates='readiness_scores')
    role = db.relationship('Role', back_populates='readiness_scores')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'score': self.score,
            'skills_component': self.skills_component,
            'certs_component': self.certs_component,
            'assessment_component': self.assessment_component,
            'experience_component': self.experience_component,
            'learning_component': self.learning_component,
            'computed_at': self.computed_at.isoformat() if self.computed_at else None,
        }
