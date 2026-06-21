"""
app.py
Main Flask application for PhishGuard - a phishing awareness training
and simulation platform.

Run with:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import sqlite3
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "phishguard.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"  # Used to sign session cookies


# ───────────────────────────── DATABASE HELPERS ─────────────────────────────

def get_db():
    """Returns a SQLite connection stored on Flask's request context (g)."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ───────────────────────────── AUTH DECORATORS ──────────────────────────────

def login_required(view_func):
    """Redirects to login page if the user is not authenticated."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


def admin_required(view_func):
    """Redirects non-admin users away from admin-only pages."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Access denied: admin privileges required.", "danger")
            return redirect(url_for("dashboard"))
        return view_func(*args, **kwargs)
    return wrapped


# ───────────────────────────── PUBLIC ROUTES ────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # --- Server-side validation ---
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE email = ? OR username = ?", (email, username)
        ).fetchone()
        if existing:
            flash("An account with that email or username already exists.", "danger")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, 'user')",
            (username, email, password_hash),
        )
        db.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("index.html")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        flash(f"Welcome back, {user['username']}!", "success")
        if user["role"] == "admin":
            return redirect(url_for("admin_panel"))
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ───────────────────────────── DASHBOARD ────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user_id = session["user_id"]

    modules = db.execute("SELECT * FROM modules ORDER BY id").fetchall()

    quiz_results = db.execute(
        """SELECT module_id, MAX(score) as best_score, total
           FROM quiz_results WHERE user_id = ? GROUP BY module_id""",
        (user_id,),
    ).fetchall()
    quiz_scores = {row["module_id"]: (row["best_score"], row["total"]) for row in quiz_results}

    sim_stats = db.execute(
        """SELECT COUNT(*) as attempted,
                  SUM(is_correct) as correct
           FROM simulation_results WHERE user_id = ?""",
        (user_id,),
    ).fetchone()

    total_modules = len(modules)
    completed_modules = len(quiz_scores)
    progress_percent = int((completed_modules / total_modules) * 100) if total_modules else 0

    return render_template(
        "dashboard.html",
        modules=modules,
        quiz_scores=quiz_scores,
        sim_attempted=sim_stats["attempted"] or 0,
        sim_correct=sim_stats["correct"] or 0,
        progress_percent=progress_percent,
        completed_modules=completed_modules,
        total_modules=total_modules,
    )


# ───────────────────────────── EDUCATION MODULES ────────────────────────────

@app.route("/module/<int:module_id>")
@login_required
def module_view(module_id):
    db = get_db()
    module = db.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    if module is None:
        flash("Module not found.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("module.html", module=module)


# ───────────────────────────── QUIZ SYSTEM ──────────────────────────────────

@app.route("/quiz/<int:module_id>", methods=["GET", "POST"])
@login_required
def quiz(module_id):
    db = get_db()
    module = db.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    if module is None:
        flash("Module not found.", "danger")
        return redirect(url_for("dashboard"))

    questions = db.execute(
        "SELECT * FROM quiz_questions WHERE module_id = ?", (module_id,)
    ).fetchall()

    if request.method == "POST":
        score = 0
        results = []
        for q in questions:
            user_answer = request.form.get(f"q{q['id']}")
            is_correct = (user_answer == q["correct_option"])
            if is_correct:
                score += 1
            results.append({
                "question": q["question"],
                "user_answer": user_answer,
                "correct_answer": q["correct_option"],
                "is_correct": is_correct,
            })

        db.execute(
            "INSERT INTO quiz_results (user_id, module_id, score, total) VALUES (?, ?, ?, ?)",
            (session["user_id"], module_id, score, len(questions)),
        )
        db.commit()

        return render_template(
            "quiz_result.html", module=module, score=score, total=len(questions), results=results
        )

    return render_template("quiz.html", module=module, questions=questions)


# ───────────────────────────── PHISHING SIMULATION ──────────────────────────

@app.route("/simulation")
@login_required
def simulation_list():
    db = get_db()
    simulations = db.execute("SELECT * FROM simulations ORDER BY id").fetchall()

    attempted_ids = {
        row["simulation_id"]
        for row in db.execute(
            "SELECT simulation_id FROM simulation_results WHERE user_id = ?",
            (session["user_id"],),
        ).fetchall()
    }

    return render_template(
        "simulation_list.html", simulations=simulations, attempted_ids=attempted_ids
    )


@app.route("/simulation/<int:sim_id>", methods=["GET", "POST"])
@login_required
def simulation_view(sim_id):
    db = get_db()
    sim = db.execute("SELECT * FROM simulations WHERE id = ?", (sim_id,)).fetchone()
    if sim is None:
        flash("Simulation scenario not found.", "danger")
        return redirect(url_for("simulation_list"))

    if request.method == "POST":
        user_answer = request.form.get("answer")  # "phishing" or "legitimate"
        user_says_phishing = 1 if user_answer == "phishing" else 0
        is_correct = 1 if user_says_phishing == sim["is_phishing"] else 0

        db.execute(
            """INSERT INTO simulation_results
               (user_id, simulation_id, user_answer, is_correct)
               VALUES (?, ?, ?, ?)""",
            (session["user_id"], sim_id, user_says_phishing, is_correct),
        )
        db.commit()

        return render_template(
            "simulation_result.html", sim=sim, is_correct=bool(is_correct)
        )

    return render_template("simulation.html", sim=sim)


# ───────────────────────────── ADMIN PANEL ──────────────────────────────────

@app.route("/admin")
@admin_required
def admin_panel():
    db = get_db()

    users = db.execute(
        "SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()

    user_stats = []
    for u in users:
        quiz_avg = db.execute(
            """SELECT AVG(score * 100.0 / total) as avg_pct
               FROM quiz_results WHERE user_id = ?""",
            (u["id"],),
        ).fetchone()["avg_pct"]

        sim_stats = db.execute(
            """SELECT COUNT(*) as attempted, SUM(is_correct) as correct
               FROM simulation_results WHERE user_id = ?""",
            (u["id"],),
        ).fetchone()

        user_stats.append({
            "user": u,
            "quiz_avg": round(quiz_avg, 1) if quiz_avg else None,
            "sim_attempted": sim_stats["attempted"] or 0,
            "sim_correct": sim_stats["correct"] or 0,
        })

    return render_template("admin.html", user_stats=user_stats)


# ───────────────────────────── ENTRY POINT ──────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
