"""
TalentBeacon™ Workforce Readiness Score Engine
Uses rule-based weighted scoring with XGBoost for prediction.
"""
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor

PROFICIENCY_MAP = {'beginner': 0.25, 'intermediate': 0.5, 'advanced': 0.75, 'expert': 1.0}
LEVEL_MAP = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
SENIORITY_EXP = {'junior': 1, 'mid': 3, 'senior': 6, 'lead': 10}

WEIGHTS = {
    'skills': 0.40,
    'certifications': 0.15,
    'assessments': 0.20,
    'experience': 0.15,
    'learning': 0.10,
}


def compute_readiness_score(employee, role):
    """
    Compute a comprehensive readiness score for an employee targeting a role.
    Returns dict with score (0-100) and component breakdown.
    """
    # 1. Skills component
    skills_score = _skills_component(employee, role)

    # 2. Certifications component
    certs_score = _certs_component(employee)

    # 3. Assessments component
    assessment_score = _assessment_component(employee, role)

    # 4. Experience component
    exp_score = _experience_component(employee, role)

    # 5. Learning completion component
    learning_score = _learning_component(employee)

    # Weighted total
    total = (
        skills_score * WEIGHTS['skills'] +
        certs_score * WEIGHTS['certifications'] +
        assessment_score * WEIGHTS['assessments'] +
        exp_score * WEIGHTS['experience'] +
        learning_score * WEIGHTS['learning']
    )

    return {
        'score': round(total * 100, 1),
        'skills_component': round(skills_score * 100, 1),
        'certs_component': round(certs_score * 100, 1),
        'assessment_component': round(assessment_score * 100, 1),
        'experience_component': round(exp_score * 100, 1),
        'learning_component': round(learning_score * 100, 1),
        'label': _score_label(total * 100),
    }


def _skills_component(employee, role):
    """Score based on skill coverage and proficiency match."""
    required_skills = [rs for rs in role.role_skills if rs.requirement_type == 'required']
    if not required_skills:
        return 1.0

    emp_skills = {es.skill_id: es for es in employee.skills}
    total_weight = sum(rs.weight for rs in required_skills)
    achieved_weight = 0.0

    for rs in required_skills:
        req_level = LEVEL_MAP.get(rs.min_level, 2)
        if rs.skill_id in emp_skills:
            emp_level = LEVEL_MAP.get(emp_skills[rs.skill_id].proficiency_level, 1)
            # Full credit if at or above required level
            if emp_level >= req_level:
                achieved_weight += rs.weight
            else:
                achieved_weight += rs.weight * (emp_level / req_level) * 0.7

    return achieved_weight / total_weight if total_weight > 0 else 0.0


def _certs_component(employee):
    """Score based on active certifications."""
    active = len([c for c in employee.certifications if c.is_active])
    # 3+ certs = full score
    return min(active / 3.0, 1.0)


def _assessment_component(employee, role):
    """Score based on assessment results for role-relevant skills."""
    if not employee.assessments:
        return 0.5  # Neutral if no assessments

    role_skill_ids = {rs.skill_id for rs in role.role_skills}
    relevant_assessments = [
        a for a in employee.assessments
        if a.skill_id in role_skill_ids
    ]

    if not relevant_assessments:
        all_scores = [a.score / a.max_score for a in employee.assessments if a.max_score > 0]
        return np.mean(all_scores) if all_scores else 0.5

    scores = [a.score / a.max_score for a in relevant_assessments if a.max_score > 0]
    return np.mean(scores) if scores else 0.5


def _experience_component(employee, role):
    """Score experience against role seniority requirements."""
    required_exp = SENIORITY_EXP.get(role.seniority_level, 3)
    emp_exp = employee.years_experience or 0
    if emp_exp >= required_exp:
        return 1.0
    return emp_exp / required_exp


def _learning_component(employee):
    """Score based on learning module completion rate."""
    if not employee.learning_records:
        return 0.3  # Low baseline for no learning activity

    total = len(employee.learning_records)
    completed = len([lr for lr in employee.learning_records if lr.status == 'completed'])
    in_progress = len([lr for lr in employee.learning_records if lr.status == 'in_progress'])

    # Completed = full, in_progress = half credit
    effective_completed = completed + (in_progress * 0.5)
    return min(effective_completed / total, 1.0) if total > 0 else 0.3


def _score_label(score):
    """Convert numeric score to readiness label."""
    if score >= 85:
        return 'Ready'
    elif score >= 70:
        return 'Nearly Ready'
    elif score >= 50:
        return 'In Progress'
    elif score >= 30:
        return 'Early Stage'
    else:
        return 'Needs Development'


def extract_features(employee, role):
    """Extract numerical feature vector for ML training."""
    emp_skills = {es.skill_id: es for es in employee.skills}
    role_skill_ids = {rs.skill_id for rs in role.role_skills}

    # Features
    total_skills = len(emp_skills)
    relevant_skills = len([s for s in emp_skills if s in role_skill_ids])
    avg_proficiency = np.mean([PROFICIENCY_MAP.get(es.proficiency_level, 0.25)
                               for es in employee.skills]) if employee.skills else 0
    cert_count = len(employee.certifications)
    years_exp = employee.years_experience or 0
    perf_rating = employee.performance_rating or 3.0
    completed_modules = len([lr for lr in employee.learning_records if lr.status == 'completed'])
    avg_assessment = np.mean([a.score for a in employee.assessments]) if employee.assessments else 50.0

    return [
        total_skills, relevant_skills, avg_proficiency,
        cert_count, years_exp, perf_rating,
        completed_modules, avg_assessment
    ]
