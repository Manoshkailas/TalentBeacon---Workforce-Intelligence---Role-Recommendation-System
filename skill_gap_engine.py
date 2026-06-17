"""
TalentBeacon™ Skill Gap Analysis Engine
Computes missing skills, gap severity, and priority recommendations.
"""

PROFICIENCY_LEVELS = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
PROFICIENCY_LABELS = {1: 'Beginner', 2: 'Intermediate', 3: 'Advanced', 4: 'Expert'}

SEVERITY_LABELS = {
    'critical': 'Critical',
    'high': 'High',
    'medium': 'Medium',
    'low': 'Low',
}


def analyze_skill_gap(employee, role):
    """
    Analyze skill gap between an employee and a target role.
    
    Returns:
        dict with missing_skills, partial_skills, matched_skills, gap_score, etc.
    """
    emp_skills = {es.skill_id: es for es in employee.skills}
    role_required = [rs for rs in role.role_skills if rs.requirement_type == 'required']
    role_desired = [rs for rs in role.role_skills if rs.requirement_type == 'desired']

    missing_required = []
    partial_required = []
    matched_required = []
    missing_desired = []
    matched_desired = []

    # Analyze required skills
    for rs in role_required:
        req_level = PROFICIENCY_LEVELS.get(rs.min_level, 2)

        if rs.skill_id not in emp_skills:
            # Completely missing
            severity = _compute_severity(rs, is_required=True, has_skill=False)
            missing_required.append({
                'skill_id': rs.skill_id,
                'skill_name': rs.skill.name,
                'skill_category': rs.skill.category,
                'required_level': rs.min_level,
                'current_level': None,
                'level_gap': req_level,
                'severity': severity,
                'requirement_type': 'required',
                'weight': rs.weight,
            })
        else:
            emp_skill = emp_skills[rs.skill_id]
            emp_level = PROFICIENCY_LEVELS.get(emp_skill.proficiency_level, 1)

            if emp_level < req_level:
                # Has the skill but at insufficient level
                severity = _compute_severity(rs, is_required=True, has_skill=True,
                                             emp_level=emp_level, req_level=req_level)
                partial_required.append({
                    'skill_id': rs.skill_id,
                    'skill_name': rs.skill.name,
                    'skill_category': rs.skill.category,
                    'required_level': rs.min_level,
                    'current_level': emp_skill.proficiency_level,
                    'level_gap': req_level - emp_level,
                    'severity': severity,
                    'requirement_type': 'required',
                    'weight': rs.weight,
                })
            else:
                # Fully matched
                matched_required.append({
                    'skill_id': rs.skill_id,
                    'skill_name': rs.skill.name,
                    'current_level': emp_skill.proficiency_level,
                    'required_level': rs.min_level,
                    'requirement_type': 'required',
                })

    # Analyze desired skills
    for rs in role_desired:
        if rs.skill_id not in emp_skills:
            missing_desired.append({
                'skill_id': rs.skill_id,
                'skill_name': rs.skill.name,
                'skill_category': rs.skill.category,
                'required_level': rs.min_level,
                'current_level': None,
                'severity': 'low',
                'requirement_type': 'desired',
                'weight': rs.weight,
            })
        else:
            emp_skill = emp_skills[rs.skill_id]
            matched_desired.append({
                'skill_id': rs.skill_id,
                'skill_name': rs.skill.name,
                'current_level': emp_skill.proficiency_level,
                'requirement_type': 'desired',
            })

    # Compute gap severity score (0-100, lower is better)
    all_missing = missing_required + partial_required
    total_required = len(role_required)
    if total_required > 0:
        gap_count = len(missing_required) + len(partial_required) * 0.5
        gap_severity_score = round((gap_count / total_required) * 100, 1)
    else:
        gap_severity_score = 0.0

    # Prioritize gaps to fix
    priority_gaps = _prioritize_gaps(missing_required + partial_required)

    return {
        'employee_id': employee.id,
        'employee_name': employee.name,
        'role_id': role.id,
        'role_name': role.name,
        'missing_required_skills': missing_required,
        'partial_skills': partial_required,
        'matched_required_skills': matched_required,
        'missing_desired_skills': missing_desired,
        'matched_desired_skills': matched_desired,
        'gap_severity_score': gap_severity_score,
        'priority_gaps': priority_gaps,
        'summary': {
            'total_required': total_required,
            'fully_matched': len(matched_required),
            'partially_matched': len(partial_required),
            'missing': len(missing_required),
            'desired_total': len(role_desired),
            'desired_matched': len(matched_desired),
        }
    }


def _compute_severity(role_skill, is_required, has_skill, emp_level=None, req_level=None):
    """Compute severity level of a skill gap."""
    weight = role_skill.weight

    if not has_skill:
        if weight >= 1.5:
            return 'critical'
        elif weight >= 1.0:
            return 'high'
        else:
            return 'medium'
    else:
        gap = (req_level - emp_level) if req_level and emp_level else 0
        if gap >= 3:
            return 'critical'
        elif gap == 2:
            return 'high'
        elif gap == 1:
            return 'medium'
        return 'low'


def _prioritize_gaps(gaps):
    """Sort gaps by priority for remediation."""
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    return sorted(gaps, key=lambda g: (
        severity_order.get(g['severity'], 4),
        -g.get('weight', 1.0)
    ))


def compute_team_gap_summary(employees, role):
    """Compute aggregated skill gap for a team against a target role."""
    all_required_skills = {rs.skill_id: rs for rs in role.role_skills if rs.requirement_type == 'required'}
    skill_coverage = {}

    for skill_id, rs in all_required_skills.items():
        covered_count = 0
        for emp in employees:
            emp_skill_ids = {es.skill_id: es for es in emp.skills}
            if skill_id in emp_skill_ids:
                emp_lvl = PROFICIENCY_LEVELS.get(emp_skill_ids[skill_id].proficiency_level, 1)
                req_lvl = PROFICIENCY_LEVELS.get(rs.min_level, 2)
                if emp_lvl >= req_lvl:
                    covered_count += 1

        skill_coverage[skill_id] = {
            'skill_name': rs.skill.name,
            'skill_category': rs.skill.category,
            'required_level': rs.min_level,
            'coverage_count': covered_count,
            'total_employees': len(employees),
            'coverage_pct': round((covered_count / len(employees)) * 100, 1) if employees else 0,
        }

    return skill_coverage
