from flask import Blueprint, render_template, request, redirect, jsonify
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from models import db, Advertisement, User, League, Tournament, LeagueMember, TournamentParticipant

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
        
        elif action == "create_league":
            league = League(
                name=request.form.get("league_name"),
                description=request.form.get("league_description"),
                game_type=request.form.get("game_type"),
                created_by=current_user.id
            )
            db.session.add(league)
            db.session.commit()
            return redirect("/admin")
        
        elif action == "create_tournament":
            tournament = Tournament(
                name=request.form.get("tournament_name"),
                description=request.form.get("tournament_description"),
                game_type=request.form.get("game_type"),
                league_id=request.form.get("league_id") or None,
                status="upcoming",
                max_participants=request.form.get("max_participants"),
                created_by=current_user.id
            )
            db.session.add(tournament)
            db.session.commit()
            return redirect("/admin")
        
        elif action == "delete_league":
            league_id = request.form.get("league_id")
            league = League.query.get(int(league_id))
            if league and league.created_by == current_user.id:
                db.session.delete(league)
                db.session.commit()
                return redirect("/admin")
        
        elif action == "delete_tournament":
            tournament_id = request.form.get("tournament_id")
            tournament = Tournament.query.get(int(tournament_id))
            if tournament and tournament.created_by == current_user.id:
                db.session.delete(tournament)
                db.session.commit()
                return redirect("/admin")
    
    ads = Advertisement.query.all()
    users = User.query.all()
    leagues = League.query.all()
    tournaments = Tournament.query.all()
    return render_template("admin.html", ads=ads, users=users, leagues=leagues, tournaments=tournaments)

@ads_bp.route("/ads-display")
def ads_display():
    """Display active advertisements for spectators"""
    now = datetime.now()
    active_ads = Advertisement.query.filter(
        Advertisement.expires_at > now,
        Advertisement.active == True
    ).all()
    return render_template("ads_display.html", ads=active_ads)
@ads_bp.route("/leagues")
def leagues():
    """Display all leagues"""
    leagues = League.query.filter_by(status='active').all()
    return render_template("leagues.html", leagues=leagues)

@ads_bp.route("/tournaments")
def tournaments():
    """Display all tournaments"""
    tournaments = Tournament.query.filter(Tournament.status != 'completed').all()
    return render_template("tournaments.html", tournaments=tournaments)

@ads_bp.route("/join-league", methods=["POST"])
@login_required
def join_league():
    """Join a league"""
    league_id = request.form.get("league_id")
    league = League.query.get(int(league_id))
    
    if league:
        # Check if already a member
        existing = LeagueMember.query.filter_by(
            league_id=league_id,
            user_id=current_user.id
        ).first()
        
        if not existing:
            member = LeagueMember(
                league_id=league_id,
                user_id=current_user.id
            )
            db.session.add(member)
            db.session.commit()
    
    return redirect("/leagues")

@ads_bp.route("/join-tournament", methods=["POST"])
@login_required
def join_tournament():
    """Join a tournament"""
    tournament_id = request.form.get("tournament_id")
    tournament = Tournament.query.get(int(tournament_id))
    
    if tournament:
        # Check if already a participant
        existing = TournamentParticipant.query.filter_by(
            tournament_id=tournament_id,
            user_id=current_user.id
        ).first()
        
        if not existing and tournament.status != 'completed':
            # Check if tournament is not full
            if not tournament.max_participants or len(tournament.participants) < tournament.max_participants:
                participant = TournamentParticipant(
                    tournament_id=tournament_id,
                    user_id=current_user.id
                )
                db.session.add(participant)
                db.session.commit()
    
    return redirect("/tournaments")

@ads_bp.route("/league/<int:league_id>")
def view_league(league_id):
    """View league details"""
    league = League.query.get(league_id)
    if not league:
        return redirect("/leagues")
    return render_template("league_detail.html", league=league)

@ads_bp.route("/tournament/<int:tournament_id>")
def view_tournament(tournament_id):
    """View tournament details"""
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return redirect("/tournaments")
    return render_template("tournament_detail.html", tournament=tournament)