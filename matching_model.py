"""
TalentBeacon™ Employee Matching Engine
Uses TF-IDF vectorization and Cosine Similarity to match employees to roles.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler


PROFICIENCY_MAP = {'beginner': 0.25, 'intermediate': 0.5, 'advanced': 0.75, 'expert': 1.0}
LEVEL_MAP = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}


def build_employee_skill_text(employee_skills, certifications=None, projects=None):
    """
    Build a text representation of an employee's profile for TF-IDF.
    Skills are weighted by proficiency (repeated for higher proficiency).
    """
    tokens = []

    # Skills with proficiency weighting
    for es in employee_skills:
        skill_name = es.skill.name.lower().replace(' ', '_')
        level = es.proficiency_level
        # Repeat skill tokens based on proficiency (higher = more weight)
        repeat = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}.get(level, 1)
        tokens.extend([skill_name] * repeat)

    # Certifications add bonus tokens
    if certifications:
        for cert in certifications:
            cert_token = cert.name.lower().replace(' ', '_').replace('-', '_')
            tokens.append(cert_token)
            tokens.append(cert_token)  # double weight for certifications

    # Projects - skills used get extra boost
    if projects:
        for project in projects:
            for skill in project.get_skills_used():
                tokens.append(skill.lower().replace(' ', '_'))

    return ' '.join(tokens) if tokens else 'no_skills'


def build_role_skill_text(role_skills):
    """
    Build a text representation of a role's requirements for TF-IDF.
    Required skills are weighted more than desired skills.
    """
    tokens = []

    for rs in role_skills:
        skill_name = rs.skill.name.lower().replace(' ', '_')
        # Required skills get higher weight than desired
        if rs.requirement_type == 'required':
            repeat = int(rs.weight * 4)
        else:
            repeat = max(1, int(rs.weight * 2))
        tokens.extend([skill_name] * max(1, repeat))

    return ' '.join(tokens) if tokens else 'no_requirements'


def compute_skill_coverage(employee_skills, role_skills):
    """
    Compute skill coverage score - what fraction of required skills the employee has.
    Returns 0.0-1.0.
    """
    required_skills = [rs for rs in role_skills if rs.requirement_type == 'required']
    if not required_skills:
        return 1.0

    emp_skill_ids = {es.skill_id: es for es in employee_skills}
    covered = 0
    total_weight = 0

    for rs in required_skills:
        total_weight += rs.weight
        if rs.skill_id in emp_skill_ids:
            emp_skill = emp_skill_ids[rs.skill_id]
            emp_level = LEVEL_MAP.get(emp_skill.proficiency_level, 1)
            req_level = LEVEL_MAP.get(rs.min_level, 2)
            if emp_level >= req_level:
                covered += rs.weight
            else:
                # Partial credit for lower proficiency
                covered += rs.weight * (emp_level / req_level) * 0.5

    return covered / total_weight if total_weight > 0 else 0.0


def compute_certification_bonus(certifications):
    """Return a bonus score for certifications (0.0-1.0 normalized)."""
    if not certifications:
        return 0.0
    # Each active certification contributes, capped at ~5 certs = full bonus
    active_certs = len([c for c in certifications if c.is_active])
    return min(active_certs / 5.0, 1.0)


def compute_experience_score(employee, role):
    """Score employee experience relative to role seniority."""
    seniority_exp_map = {'junior': 1, 'mid': 3, 'senior': 6, 'lead': 10}
    required_exp = seniority_exp_map.get(role.seniority_level, 3)
    emp_exp = employee.years_experience or 0
    if emp_exp >= required_exp:
        return 1.0
    return emp_exp / required_exp


def match_employees_to_role(role, employees, top_n=10):
    """
    Main matching function.
    Returns list of (employee, match_score, breakdown) sorted by match_score desc.
    """
    if not employees or not role.role_skills:
        return []

    role_text = build_role_skill_text(role.role_skills)

    results = []
    for emp in employees:
        emp_text = build_employee_skill_text(
            emp.skills,
            certifications=emp.certifications,
            projects=emp.projects
        )

        # TF-IDF Cosine Similarity
        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 1))
            matrix = vectorizer.fit_transform([role_text, emp_text])
            cosine_score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        except Exception:
            cosine_score = 0.0

        # Skill coverage (ensures required skills are present)
        coverage_score = compute_skill_coverage(emp.skills, role.role_skills)

        # Certification bonus
        cert_bonus = compute_certification_bonus(emp.certifications)

        # Experience score
        exp_score = compute_experience_score(emp, role)

        # Performance rating bonus (normalized to 0-1)
        perf_score = (emp.performance_rating or 3.0) / 5.0

        # Weighted final score
        final_score = (
            cosine_score * 0.35 +
            coverage_score * 0.35 +
            cert_bonus * 0.10 +
            exp_score * 0.12 +
            perf_score * 0.08
        )

        # Convert to percentage
        match_pct = round(final_score * 100, 1)

        results.append({
            'employee': emp,
            'match_score': match_pct,
            'skill_score': round(cosine_score * 100, 1),
            'coverage_score': round(coverage_score * 100, 1),
            'cert_score': round(cert_bonus * 100, 1),
            'experience_score': round(exp_score * 100, 1),
        })

    # Sort by match score descending
    results.sort(key=lambda x: x['match_score'], reverse=True)

    return results[:top_n]
