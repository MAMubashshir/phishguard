PhishGuard

A Web-Based Phishing Awareness Training and Simulation Platform

Final Year Project | HND in Cyber Security | COM-FYP-403
TT Metro Campus - School of Computing | Academic Year 2024/2026
Student: Mubashshir Ahmed | Student ID: TTCISLlHND/CS/24/003

---

Project Overview

PhishGuard is a web-based phishing awareness training platform designed to educate users about phishing attacks through:

Interactive educational modules covering phishing techniques
Phishing simulation exercises with real-time feedback
Scored quizzes to test knowledge before and after training
User dashboard to track progress and scores
Admin panel to monitor all user performance

The platform is built using Python (Flask) for the backend, HTML/CSS/JavaScript/Bootstrap 5 for the frontend, and SQLite for the database.

---

How to Run the Project

Prerequisites

Make sure you have the following installed on your computer:

Python 3.10 or higher Download Python
pip (comes with Python)
Git Download Git

---

Step 1 - Clone the Repository

Open your terminal or command prompt and run:

git clone https://github.com/MAMubashshir/phishguard.git
cd phishguard

---

Step 2 - Install Dependencies

Install all required Python packages using pip:

pip install -r requirements.txt

The main dependencies are:

| Package | Purpose |
|---------|---------|
| Flask | Web framework |
| Werkzeug | Password hashing |
| Flask-Session | Session management |

---

Step 3 - Set Up the Database

Run the database setup script to create all tables and load sample data:

python setup_db.py

This will create a `phishguard.db` SQLite file with all required tables:
users
modules
quiz_questions
quiz_results
simulations
simulation_results

---

Step 4 - Run the Application

Start the Flask development server:

python app.py

You should see output like:

 * Running on http://127.0.0.1:5000
 * Debug mode: on

---

Step 5 - Open in Browser

Open your web browser and go to:

http://127.0.0.1:5000

---

Default Admin Account

An admin account is created automatically when you run `setup_db.py`:

| Field | Value |
|-------|-------|
| Email | admin@phishguard.com |
| Password | Admin@1234 |

Change this password immediately after first login in a real deployment.

---

Project Structure

phishguard/

app.py # Main Flask application and routes
setup_db.py # Database initialisation script
phishguard.db # SQLite database (created after setup)
requirements.txt # Python dependencies
README.md # This file

templates/ # HTML templates (Jinja2)
base.html # Base layout template
index.html # Home / login page
register.html # Registration page
dashboard.html # User dashboard
module.html # Education module page
quiz.html # Quiz page
simulation.html # Phishing simulation page
admin.html # Admin panel

static/ # Static files
css/
style.css # Custom stylesheet
js/
main.js # Custom JavaScript
images/ # Images and icons

tests/
test_cases.md # Manual test case documentation

---

Testing

Manual testing was conducted for all features. Test cases are documented in /tests/test_cases.md.

To verify the application is working correctly, test the following after setup:

[ ] Register a new user account
[ ] Log in with the new account
[ ] Complete an education module
[ ] Attempt a quiz and view your score
[ ] Complete a phishing simulation exercise
[ ] View your progress on the dashboard
[ ] Log in as admin and view user statistics

---

Security Features

Passwords hashed with bcrypt (via Werkzeug)
Parameterised SQL queries to prevent SQL injection
Server-side input validation on all forms
Role-based access control (admin vs regular user)
Session management with Flask sessions
Unauthenticated users redirected to login page

---

Technologies Used

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Backend | Python 3, Flask |
| Database | SQLite |
| Templating | Jinja2 |
| Security | Werkzeug (bcrypt) |
| Version Control | Git / GitHub |
| IDE | Visual Studio Code |

---

Deliverables Checklist

| # | Deliverable | Status |
|---|------------|--------|
| 1 | Project Proposal | Submitted |
| 2 | System Design Document | Submitted |
| 3 | Final Technical Report | Submitted |
| 4 | Working Prototype (this repo) | Submitted |
| 5 | Final Presentation | Submitted |

---

Disclaimer

This project is developed for educational purposes only as part of an academic Final Year Project. All phishing scenarios within the platform are fictional and pre-built for training use. No real phishing emails are sent. The platform must not be used to conduct actual phishing attacks against real individuals or organisations.

---

License

This project is submitted as academic coursework and is not licensed for commercial use.

---

* 2026 Mubashshir Ahmed | TT Metro Campus - School of Computing*