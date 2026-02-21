import json
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta

db = SQLAlchemy()

class UserSession(db.Model):
    """Track multiple concurrent sessions per user"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    is_active = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref='sessions')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # player or admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    advertisements = db.relationship('Advertisement', backref='advertiser', lazy=True, cascade='all, delete-orphan')
    leagues_created = db.relationship('League', backref='creator', lazy=True, cascade='all, delete-orphan', foreign_keys='League.created_by')
    tournaments_created = db.relationship('Tournament', backref='creator', lazy=True, cascade='all, delete-orphan', foreign_keys='Tournament.created_by')
    league_memberships = db.relationship('LeagueMember', backref='user', lazy=True, cascade='all, delete-orphan')
    tournament_participations = db.relationship('TournamentParticipant', backref='user', lazy=True, cascade='all, delete-orphan')

class GameState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_type = db.Column(db.String(20))  # tic_tac_toe | connect_four | maze
    state = db.Column(db.Text)            # JSON board
    current_turn = db.Column(db.String(1), default="X")  # X or O
    winner = db.Column(db.String(1), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertiser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product = db.Column(db.String(200), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True)

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    game_type = db.Column(db.String(20), nullable=False)  # tic_tac_toe, checkers, maze
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=True)
    league = db.relationship('League', backref='tournaments')
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    max_participants = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    participants = db.relationship('TournamentParticipant', backref='tournament', lazy=True, cascade='all, delete-orphan')

class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    game_type = db.Column(db.String(20), nullable=False)  # tic_tac_toe, checkers, maze
    status = db.Column(db.String(20), default='active')  # active, inactive, archived
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    members = db.relationship('LeagueMember', backref='league', lazy=True, cascade='all, delete-orphan')

class LeagueMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint('league_id', 'user_id', name='unique_league_member'),)

class TournamentParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    position = db.Column(db.Integer, nullable=True)  # Final position/ranking
    score = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint('tournament_id', 'user_id', name='unique_tournament_participant'),)

class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_type = db.Column(db.String(20), nullable=False)  # tic_tac_toe, checkers, maze
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # None if vs AI
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # None if draw
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    player1 = db.relationship('User', foreign_keys=[player1_id])
    player2 = db.relationship('User', foreign_keys=[player2_id])
    winner = db.relationship('User', foreign_keys=[winner_id])

class MatchQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(20), nullable=False)  # tic_tac_toe, checkers, maze
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User')

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(20), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=True)
    status = db.Column(db.String(20), default='waiting')
    player1_ready = db.Column(db.Boolean, default=False)
    player2_ready = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    player1 = db.relationship('User', foreign_keys=[player1_id])
    player2 = db.relationship('User', foreign_keys=[player2_id])

