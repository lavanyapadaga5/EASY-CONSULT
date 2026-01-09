from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "your_secret_key"

# DB path
if os.getenv("VERCEL") == "1":
    db_path = "/tmp/hospital.db"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "hospital.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    doctor = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)


# Ensure DB exists
with app.app_context():
    db.create_all()


# ROUTES
@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["username"] = username
            return redirect(url_for("dashboard"))
        flash("Invalid credentials")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
        else:
            new_user = User(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    appointments = Appointment.query.filter_by(username=username).all()

    grouped = {}
    for a in appointments:
        grouped.setdefault(a.doctor, []).append(f"{a.date} {a.time}")

    return render_template("dashboard.html", username=username, appointments=grouped)


@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        doctor = request.form["doctor"]
        date = request.form["date"]
        time = request.form["time"]

        new_appointment = Appointment(
            username=session["username"], doctor=doctor, date=date, time=time
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash("Appointment scheduled!")
        return redirect(url_for("dashboard"))

    doctors = ["Dr. Smith", "Dr. Patel", "Dr. Khan"]
    return render_template("schedule.html", doctors=doctors)


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# Vercel handler
def handler(environ, start_response):
    return app(environ, start_response)
