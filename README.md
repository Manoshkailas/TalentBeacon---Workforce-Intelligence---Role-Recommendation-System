# TalentBeacon™ – AI‑Powered Employee Recommendation & Skill Intelligence Platform

TalentBeacon™ is an AI‑driven workforce intelligence platform designed to help organizations identify the best‑fit employees for roles, projects, and career opportunities.  
The system analyzes employee skills, certifications, assessments, learning history, and experience to deliver intelligent recommendations, skill‑gap insights, and career progression analytics.

---

## 🚀 Features

### 🔹 Employee–Role Matching
- TF‑IDF + Cosine Similarity based matching  
- Top‑N employee recommendations for any role  
- Match score (0–100%)

### 🔹 Skill Gap Analysis
- Compare employee skills vs. role requirements  
- Identify missing and priority skills  
- Gap severity scoring

### 🔹 Learning Recommendation Engine
- Suggests courses to close skill gaps  
- Integrates internal LMS, YouTube, certifications  
- Gemini‑powered learning path generation

### 🔹 Career Path Intelligence
- Predicts future roles based on current skills  
- Generates personalized career roadmaps  
- Readiness percentage for target roles

### 🔹 Workforce Readiness Analytics
- ML‑based readiness scoring (XGBoost/RandomForest)  
- Team‑level and organization‑level insights

### 🔹 Dashboards & Reports
- Talent discovery dashboard  
- Workforce analytics dashboard  
- Employee career dashboard  
- Export reports as PDF, Excel, CSV

### 🔹 Authentication & Role Management
- Admin, Manager, Employee roles  
- Secure login system  
- Session‑based authentication

---

## 🛠️ Tech Stack

### **Backend**
- Python  
- Flask  
- SQLAlchemy  
- REST APIs  

### **Frontend**
- HTML  
- CSS  
- Bootstrap  
- JavaScript  
- Chart.js  

### **Database**
- SQLite (development)  
- PostgreSQL / MySQL (production-ready)

### **Machine Learning**
- Scikit‑Learn  
- TF‑IDF Vectorizer  
- Cosine Similarity  
- XGBoost / RandomForest  

### **AI Integration**
- Gemini API (skill extraction, learning paths, career insights)

### **Storage**
- AWS S3 (optional for production)

---

## 📁 Project Structure

TalentBeacon/
│── backend/
│   ├── auth/
│   ├── employees/
│   ├── roles/
│   ├── matching/
│   ├── gap_analysis/
│   ├── learning/
│   ├── readiness/
│   ├── career/
│   ├── projects/
│   ├── dashboards/
│   ├── reports/
│   ├── services/
│   ├── models/
│   ├── config.py
│   ├── app.py
│   └── extensions.py
│
│── frontend/
│   ├── templates/
│   └── static/
│
│── ml/
│   ├── matching_model.py
│   ├── readiness_model.py
│   ├── skill_gap_engine.py
│   └── saved_models/
│
│── database/
│── run.py
│── requirements.txt
│── README.md
│── .gitignore
