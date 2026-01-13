from flask import Blueprint, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return render_template("signup.html", error="Username already exists")
        
        user = User(
            username=username,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == "admin":
                return redirect("/admin")
            else:
                return redirect("/dashboard")
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect("/")
