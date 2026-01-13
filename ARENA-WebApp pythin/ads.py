from flask import Blueprint, render_template, request, redirect, jsonify
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from models import db, Advertisement, User

ads_bp = Blueprint("ads", __name__)

@ads_bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    # Only users with admin role can access this
    if current_user.role != "admin":
        return redirect("/")
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create_ad":
            ad = Advertisement(
                advertiser_id=current_user.id,
                product=request.form.get("product"),
                amount_paid=float(request.form.get("amount")),
                expires_at=datetime.now() + timedelta(days=int(request.form.get("days")))
            )
            db.session.add(ad)
            db.session.commit()
            return redirect("/admin")
        
        elif action == "grant_admin":
            user_id = request.form.get("user_id")
            user = User.query.get(int(user_id))
            if user and user.id != current_user.id:
                user.role = "admin"
                db.session.commit()
                return redirect("/admin")
        
        elif action == "revoke_admin":
            user_id = request.form.get("user_id")
            user = User.query.get(int(user_id))
            if user and user.id != current_user.id:
                user.role = "player"
                db.session.commit()
                return redirect("/admin")
        
        elif action == "delete_user":
            user_id = request.form.get("user_id")
            user = User.query.get(int(user_id))
            if user and user.id != current_user.id:
                db.session.delete(user)
                db.session.commit()
                return redirect("/admin")
    
    ads = Advertisement.query.all()
    users = User.query.all()
    return render_template("admin.html", ads=ads, users=users)

@ads_bp.route("/ads-display")
def ads_display():
    """Display active advertisements for spectators"""
    now = datetime.now()
    active_ads = Advertisement.query.filter(
        Advertisement.expires_at > now,
        Advertisement.active == True
    ).all()
    return render_template("ads_display.html", ads=active_ads)
