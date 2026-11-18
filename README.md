# 🏋️ Fitness Master – Personal Fitness & Wellness Platform

A modern, responsive, full-featured Personal Fitness & Wellness Web Application built with **Python**, **Django 5**, **SQLite3**, **Tailwind CSS**, **JavaScript**, and **Chart.js**.

---

## 🌟 Key Sections

The project contains **3 separate sections**:

1. **Public Website (`/`)**
   - High-impact Hero section with call-to-actions
   - Featured Workout Programs & Diet Plans showcase
   - Interactive BMI & TDEE Calorie Calculators
   - Exercise Catalog & Member Testimonials
   - Contact Form & About Us page

2. **User Panel (`/user/`)**
   - Personal Fitness Dashboard with momentum stats & streak counter
   - Interactive Weight Trend Chart & Daily Water Intake Tracker (Chart.js)
   - Structured Workout Routines with interactive workout logger
   - Comprehensive Exercise Library with instructions & muscle targets
   - Meal & Diet Plans
   - Fitness Challenges with milestone check-ins & trophy achievements
   - Profile management with custom biometrics (starts empty on registration for user input)
   - Top-bar Profile Avatar with hover dropdown menu & instant Logout

3. **Custom Admin Panel (`/custom-admin/` or `/admin/`)**
   - Dedicated administration operations portal
   - Separate tables for Registered Athletes (`role='USER'`) and Administrators (`role='ADMIN'`)
   - Full CRUD Management for Users (with block/unblock functionality)
   - Full CRUD for Exercises, Workout Plans, Diet Plans, Challenges & Accolades
   - Contact messages & feedback inbox
   - Platform Analytics & KPI dashboard

---

## 🔐 Default Admin Credentials

| Role | Username | Email | Password |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `Viraj` | `viraj@fitnessmaster.com` | `Viraj123` |

---

## 🎨 Color Palette & Design
- **Deep Navy / Midnight**: `#0F172A`, `#101828`, `#182230`
- **Electric Cyan**: `#06B6D4`
- **Blaze Orange**: `#FF5722`
- **Emerald Green**: `#10B981`
- **Danger Red**: `#E53945`
- **Light Slate Background**: `#F8FAFC`, `#F4F6FA`

---

## 🚀 Quick Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/virudobariya24/Fitness_Master.git
cd Fitness_Master
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Seed sample data & fixed admin
```bash
python seed_data.py
```

### 6. Run the local development server
```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Public Site**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **User Dashboard**: [http://127.0.0.1:8000/user/](http://127.0.0.1:8000/user/)
- **Custom Admin Portal**: [http://127.0.0.1:8000/custom-admin/](http://127.0.0.1:8000/custom-admin/)

---

## 🧪 Running Automated Tests
```bash
python manage.py test accounts
```
Runs the comprehensive test suite covering authentication, public pages, user workflows, trackers, and admin operations.
