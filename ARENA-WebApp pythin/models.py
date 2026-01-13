import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # player or admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    advertisements = db.relationship('Advertisement', backref='advertiser', lazy=True, cascade='all, delete-orphan')

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
    game_type = db.Column(db.String(20), nullable=False)  # tic_tac_toe | connect_four
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InterestGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
