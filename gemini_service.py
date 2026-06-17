"""
TalentBeacon™ Gemini AI Service
Provides AI-powered features: learning paths, career paths, skill extraction, NL search.
"""
import os
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

_model = None


def _get_model():
    """Lazy-load Gemini model."""
    global _model
    if _model is None and GEMINI_AVAILABLE:
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            genai.configure(api_key=api_key)
            _model = genai.GenerativeModel('gemini-1.5-flash')
    return _model


def _call_gemini(prompt, fallback=None):
    """Call Gemini and return text response, with fallback on error."""
    model = _get_model()
    if not model:
        return fallback
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[Gemini Error] {e}")
        return fallback


def get_learning_recommendations(missing_skills, role_name, employee_name=None):
    """
    Generate personalized learning recommendations for skill gaps.
    Returns a structured list of course recommendations.
    """
    skills_str = ', '.join(missing_skills) if missing_skills else 'general skills'
    emp_str = f" for {employee_name}" if employee_name else ""

    prompt = f"""You are a learning and development expert for TalentBeacon™.

Generate specific, actionable learning recommendations{emp_str} targeting the role: {role_name}.

Missing/weak skills to address: {skills_str}

For each skill, provide 2-3 specific course/resource recommendations.
Return your response as a valid JSON array with this exact structure:
[
  {{
    "skill": "skill name",
    "recommendations": [
      {{
        "title": "Course/Resource Title",
        "provider": "Provider Name (e.g., Coursera, Udemy, YouTube, internal)",
        "type": "course|video|certification|book|workshop",
        "duration": "estimated duration (e.g., 20 hours, 3 days)",
        "level": "beginner|intermediate|advanced",
        "url": "https://example.com or null",
        "description": "Brief 1-sentence description"
      }}
    ]
  }}
]

Only return the JSON array, no other text."""

    fallback = _default_learning_recommendations(missing_skills)
    result = _call_gemini(prompt, fallback=json.dumps(fallback))

    try:
        # Clean up response
        text = result.strip()
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        return json.loads(text)
    except:
        return fallback


def get_career_path(employee_name, current_role, current_skills, target_role=None):
    """
    Generate AI-powered career path recommendations.
    """
    skills_str = ', '.join(current_skills[:15]) if current_skills else 'various skills'
    target_str = f" towards {target_role}" if target_role else ""

    prompt = f"""You are a career development advisor for TalentBeacon™.

Analyze the career trajectory for: {employee_name}
Current role: {current_role}
Current skills: {skills_str}

Generate a career path recommendation{target_str}.

Return as valid JSON:
{{
  "current_role": "{current_role}",
  "potential_roles": [
    {{
      "role": "Role Name",
      "timeline": "6-12 months",
      "readiness_pct": 75,
      "skills_to_add": ["skill1", "skill2"],
      "description": "Brief description",
      "seniority": "junior|mid|senior|lead"
    }}
  ],
  "career_roadmap": [
    {{
      "phase": "Phase 1 - Foundation",
      "duration": "0-6 months",
      "actions": ["action1", "action2"],
      "milestone": "Milestone description"
    }}
  ],
  "key_skills_to_develop": ["skill1", "skill2", "skill3"],
  "summary": "Brief career advice summary"
}}

Only return the JSON, no other text."""

    fallback = _default_career_path(current_role)
    result = _call_gemini(prompt, fallback=json.dumps(fallback))

    try:
        text = result.strip()
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        return json.loads(text)
    except:
        return fallback


def extract_skills_from_text(text):
    """Extract skills mentioned in a job description or project description."""
    prompt = f"""Extract all technical skills, tools, frameworks, and competencies mentioned in the following text.

Text: {text}

Return as valid JSON array of strings. Only the skill names, no explanations.
Example: ["Python", "SQL", "Machine Learning", "AWS"]

Only return the JSON array, no other text."""

    result = _call_gemini(prompt, fallback='[]')
    try:
        text = result.strip()
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        return json.loads(text)
    except:
        return []


def natural_language_search(query, context="employees and skills"):
    """
    Parse a natural language search query into structured filters.
    """
    prompt = f"""Parse this natural language search query for a talent management system into structured filters.

Query: "{query}"

Return as valid JSON:
{{
  "skills": ["skill1", "skill2"],
  "departments": ["dept1"],
  "roles": ["role1"],
  "experience_min": null,
  "certifications": ["cert1"],
  "interpretation": "human-readable interpretation of the query"
}}

Only return the JSON, no other text."""

    fallback = {"skills": [], "departments": [], "roles": [], "interpretation": query}
    result = _call_gemini(prompt, fallback=json.dumps(fallback))
    try:
        text = result.strip()
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        return json.loads(text)
    except:
        return fallback


def _default_learning_recommendations(missing_skills):
    """Fallback recommendations when Gemini is unavailable."""
    recs = []
    for skill in (missing_skills or []):
        recs.append({
            "skill": skill,
            "recommendations": [
                {
                    "title": f"{skill} Fundamentals",
                    "provider": "Coursera",
                    "type": "course",
                    "duration": "20 hours",
                    "level": "beginner",
                    "url": f"https://www.coursera.org/search?query={skill.replace(' ', '+')}",
                    "description": f"Comprehensive introduction to {skill}"
                },
                {
                    "title": f"Advanced {skill}",
                    "provider": "Udemy",
                    "type": "course",
                    "duration": "30 hours",
                    "level": "intermediate",
                    "url": f"https://www.udemy.com/courses/search/?q={skill.replace(' ', '+')}",
                    "description": f"Hands-on {skill} training with real projects"
                }
            ]
        })
    return recs


def _default_career_path(current_role):
    """Fallback career path when Gemini is unavailable."""
    return {
        "current_role": current_role,
        "potential_roles": [
            {"role": "Senior " + current_role, "timeline": "12-18 months",
             "readiness_pct": 70, "skills_to_add": ["Leadership", "System Design"],
             "description": "Senior-level advancement", "seniority": "senior"},
            {"role": "Team Lead", "timeline": "24-36 months",
             "readiness_pct": 45, "skills_to_add": ["Team Management", "Agile"],
             "description": "Leadership track", "seniority": "lead"},
        ],
        "career_roadmap": [
            {"phase": "Phase 1 - Skill Building", "duration": "0-6 months",
             "actions": ["Complete advanced training", "Build portfolio projects"],
             "milestone": "Advanced proficiency in core skills"},
            {"phase": "Phase 2 - Leadership", "duration": "6-18 months",
             "actions": ["Lead a small project", "Mentor juniors"],
             "milestone": "First leadership role"},
        ],
        "key_skills_to_develop": ["Leadership", "Communication", "System Design"],
        "summary": f"Build on your {current_role} experience to grow into senior and leadership positions."
    }
