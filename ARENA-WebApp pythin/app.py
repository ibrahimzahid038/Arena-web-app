from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, User, GameState, Advertisement
from auth import auth_bp
from games import games_bp
from ads import ads_bp
from datetime import datetime
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arena.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(games_bp)
app.register_blueprint(ads_bp)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    now = datetime.now()
    active_ads = Advertisement.query.filter(
        Advertisement.expires_at > now,
        Advertisement.active == True
    ).all()
    return render_template("dashboard.html", ads=active_ads)

@app.route("/spectate")
def spectate():
    return render_template("spectate.html")

@app.route("/api/game-state/<game_type>")
def get_game_state(game_type):
    """API endpoint for spectators to get live game state"""
    game = GameState.query.filter_by(game_type=game_type).first()
    if game:
        return jsonify({
            "state": game.state,
            "turn": game.current_turn,
            "winner": game.winner,
            "type": game.game_type
        })
    return jsonify({"error": "Game not found"}), 404

@app.route("/spectate/<game_type>")
def spectate_game(game_type):
    """Spectator view for watching games"""
    game = GameState.query.filter_by(game_type=game_type).first()
    if not game:
        return "Game not found", 404
    
    return render_template(
        f"spectate_{game_type}.html",
        game_type=game_type
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Create hardcoded admin account if it doesn't exist
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                password=generate_password_hash("admin"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
