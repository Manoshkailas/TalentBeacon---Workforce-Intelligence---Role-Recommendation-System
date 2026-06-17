# TalentBeacon™ – Employee Recommendation & Skill Intelligence Platform

TalentBeacon™ is an AI-powered enterprise talent mapping and intelligence system. It uses machine learning models (TF-IDF, Cosine Similarity, and Regression scoring) alongside Google's Gemini API to analyze employee skills, certificates, experience, and performance to recommend candidate-role matches, predict workforce readiness, generate career roadmaps, and identify team skill gaps.

---

## 🌟 Key Features

1. **Talent Discovery Engine**: Search and match employees dynamically to roles using ML similarity matching or natural language AI queries.
2. **Workforce Readiness Intelligence**: Evaluate employee readiness metrics for specific job roles or promotional tracks with regression analysis.
3. **AI Career Roadmap**: Generate personalized career paths and action items using Google Gemini.
4. **Skill Gap Analytics**: Identify missing required and desired skills for individuals and departments.
5. **Project Staffing Recommendations**: Auto-recommend optimal project teams based on multi-skill requirements.
6. **L&D Course Recommendations**: Recommend courses and learning paths to bridge identified skill gaps.
7. **Report Generation**: Export comprehensive PDF, Excel, and CSV dashboards for audits and management reviews.
8. **Enterprise Security & RBAC**: Custom JWT authentication with access control for Admin, Manager, and Employee roles.

---

## 🛠️ Technology Stack

- **Backend**: Python Flask, Flask-SQLAlchemy (ORM), Flask-JWT-Extended
- **Frontend**: HTML5, Vanilla CSS (Premium Dark Theme/Glassmorphic UI), Jinja2 Templates, Bootstrap 5, Chart.js, Plotly.js
- **Machine Learning**: Scikit-Learn (TF-IDF + Vectorization + Cosine Similarity)
- **Generative AI**: Google Gemini API via `google-generativeai`
- **Database**: SQLite (default for development), PostgreSQL/MySQL compatible
- **Reporting**: ReportLab (PDF), openpyxl (Excel), CSV engine

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Clone and Setup Environment
Navigate to your project root folder and create a `.env` file from the template:
```bash
cp .env.example .env
```
Ensure your `.env` contains your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///talentbeacon.db
```

### 3. Install Dependencies
Run the package manager to install all required libraries:
```bash
pip install -r requirements.txt
```

### 4. Initialize and Seed the Database
Populate the database with sample skills, roles, learning modules, and 20+ realistic employee profiles:
```bash
python database/seed_data.py
```

### 5. Launch the Application
Start the Flask development server:
```bash
python run.py
```
Open **`http://localhost:5000`** in your browser.

---

## 🔑 Demo Credentials

To test different role dashboards, use the following pre-configured user credentials:

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin@talentbeacon.com` | `admin123` |
| **Manager** | `manager@talentbeacon.com` | `manager123` |
| **Employee** | `alice.johnson@talentbeacon.com` | `employee123` |

---

## 📁 Directory Structure

```
intern project/
├── backend/
│   ├── app.py                # Flask app entry point & config wiring
│   ├── config.py             # Configuration properties
│   ├── extensions.py         # SQLAlchemy, JWT, Bcrypt extensions
│   ├── models/               # Database ORM models (13 tables)
│   ├── auth/                 # Authentication & login routes
│   ├── employees/            # Employee profiles & actions
│   ├── skills/               # Skills repository
│   ├── roles/                # Role profiles
│   ├── matching/             # Similarity matching engines
│   ├── gap_analysis/         # Skill gap metrics
│   ├── learning/             # LMS & recommendations
│   ├── career/               # Gemini career roadmap services
│   ├── readiness/            # Regression prediction engines
│   ├── projects/             # Project staffing logic
│   ├── reports/              # PDF/Excel reporting modules
│   └── services/             # Gemini API wrappers
├── database/
│   └── seed_data.py          # Script to populate initial database
├── ml/
│   ├── matching_model.py     # Cosine similarity vectorizers
│   ├── readiness_model.py    # Weighted readiness calculations
│   └── skill_gap_engine.py   # Departmental gap analyzers
├── frontend/
│   ├── static/               # CSS stylesheets & JS modules
│   └── templates/            # Jinja2 template files
├── requirements.txt          # Python dependency list
├── run.py                    # Main startup execution entrypoint
└── README.md                 # Project documentation
```
