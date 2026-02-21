from flask import Blueprint, render_template, request, redirect, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, UserSession
from datetime import datetime, timedelta

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
            # Create a new user session
            user_session = UserSession(
                user_id=user.id,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(user_session)
            db.session.commit()
            
            # Login user and set session ID in response
            session.permanent = True
            login_user(user, remember=True)
            
            response = make_response(redirect("/admin" if user.role == "admin" else "/dashboard"))
            response.set_cookie('X-Session-ID', user_session.session_id, max_age=2592000, httponly=True)
            return response
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    # Invalidate current session
    session_id = request.cookies.get('X-Session-ID')
    if session_id:
        user_session = UserSession.query.filter_by(session_id=session_id).first()
        if user_session:
            user_session.is_active = False
            db.session.commit()
    
    logout_user()
    response = make_response(redirect("/"))
    response.delete_cookie('X-Session-ID')
    return response

@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Check if current password is correct
        if not check_password_hash(current_user.password, current_password):
            return render_template("change_password.html", error="Current password is incorrect")
        
        # Check if new passwords match
        if new_password != confirm_password:
            return render_template("change_password.html", error="New passwords do not match")
        
        # Check if new password is not empty
        if not new_password or len(new_password) < 6:
            return render_template("change_password.html", error="New password must be at least 6 characters long")
        
        # Update password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return render_template("change_password.html", success="Password changed successfully!")
    
    return render_template("change_password.html")
