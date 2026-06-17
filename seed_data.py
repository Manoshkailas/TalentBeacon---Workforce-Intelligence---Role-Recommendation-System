"""
TalentBeacon™ Database Initializer & Seeder
Run this once to create all tables and populate sample data.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from backend.app import create_app
from backend.extensions import db, bcrypt
from backend.models import (
    User, Employee, Skill, EmployeeSkill, Role, RoleSkill,
    Certification, LearningModule, EmployeeLearning, Assessment, Project
)
from datetime import date, datetime
import json
import random

app = create_app()

SKILLS_DATA = [
    # Technical
    ('Python', 'technical'), ('Java', 'technical'), ('JavaScript', 'technical'),
    ('TypeScript', 'technical'), ('React', 'technical'), ('Node.js', 'technical'),
    ('Flask', 'technical'), ('Django', 'technical'), ('FastAPI', 'technical'),
    ('SQL', 'technical'), ('MySQL', 'technical'), ('PostgreSQL', 'technical'),
    ('MongoDB', 'technical'), ('Redis', 'technical'), ('Docker', 'technical'),
    ('Kubernetes', 'technical'), ('AWS', 'technical'), ('Azure', 'technical'),
    ('GCP', 'technical'), ('Git', 'technical'), ('Linux', 'technical'),
    ('REST APIs', 'technical'), ('GraphQL', 'technical'), ('Microservices', 'technical'),
    # Analytics
    ('Machine Learning', 'analytics'), ('Deep Learning', 'analytics'),
    ('Data Analysis', 'analytics'), ('Statistics', 'analytics'),
    ('Power BI', 'analytics'), ('Tableau', 'analytics'), ('Excel', 'analytics'),
    ('Pandas', 'analytics'), ('NumPy', 'analytics'), ('Scikit-Learn', 'analytics'),
    ('TensorFlow', 'analytics'), ('PyTorch', 'analytics'), ('NLP', 'analytics'),
    ('Data Visualization', 'analytics'), ('R Programming', 'analytics'),
    ('ETL Pipelines', 'analytics'), ('Apache Spark', 'analytics'),
    # Soft
    ('Communication', 'soft'), ('Leadership', 'soft'), ('Problem Solving', 'soft'),
    ('Team Collaboration', 'soft'), ('Project Management', 'soft'),
    ('Agile/Scrum', 'soft'), ('Critical Thinking', 'soft'), ('Presentation', 'soft'),
    ('Mentoring', 'soft'),
]

ROLES_DATA = [
    {
        'name': 'Data Scientist',
        'description': 'Builds ML models and derives insights from large datasets',
        'department': 'Data Science',
        'seniority_level': 'mid',
        'required': ['Python', 'Machine Learning', 'Statistics', 'SQL', 'Data Analysis'],
        'desired': ['Deep Learning', 'TensorFlow', 'PyTorch', 'NLP', 'Apache Spark'],
    },
    {
        'name': 'Data Analyst',
        'description': 'Analyzes data to generate business insights and reports',
        'department': 'Analytics',
        'seniority_level': 'mid',
        'required': ['SQL', 'Excel', 'Power BI', 'Statistics', 'Data Analysis'],
        'desired': ['Python', 'Tableau', 'Machine Learning', 'Data Visualization'],
    },
    {
        'name': 'Full Stack Developer',
        'description': 'Develops both frontend and backend web applications',
        'department': 'Engineering',
        'seniority_level': 'mid',
        'required': ['JavaScript', 'React', 'Node.js', 'SQL', 'REST APIs'],
        'desired': ['TypeScript', 'Docker', 'AWS', 'MongoDB', 'GraphQL'],
    },
    {
        'name': 'Machine Learning Engineer',
        'description': 'Builds and deploys ML systems at scale',
        'department': 'AI/ML',
        'seniority_level': 'senior',
        'required': ['Python', 'Machine Learning', 'Scikit-Learn', 'Docker', 'SQL'],
        'desired': ['TensorFlow', 'PyTorch', 'Kubernetes', 'AWS', 'MLflow'],
    },
    {
        'name': 'Cloud Engineer',
        'description': 'Designs and manages cloud infrastructure',
        'department': 'Infrastructure',
        'seniority_level': 'mid',
        'required': ['AWS', 'Docker', 'Kubernetes', 'Linux', 'Python'],
        'desired': ['Azure', 'GCP', 'Terraform', 'Ansible', 'Microservices'],
    },
    {
        'name': 'Backend Developer',
        'description': 'Builds scalable server-side applications and APIs',
        'department': 'Engineering',
        'seniority_level': 'mid',
        'required': ['Python', 'REST APIs', 'SQL', 'Git', 'Docker'],
        'desired': ['Flask', 'Django', 'FastAPI', 'Redis', 'Microservices'],
    },
    {
        'name': 'Data Engineer',
        'description': 'Builds data pipelines and warehouses',
        'department': 'Data Engineering',
        'seniority_level': 'mid',
        'required': ['Python', 'SQL', 'ETL Pipelines', 'Apache Spark', 'AWS'],
        'desired': ['Pandas', 'Docker', 'Kubernetes', 'MongoDB', 'NumPy'],
    },
    {
        'name': 'Cybersecurity Analyst',
        'description': 'Monitors and protects organization security infrastructure',
        'department': 'Security',
        'seniority_level': 'mid',
        'required': ['Linux', 'Python', 'SQL', 'Communication', 'Problem Solving'],
        'desired': ['AWS', 'Docker', 'Network Security', 'SIEM', 'Penetration Testing'],
    },
]

EMPLOYEES_DATA = [
    # (name, email, dept, designation, years_exp, performance, skills_list, certs)
    ('Aadhya Iyer', 'aadhya.iyer@talentbeacon.com', 'Data Science', 'Senior Data Scientist', 6.5, 4.8,
     [('Python', 'expert'), ('Machine Learning', 'expert'), ('Statistics', 'advanced'),
      ('SQL', 'advanced'), ('TensorFlow', 'advanced'), ('Data Analysis', 'expert'),
      ('Scikit-Learn', 'advanced'), ('Deep Learning', 'intermediate')],
     ['AWS Certified ML Specialty', 'Google Data Analytics', 'B.Tech IIT Madras']),

    ('Balaji Krishnan', 'balaji.krishnan@talentbeacon.com', 'Engineering', 'Full Stack Developer', 4.0, 4.2,
     [('JavaScript', 'expert'), ('React', 'expert'), ('Node.js', 'advanced'),
      ('SQL', 'intermediate'), ('REST APIs', 'advanced'), ('TypeScript', 'advanced'),
      ('Docker', 'intermediate'), ('Git', 'expert')],
     ['AWS Solutions Architect Associate', 'M.Tech NIT Trichy']),

    ('Chitra Ramaswamy', 'chitra.ramaswamy@talentbeacon.com', 'Analytics', 'Data Analyst', 3.0, 4.5,
     [('SQL', 'advanced'), ('Excel', 'expert'), ('Power BI', 'expert'),
      ('Statistics', 'intermediate'), ('Data Analysis', 'advanced'),
      ('Python', 'beginner'), ('Data Visualization', 'advanced')],
     ['Microsoft Power BI Certification', 'Google Analytics', 'B.E. Anna University']),

    ('Dinesh Naidu', 'dinesh.naidu@talentbeacon.com', 'AI/ML', 'ML Engineer', 5.0, 4.6,
     [('Python', 'expert'), ('Machine Learning', 'expert'), ('Scikit-Learn', 'expert'),
      ('TensorFlow', 'advanced'), ('Docker', 'advanced'), ('Kubernetes', 'intermediate'),
      ('AWS', 'advanced'), ('SQL', 'intermediate'), ('PyTorch', 'advanced')],
     ['AWS ML Specialty', 'TensorFlow Developer Certificate', 'M.S. IIIT Hyderabad']),

    ('Ezhil Natesan', 'ezhil.natesan@talentbeacon.com', 'Infrastructure', 'Cloud Engineer', 4.5, 4.3,
     [('AWS', 'expert'), ('Docker', 'expert'), ('Kubernetes', 'advanced'),
      ('Linux', 'expert'), ('Python', 'intermediate'), ('Azure', 'intermediate'),
      ('Microservices', 'advanced')],
     ['AWS Solutions Architect Professional', 'CKA - Kubernetes Admin', 'B.Tech VIT Vellore']),

    ('Farooq Mohammed', 'farooq.mohammed@talentbeacon.com', 'Data Engineering', 'Data Engineer', 3.5, 4.0,
     [('Python', 'advanced'), ('SQL', 'advanced'), ('ETL Pipelines', 'advanced'),
      ('Apache Spark', 'intermediate'), ('AWS', 'intermediate'), ('Pandas', 'advanced'),
      ('Docker', 'beginner')],
     ['AWS Data Analytics Specialty', 'B.E. Osmania University']),

    ('Gayatri Menon', 'gayatri.menon@talentbeacon.com', 'Data Science', 'Junior Data Scientist', 1.5, 3.8,
     [('Python', 'intermediate'), ('Machine Learning', 'intermediate'),
      ('Statistics', 'intermediate'), ('SQL', 'beginner'), ('Pandas', 'advanced'),
      ('NumPy', 'advanced'), ('Scikit-Learn', 'intermediate')],
     ['B.Sc. Data Science, Christ University']),

    ('Hariharan Reddy', 'hariharan.reddy@talentbeacon.com', 'Engineering', 'Backend Developer', 3.0, 4.1,
     [('Python', 'advanced'), ('REST APIs', 'advanced'), ('SQL', 'advanced'),
      ('Flask', 'advanced'), ('Docker', 'intermediate'), ('Redis', 'intermediate'),
      ('Git', 'advanced'), ('Linux', 'intermediate')],
     ['Python Institute PCEP', 'B.Tech SRM University']),

    ('Indira Pillai', 'indira.pillai@talentbeacon.com', 'Analytics', 'Senior Analyst', 5.5, 4.7,
     [('SQL', 'expert'), ('Tableau', 'expert'), ('Power BI', 'advanced'),
      ('Statistics', 'advanced'), ('Data Analysis', 'expert'), ('Excel', 'expert'),
      ('Python', 'intermediate'), ('Data Visualization', 'expert')],
     ['Tableau Desktop Specialist', 'Microsoft Excel Expert', 'M.Sc. Statistics, Madras University']),

    ('Jaganath Rao', 'jaganath.rao@talentbeacon.com', 'Security', 'Security Analyst', 4.0, 4.2,
     [('Linux', 'expert'), ('Python', 'advanced'), ('SQL', 'intermediate'),
      ('Problem Solving', 'advanced'), ('Communication', 'advanced')],
     ['CompTIA Security+', 'CEH - Ethical Hacker', 'B.Tech Amrita Vishwa Vidyapeetham']),

    ('Kavitha Nair', 'kavitha.nair@talentbeacon.com', 'Data Science', 'Data Scientist', 3.5, 4.4,
     [('Python', 'advanced'), ('Machine Learning', 'advanced'), ('Statistics', 'advanced'),
      ('SQL', 'intermediate'), ('Data Analysis', 'advanced'), ('R Programming', 'intermediate'),
      ('NLP', 'beginner')],
     ['IBM Data Science Professional', 'M.Tech IISc Bangalore']),

    ('Lakshman Kumar', 'lakshman.kumar@talentbeacon.com', 'Engineering', 'Frontend Developer', 2.5, 3.9,
     [('JavaScript', 'advanced'), ('React', 'advanced'), ('TypeScript', 'intermediate'),
      ('CSS', 'advanced'), ('Git', 'intermediate'), ('REST APIs', 'intermediate')],
     ['B.E. PSG Tech Coimbatore']),

    ('Meenakshi Sundaram', 'meenakshi.sundaram@talentbeacon.com', 'AI/ML', 'AI Researcher', 6.0, 4.9,
     [('Python', 'expert'), ('Deep Learning', 'expert'), ('TensorFlow', 'expert'),
      ('PyTorch', 'expert'), ('NLP', 'advanced'), ('Machine Learning', 'expert'),
      ('Statistics', 'expert'), ('Research', 'expert')],
     ['Google ML Engineer', 'Deep Learning Specialization', 'Ph.D. IIT Madras']),

    ('Naveen Varma', 'naveen.varma@talentbeacon.com', 'Infrastructure', 'DevOps Engineer', 4.0, 4.3,
     [('Docker', 'expert'), ('Kubernetes', 'advanced'), ('AWS', 'advanced'),
      ('Linux', 'advanced'), ('Python', 'intermediate'), ('Git', 'expert'),
      ('Microservices', 'intermediate')],
     ['AWS DevOps Engineer Professional', 'B.Tech JNTU Hyderabad']),

    ('Oviya Selvan', 'oviya.selvan@talentbeacon.com', 'Analytics', 'BI Developer', 3.0, 4.1,
     [('Power BI', 'expert'), ('SQL', 'advanced'), ('Excel', 'advanced'),
      ('Data Visualization', 'advanced'), ('Data Analysis', 'intermediate'),
      ('ETL Pipelines', 'beginner')],
     ['Microsoft Power BI Certification', 'B.Sc. Computer Science, Loyola College']),

    ('Prakash Raj', 'prakash.raj@talentbeacon.com', 'Data Engineering', 'Senior Data Engineer', 7.0, 4.5,
     [('Python', 'expert'), ('SQL', 'expert'), ('Apache Spark', 'expert'),
      ('ETL Pipelines', 'expert'), ('AWS', 'advanced'), ('Docker', 'advanced'),
      ('Kubernetes', 'intermediate'), ('MongoDB', 'intermediate')],
     ['AWS Data Analytics Specialty', 'Databricks Spark Developer', 'M.Tech NIT Warangal']),

    ('Qasim Ali', 'qasim.ali@talentbeacon.com', 'Engineering', 'Senior Backend Developer', 5.5, 4.6,
     [('Python', 'expert'), ('REST APIs', 'expert'), ('SQL', 'expert'),
      ('Django', 'expert'), ('Docker', 'advanced'), ('Redis', 'advanced'),
      ('Microservices', 'advanced'), ('AWS', 'intermediate')],
     ['AWS Solutions Architect Associate', 'B.E. Muffakham Jah College']),

    ('Ramya Srinivasan', 'ramya.srinivasan@talentbeacon.com', 'Data Science', 'ML Research Engineer', 4.5, 4.8,
     [('Python', 'expert'), ('Machine Learning', 'expert'), ('Deep Learning', 'advanced'),
      ('Statistics', 'advanced'), ('TensorFlow', 'advanced'), ('Scikit-Learn', 'expert'),
      ('Data Analysis', 'advanced'), ('NumPy', 'expert'), ('Pandas', 'expert')],
     ['Google Cloud ML Engineer', 'AWS ML Specialty', 'M.Tech BITS Pilani (Hyderabad)']),

    ('Srinivas Prasad', 'srinivas.prasad@talentbeacon.com', 'Engineering', 'Software Engineer', 2.0, 3.7,
     [('Java', 'intermediate'), ('Python', 'beginner'), ('SQL', 'beginner'),
      ('Git', 'intermediate'), ('REST APIs', 'beginner')],
     ['B.Tech KL University']),

    ('Trisha Venkatesh', 'trisha.venkatesh@talentbeacon.com', 'Analytics', 'Analytics Manager', 8.0, 4.7,
     [('SQL', 'expert'), ('Power BI', 'expert'), ('Statistics', 'expert'),
      ('Data Analysis', 'expert'), ('Leadership', 'expert'), ('Communication', 'expert'),
      ('Project Management', 'advanced'), ('Tableau', 'advanced')],
     ['PMP Certification', 'Tableau Server Admin', 'MBA IIM Bangalore', 'B.E. RVCE Bangalore']),
]

LEARNING_MODULES_DATA = [
    ('Python for Data Science', 'Python', 'Coursera', 'https://coursera.org', 30, 'course', 'beginner'),
    ('Machine Learning A-Z', 'Machine Learning', 'Udemy', 'https://udemy.com', 45, 'course', 'intermediate'),
    ('SQL Masterclass', 'SQL', 'DataCamp', 'https://datacamp.com', 20, 'course', 'beginner'),
    ('AWS Solutions Architect', 'AWS', 'AWS', 'https://aws.amazon.com', 40, 'certification', 'intermediate'),
    ('React Complete Guide', 'React', 'Udemy', 'https://udemy.com', 35, 'course', 'intermediate'),
    ('Docker & Kubernetes', 'Docker', 'Udemy', 'https://udemy.com', 25, 'course', 'intermediate'),
    ('Statistics for Data Science', 'Statistics', 'edX', 'https://edx.org', 20, 'course', 'beginner'),
    ('Power BI Masterclass', 'Power BI', 'Microsoft', 'https://learn.microsoft.com', 15, 'course', 'beginner'),
    ('Deep Learning Specialization', 'Deep Learning', 'Coursera', 'https://coursera.org', 80, 'certification', 'advanced'),
    ('Tableau Desktop', 'Tableau', 'Tableau', 'https://tableau.com', 20, 'course', 'beginner'),
    ('Flask Web Development', 'Flask', 'Real Python', 'https://realpython.com', 12, 'course', 'intermediate'),
    ('Apache Spark Fundamentals', 'Apache Spark', 'Databricks', 'https://databricks.com', 30, 'course', 'intermediate'),
    ('NLP with Python', 'NLP', 'Coursera', 'https://coursera.org', 40, 'course', 'advanced'),
    ('Kubernetes Administration', 'Kubernetes', 'Linux Foundation', 'https://training.linuxfoundation.org', 50, 'certification', 'advanced'),
    ('ETL Pipeline Design', 'ETL Pipelines', 'DataCamp', 'https://datacamp.com', 25, 'course', 'intermediate'),
    ('Data Visualization with Plotly', 'Data Visualization', 'YouTube', 'https://youtube.com', 8, 'video', 'beginner'),
    ('TensorFlow Developer Cert', 'TensorFlow', 'Google', 'https://tensorflow.org', 60, 'certification', 'advanced'),
    ('Leadership for Tech Leads', 'Leadership', 'LinkedIn Learning', 'https://linkedin.com', 10, 'course', 'intermediate'),
    ('Agile & Scrum Masterclass', 'Agile/Scrum', 'Udemy', 'https://udemy.com', 12, 'course', 'beginner'),
    ('Communication Skills for Developers', 'Communication', 'Coursera', 'https://coursera.org', 8, 'course', 'beginner'),
]


def seed_database():
    with app.app_context():
        print("[*] Creating TalentBeacon database tables...")
        db.create_all()

        # Check if already seeded
        if User.query.count() > 0:
            print("[OK] Database already seeded. Skipping.")
            return

        print("[*] Seeding skills...")
        skill_map = {}
        for skill_name, category in SKILLS_DATA:
            skill = Skill(name=skill_name, category=category,
                          description=f'{skill_name} skill')
            db.session.add(skill)
            db.session.flush()
            skill_map[skill_name] = skill

        print("[*] Seeding roles...")
        role_map = {}
        for role_data in ROLES_DATA:
            role = Role(
                name=role_data['name'],
                description=role_data['description'],
                department=role_data['department'],
                seniority_level=role_data['seniority_level'],
            )
            db.session.add(role)
            db.session.flush()
            role_map[role_data['name']] = role

            for skill_name in role_data.get('required', []):
                if skill_name in skill_map:
                    rs = RoleSkill(
                        role_id=role.id, skill_id=skill_map[skill_name].id,
                        requirement_type='required', min_level='intermediate', weight=1.0
                    )
                    db.session.add(rs)

            for skill_name in role_data.get('desired', []):
                if skill_name in skill_map:
                    rs = RoleSkill(
                        role_id=role.id, skill_id=skill_map[skill_name].id,
                        requirement_type='desired', min_level='beginner', weight=0.5
                    )
                    db.session.add(rs)

        print("[*] Seeding learning modules...")
        module_map = {}
        for title, skill_name, provider, url, duration, mod_type, level in LEARNING_MODULES_DATA:
            skill = skill_map.get(skill_name)
            module = LearningModule(
                title=title,
                skill_id=skill.id if skill else None,
                provider=provider,
                url=url,
                duration_hours=duration,
                module_type=mod_type,
                level=level,
                description=f'Learn {skill_name} with {provider}',
            )
            db.session.add(module)
            db.session.flush()
            module_map[title] = module

        print("[*] Seeding employees...")
        emp_map = {}
        for emp_data in EMPLOYEES_DATA:
            name, email, dept, designation, years_exp, perf, skills, certs = emp_data

            # Find matching role
            role_id = None
            for role_name, role in role_map.items():
                if any(word in designation for word in role_name.split()):
                    role_id = role.id
                    break

            emp = Employee(
                employee_code=f'TB{len(emp_map)+1:04d}',
                name=name, email=email,
                department=dept, designation=designation,
                current_role_id=role_id,
                years_experience=years_exp,
                performance_rating=perf,
                hire_date=date(2024 - int(years_exp), random.randint(1, 12), random.randint(1, 28)),
            )
            db.session.add(emp)
            db.session.flush()
            emp_map[email] = emp

            # Add skills
            for skill_name, proficiency in skills:
                if skill_name in skill_map:
                    es = EmployeeSkill(
                        employee_id=emp.id,
                        skill_id=skill_map[skill_name].id,
                        proficiency_level=proficiency,
                        years_with_skill=round(random.uniform(0.5, years_exp), 1),
                    )
                    db.session.add(es)

            # Add certifications
            for cert_name in certs:
                cert = Certification(
                    employee_id=emp.id,
                    name=cert_name,
                    provider='Certification Body',
                    issue_date=date(2023, random.randint(1, 12), 15),
                )
                db.session.add(cert)

            # Add sample assessments
            for skill_name, _ in skills[:3]:
                if skill_name in skill_map:
                    assess = Assessment(
                        employee_id=emp.id,
                        skill_id=skill_map[skill_name].id,
                        score=random.uniform(65, 98),
                        max_score=100,
                        date_taken=datetime(2024, random.randint(1, 12), random.randint(1, 28)),
                    )
                    db.session.add(assess)

            # Add sample learning records
            module_titles = list(module_map.keys())[:3]
            for title in module_titles:
                module = module_map[title]
                status = random.choice(['completed', 'completed', 'in_progress', 'enrolled'])
                lr = EmployeeLearning(
                    employee_id=emp.id,
                    module_id=module.id,
                    status=status,
                    score=random.uniform(75, 100) if status == 'completed' else None,
                    completion_date=datetime(2024, random.randint(1, 12), 15) if status == 'completed' else None,
                )
                db.session.add(lr)

            # Add sample projects
            project = Project(
                employee_id=emp.id,
                name=f'{dept} Analytics Platform',
                role_in_project=designation,
                description=f'Worked on {dept} team project',
                skills_used=json.dumps([s[0] for s in skills[:3]]),
                start_date=date(2023, 6, 1),
                end_date=date(2024, 3, 31),
            )
            db.session.add(project)

        print("[*] Seeding users...")
        # Admin user
        admin = User(
            email='admin@talentbeacon.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin',
        )
        db.session.add(admin)

        # Manager user (linked to Trisha Venkatesh)
        tina = emp_map.get('trisha.venkatesh@talentbeacon.com')
        manager = User(
            email='manager@talentbeacon.com',
            password_hash=bcrypt.generate_password_hash('manager123').decode('utf-8'),
            role='manager',
            employee_id=tina.id if tina else None,
        )
        db.session.add(manager)

        # Employee users
        for i, (email, emp) in enumerate(list(emp_map.items())[:5]):
            emp_user = User(
                email=email,
                password_hash=bcrypt.generate_password_hash('employee123').decode('utf-8'),
                role='employee',
                employee_id=emp.id,
            )
            db.session.add(emp_user)

        db.session.commit()

        print("\n[OK] TalentBeacon database seeded successfully!")
        print("\nDemo Accounts:")
        print("   Admin:    admin@talentbeacon.com / admin123")
        print("   Manager:  manager@talentbeacon.com / manager123")
        print("   Employee: aadhya.iyer@talentbeacon.com / employee123")
        print(f"\nSeeded:")
        print(f"   {len(SKILLS_DATA)} skills")
        print(f"   {len(ROLES_DATA)} roles")
        print(f"   {len(EMPLOYEES_DATA)} employees")
        print(f"   {len(LEARNING_MODULES_DATA)} learning modules")


if __name__ == '__main__':
    seed_database()
