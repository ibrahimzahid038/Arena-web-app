from flask import Blueprint, render_template, request, redirect, jsonify
from flask_login import login_required, current_user
from models import db, GameState, Advertisement, League, Tournament, LeagueMember, TournamentParticipant, GameResult, MatchQueue, Match
import json
import random
from datetime import datetime

games_bp = Blueprint("games", __name__)

# ============== AI PLAYER ==============

def get_best_move_ttt(board):
    """Minimax algorithm for Tic Tac Toe AI"""
    def minimax(board, depth, is_maximizing):
        winner = check_ttt_winner(board)
        
        if winner == "O":
            return 10 - depth
        elif winner == "X":
            return depth - 10
        elif None not in board:
            return 0
        
        if is_maximizing:
            best_score = -float('inf')
            for i in range(9):
                if board[i] is None:
                    board[i] = "O"
                    score = minimax(board, depth + 1, False)
                    board[i] = None
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] is None:
                    board[i] = "X"
                    score = minimax(board, depth + 1, True)
                    board[i] = None
                    best_score = min(score, best_score)
            return best_score
    
    best_score = -float('inf')
    best_move = None
    for i in range(9):
        if board[i] is None:
            board[i] = "O"
            score = minimax(board, 0, False)
            board[i] = None
            if score > best_score:
                best_score = score
                best_move = i
    return best_move

# ============== TIC TAC TOE ==============

def check_ttt_winner(board):
    lines = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for a,b,c in lines:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None

@games_bp.route("/tic-tac-toe", methods=["GET", "POST"])
def tic_tac_toe():
    vs_computer = request.args.get("vs_computer", "false").lower() == "true"
    # Get match_id from query params or form data
    match_id = request.args.get("match_id") or request.form.get("match_id")
    
    # Determine game type key - use match_id if in tournament/league
    if match_id:
        game_type_key = f"match_{match_id}_tic_tac_toe"
    else:
        game_type_key = "tic_tac_toe"
    
    game = GameState.query.filter_by(game_type=game_type_key).first()

    # Handle replay button
    if request.method == "POST" and request.form.get("action") == "replay":
        if game:
            game.state = json.dumps([None]*9)
            game.current_turn = "X"
            game.winner = None
            db.session.commit()
        else:
            game = GameState(
                game_type=game_type_key,
                state=json.dumps([None]*9),
                current_turn="X"
            )
            db.session.add(game)
            db.session.commit()

    # Create game only if it doesn't exist
    if not game:
        game = GameState(
            game_type=game_type_key,
            state=json.dumps([None]*9),
            current_turn="X"
        )
        db.session.add(game)
        db.session.commit()

    board = json.loads(game.state)

    # Handle move
    if request.method == "POST" and request.form.get("action") == "move" and not game.winner:
        if current_user.is_authenticated:
            index = int(request.form.get("cell"))
            if board[index] is None:
                board[index] = game.current_turn
                game.winner = check_ttt_winner(board)
                
                # Check for draw (board full and no winner)
                if not game.winner and None not in board:
                    game.winner = "DRAW"
                
                if not game.winner and None in board and vs_computer and game.current_turn == "X":
                    game.current_turn = "O"
                    ai_move = get_best_move_ttt(board.copy())
                    board[ai_move] = "O"
                    game.winner = check_ttt_winner(board)
                    
                    # Check for draw after AI move
                    if not game.winner and None not in board:
                        game.winner = "DRAW"
                    
                    if not game.winner:
                        game.current_turn = "X"
                elif not game.winner:
                    game.current_turn = "O" if game.current_turn == "X" else "X"
                
                game.state = json.dumps(board)
                db.session.commit()

    now = datetime.now()
    active_ads = Advertisement.query.filter(
        Advertisement.expires_at > now,
        Advertisement.active == True
    ).all()

    return render_template(
        "tic_tac_toe.html",
        board=board,
        winner=game.winner,
        turn=game.current_turn,
        vs_computer=vs_computer,
        match_id=match_id,
        ads=active_ads
    )

# ============== CHECKERS ==============

def init_checkers_board():
    """Initialize an 8x8 Checkers board"""
    board = [[None for _ in range(8)] for _ in range(8)]
    # Red pieces at top (rows 0-2)
    for r in range(3):
        for c in range(8):
            if (r + c) % 2 == 1:
                board[r][c] = "r"
    # Black pieces at bottom (rows 5-7)
    for r in range(5, 8):
        for c in range(8):
            if (r + c) % 2 == 1:
                board[r][c] = "b"
    return board

def get_valid_moves_checkers(board, row, col, is_red):
    """Get all valid moves for a piece"""
    piece = board[row][col]
    if piece is None:
        return []
    
    is_king = piece.isupper()
    moves = []
    
    # Regular moves (diagonal forward, or any diagonal if king)
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    if not is_king:
        # Red pieces move DOWN (positive row), Black pieces move UP (negative row)
        directions = [(1, -1), (1, 1)] if is_red else [(-1, -1), (-1, 1)]
    
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] is None:
            moves.append((nr, nc, False))  # (row, col, is_jump)
    
    # Capture moves
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            opponent = board[nr][nc]
            if opponent and opponent.lower() != piece.lower():
                # Check if we can jump
                jnr, jnc = nr + dr, nc + dc
                if 0 <= jnr < 8 and 0 <= jnc < 8 and board[jnr][jnc] is None:
                    moves.append((jnr, jnc, True))  # (row, col, is_jump)
    
    return moves

def apply_move_checkers(board, from_row, from_col, to_row, to_col):
    """Apply a move and return the updated board"""
    piece = board[from_row][from_col]
    board[to_row][to_col] = piece
    board[from_row][from_col] = None
    
    # Check for capture
    dr = (to_row - from_row) // 2
    dc = (to_col - from_col) // 2
    if abs(to_row - from_row) == 2:
        captured_row = from_row + dr
        captured_col = from_col + dc
        board[captured_row][captured_col] = None
    
    # Check for king promotion
    if (to_row == 7 and piece == "r") or (to_row == 0 and piece == "b"):
        board[to_row][to_col] = piece.upper()
    
    return board

def count_pieces_checkers(board):
    """Count remaining pieces"""
    red = sum(1 for r in board for c in r if c and c.lower() == "r")
    black = sum(1 for r in board for c in r if c and c.lower() == "b")
    return red, black

def get_best_move_checkers(board, is_red):
    """Simple AI for Checkers - prioritize captures, then center"""
    piece_char = "r" if is_red else "b"
    best_move = None
    best_score = -1
    
    for r in range(8):
        for c in range(8):
            if board[r][c] and board[r][c].lower() == piece_char:
                moves = get_valid_moves_checkers(board, r, c, is_red)
                for to_r, to_c, is_jump in moves:
                    score = 10 if is_jump else (abs(to_r - 4) + abs(to_c - 4))
                    if score > best_score:
                        best_score = score
                        best_move = (r, c, to_r, to_c)
    
    return best_move if best_move else None

@games_bp.route("/checkers", methods=["GET", "POST"])
def checkers():
    # Get vs_computer from either GET parameter or POST data
    vs_computer = request.args.get("vs_computer", "false").lower() == "true"
    match_id = request.args.get("match_id")
    if request.method == "POST":
        vs_computer = request.form.get("vs_computer", "false").lower() == "true"
        match_id = request.form.get("match_id") or match_id
    
    # Determine game type key - use match_id if in tournament/league
    if match_id:
        game_type_key = f"match_{match_id}_checkers"
    else:
        game_type_key = "checkers"
    
    game = GameState.query.filter_by(game_type=game_type_key).first()

    # Handle replay button
    if request.method == "POST" and request.form.get("action") == "replay":
        board = init_checkers_board()
        if game:
            game.state = json.dumps(board)
            game.current_turn = "red"
            game.winner = None
            db.session.commit()
        else:
            game = GameState(
                game_type=game_type_key,
                state=json.dumps(board),
                current_turn="red"
            )
            db.session.add(game)
            db.session.commit()
    
    # Create game only if it doesn't exist
    if not game:
        board = init_checkers_board()
        game = GameState(
            game_type=game_type_key,
            state=json.dumps(board),
            current_turn="red"
        )
        db.session.add(game)
        db.session.commit()

    board = json.loads(game.state)

    # Handle move
    if request.method == "POST" and request.form.get("action") == "move" and not game.winner:
        print("🔵 MOVE REQUEST RECEIVED")
        print(f"Form data: {request.form}")
        print(f"Authenticated: {current_user.is_authenticated}")
        # Allow moves even if not authenticated (for testing)
        from_r = int(request.form.get("from_r"))
        from_c = int(request.form.get("from_c"))
        to_r = int(request.form.get("to_r"))
        to_c = int(request.form.get("to_c"))
        
        print(f"Moving piece from [{from_r}, {from_c}] to [{to_r}, {to_c}]")
        
        piece = board[from_r][from_c]
        is_red = piece and piece.lower() == "r"
        
        print(f"Piece: {piece}, Is red: {is_red}, Current turn: {game.current_turn}")
        
        if piece and ((is_red and game.current_turn == "red") or (not is_red and game.current_turn == "black")):
            moves = get_valid_moves_checkers(board, from_r, from_c, is_red)
            print(f"Valid moves: {moves}")
            # Check if destination is in valid moves (compare just row and col, not the jump flag)
            is_valid = any(m[0] == to_r and m[1] == to_c for m in moves)
            
            if is_valid:
                board = apply_move_checkers(board, from_r, from_c, to_r, to_c)
                
                # Check win condition
                red_count, black_count = count_pieces_checkers(board)
                if red_count == 0:
                    game.winner = "black"
                elif black_count == 0:
                    game.winner = "red"
                else:
                    game.current_turn = "black" if game.current_turn == "red" else "red"
                    
                    # AI move
                    print(f"🤖 AI CHECK: vs_computer={vs_computer}, current_turn={game.current_turn}, winner={game.winner}")
                    if not game.winner and vs_computer and game.current_turn == "black":
                        print(f"🤖 MAKING AI MOVE FOR BLACK")
                        ai_move = get_best_move_checkers(board, False)
                        print(f"🤖 AI MOVE: {ai_move}")
                        if ai_move:
                            fr, fc, tr, tc = ai_move
                            board = apply_move_checkers(board, fr, fc, tr, tc)
                            red_count, black_count = count_pieces_checkers(board)
                            if red_count == 0:
                                game.winner = "black"
                            elif black_count == 0:
                                game.winner = "red"
                            else:
                                game.current_turn = "red"
                        print(f"🤖 AFTER AI: turn={game.current_turn}, winner={game.winner}")
                
                game.state = json.dumps(board)
                db.session.commit()

    now = datetime.now()
    active_ads = Advertisement.query.filter(
        Advertisement.expires_at > now,
        Advertisement.active == True
    ).all()

    return render_template(
        "checkers.html",
        board=board,
        winner=game.winner,
        turn=game.current_turn,
        vs_computer=vs_computer,
        match_id=match_id,
        ads=active_ads
    )

# ============== MAZE ==============

# ============== MAZE ==============

def create_random_maze():
    """Generate a random 7x7 maze with guaranteed path to exit using recursive backtracking"""
    SIZE = 7
    maze = [[1 for _ in range(SIZE)] for _ in range(SIZE)]
    
    def carve_path(x, y):
        maze[y][x] = 0
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < SIZE and 0 <= ny < SIZE and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                carve_path(nx, ny)
    
    carve_path(1, 1)
    maze[1][1] = 0  # Start
    maze[SIZE-2][SIZE-2] = 0  # Goal
    return maze

@games_bp.route("/maze", methods=["GET", "POST"])
def maze():
    # Get match_id from query params or form data
    match_id = request.args.get("match_id") or request.form.get("match_id")
    if request.method == "POST":
        match_id = request.form.get("match_id") or match_id
    
    # Determine game type key - use match_id if in tournament/league
    if match_id:
        game_type_key = f"match_{match_id}_maze"
    else:
        game_type_key = "maze"
    
    game = GameState.query.filter_by(game_type=game_type_key).first()

    # Handle replay button
    if request.method == "POST" and request.form.get("action") == "replay":
        maze_board = create_random_maze()
        if game:
            game.state = json.dumps({"maze": maze_board, "player_pos": [1, 1], "moves": 0})
            db.session.commit()
        else:
            game = GameState(
                game_type=game_type_key,
                state=json.dumps({"maze": maze_board, "player_pos": [1, 1], "moves": 0}),
                current_turn="X"
            )
            db.session.add(game)
            db.session.commit()

    # Create game only if it doesn't exist
    if not game:
        maze_board = create_random_maze()
        game = GameState(
            game_type=game_type_key,
            state=json.dumps({"maze": maze_board, "player_pos": [1, 1], "moves": 0}),
            current_turn="X"
        )
        db.session.add(game)
        db.session.commit()

    game_data = json.loads(game.state)
    maze_board = game_data["maze"]
    player_pos = game_data["player_pos"]
    moves = game_data.get("moves", 0)
    SIZE = len(maze_board)
    goal_pos = [SIZE-2, SIZE-2]
    game_won = player_pos == goal_pos

    # Handle move - return JSON for AJAX
    if request.method == "POST" and request.form.get("action") == "move" and current_user.is_authenticated and not game_won:
        direction = request.form.get("direction")
        row, col = player_pos
        
        if direction == "up" and row > 0 and maze_board[row-1][col] == 0:
            player_pos = [row-1, col]
            moves += 1
        elif direction == "down" and row < SIZE-1 and maze_board[row+1][col] == 0:
            player_pos = [row+1, col]
            moves += 1
        elif direction == "left" and col > 0 and maze_board[row][col-1] == 0:
            player_pos = [row, col-1]
            moves += 1
        elif direction == "right" and col < SIZE-1 and maze_board[row][col+1] == 0:
            player_pos = [row, col+1]
            moves += 1
        
        game_data = {"maze": maze_board, "player_pos": player_pos, "moves": moves}
        game.state = json.dumps(game_data)
        db.session.commit()
        
        # Check if goal reached
        game_won = player_pos == goal_pos
        
        # Return JSON response
        return jsonify({
            "maze": maze_board,
            "player_pos": player_pos,
            "goal_pos": goal_pos,
            "moves": moves,
            "game_won": game_won
        })

    now = datetime.now()
    active_ads = Advertisement.query.filter(
        Advertisement.expires_at > now,
        Advertisement.active == True
    ).all()

    return render_template(
        "maze.html",
        maze=maze_board,
        player_pos=player_pos,
        goal_pos=goal_pos,
        moves=moves,
        game_won=game_won,
        match_id=match_id,
        ads=active_ads
    )
# ============== LEAGUE & TOURNAMENT GAMES ==============

@games_bp.route("/league/<int:league_id>/play/<game_type>")
@login_required
def play_league_game(league_id, game_type):
    """Play a game in a league"""
    league = League.query.get(league_id)
    if not league:
        return redirect("/leagues")
    
    # Check if user is a member
    member = LeagueMember.query.filter_by(league_id=league_id, user_id=current_user.id).first()
    if not member:
        return redirect(f"/league/{league_id}")
    
    # Join queue for this league game
    queue_entry = MatchQueue(
        user_id=current_user.id,
        game_type=game_type,
        league_id=league_id
    )
    db.session.add(queue_entry)
    db.session.commit()
    
    # Try to find existing match
    waiting_players = MatchQueue.query.filter(
        MatchQueue.game_type == game_type,
        MatchQueue.league_id == league_id,
        MatchQueue.user_id != current_user.id
    ).all()
    
    if waiting_players:
        # Create match with first waiting player
        opponent = waiting_players[0]
        match = Match(
            player1_id=current_user.id,
            player2_id=opponent.user_id,
            game_type=game_type,
            league_id=league_id,
            status='waiting'
        )
        db.session.add(match)
        
        # Remove both from queue
        db.session.delete(queue_entry)
        db.session.delete(opponent)
        db.session.commit()
        
        return redirect(f"/play-match/{match.id}")
    
    # Show queue page if no opponent found
    return render_template("queue.html", queue_id=queue_entry.id, game_type=game_type, context_type=f"League: {league.name}")

@games_bp.route("/tournament/<int:tournament_id>/play")
@login_required
def play_tournament_game(tournament_id):
    """Play a game in a tournament"""
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return redirect("/tournaments")
    
    # Check if user is a participant
    participant = TournamentParticipant.query.filter_by(tournament_id=tournament_id, user_id=current_user.id).first()
    if not participant:
        return redirect(f"/tournament/{tournament_id}")
    
    # Join queue for this tournament game
    queue_entry = MatchQueue(
        user_id=current_user.id,
        game_type=tournament.game_type,
        tournament_id=tournament_id
    )
    db.session.add(queue_entry)
    db.session.commit()
    
    # Try to find existing match
    waiting_players = MatchQueue.query.filter(
        MatchQueue.game_type == tournament.game_type,
        MatchQueue.tournament_id == tournament_id,
        MatchQueue.user_id != current_user.id
    ).all()
    
    if waiting_players:
        # Create match with first waiting player
        opponent = waiting_players[0]
        match = Match(
            player1_id=current_user.id,
            player2_id=opponent.user_id,
            game_type=tournament.game_type,
            tournament_id=tournament_id,
            status='waiting'
        )
        db.session.add(match)
        
        # Remove both from queue
        db.session.delete(queue_entry)
        db.session.delete(opponent)
        db.session.commit()
        
        return redirect(f"/play-match/{match.id}")
    
    # Show queue page if no opponent found
    return render_template("queue.html", queue_id=queue_entry.id, game_type=tournament.game_type, context_type=f"Tournament: {tournament.name}")

@games_bp.route("/record-game-result", methods=["POST"])
@login_required
def record_game_result():
    """Record a game result and update league/tournament stats"""
    data = request.get_json()
    
    game_type = data.get("game_type")
    player1_id = int(data.get("player1_id"))
    player2_id = data.get("player2_id")
    player2_id = int(player2_id) if player2_id else None
    winner_id = data.get("winner_id")
    winner_id = int(winner_id) if winner_id else None
    league_id = data.get("league_id")
    league_id = int(league_id) if league_id else None
    tournament_id = data.get("tournament_id")
    tournament_id = int(tournament_id) if tournament_id else None
    
    # Record the game result
    result = GameResult(
        game_type=game_type,
        player1_id=player1_id,
        player2_id=player2_id,
        winner_id=winner_id,
        league_id=league_id,
        tournament_id=tournament_id
    )
    db.session.add(result)
    
    # Update league stats if league game
    if league_id:
        league = League.query.get(league_id)
        if league:
            # Update player1 stats
            member1 = LeagueMember.query.filter_by(league_id=league_id, user_id=player1_id).first()
            if member1:
                if winner_id == player1_id:
                    member1.wins += 1
                    member1.points += 10
                elif winner_id is None:  # Draw
                    member1.points += 5
                else:
                    member1.losses += 1
            
            # Update player2 stats if exists
            if player2_id:
                member2 = LeagueMember.query.filter_by(league_id=league_id, user_id=player2_id).first()
                if member2:
                    if winner_id == player2_id:
                        member2.wins += 1
                        member2.points += 10
                    elif winner_id is None:  # Draw
                        member2.points += 5
                    else:
                        member2.losses += 1
    
    # Update tournament stats if tournament game
    if tournament_id:
        tournament = Tournament.query.get(tournament_id)
        if tournament:
            # Award points to winner
            if winner_id:
                participant = TournamentParticipant.query.filter_by(tournament_id=tournament_id, user_id=winner_id).first()
                if participant:
                    participant.score += 10
            
            # Award points to loser
            if player2_id and winner_id != player2_id:
                participant = TournamentParticipant.query.filter_by(tournament_id=tournament_id, user_id=player2_id).first()
                if participant:
                    participant.score += 5
    
    db.session.commit()
    
    return jsonify({"success": True})

# ============== MATCHMAKING QUEUE ==============

@games_bp.route("/join-queue", methods=["POST"])
@login_required
def join_queue():
    """Join the matchmaking queue"""
    data = request.get_json()
    
    game_type = data.get("game_type")
    league_id = data.get("league_id")
    tournament_id = data.get("tournament_id")
    
    league_id = int(league_id) if league_id else None
    tournament_id = int(tournament_id) if tournament_id else None
    
    # Check if already in queue
    existing = MatchQueue.query.filter_by(
        user_id=current_user.id,
        game_type=game_type,
        league_id=league_id,
        tournament_id=tournament_id
    ).first()
    
    if existing:
        return jsonify({"success": False, "message": "Already in queue"})
    
    # Add to queue
    queue_entry = MatchQueue(
        user_id=current_user.id,
        game_type=game_type,
        league_id=league_id,
        tournament_id=tournament_id
    )
    db.session.add(queue_entry)
    db.session.commit()
    
    # Try to find a match (find another player in same queue)
    waiting_players = MatchQueue.query.filter(
        MatchQueue.game_type == game_type,
        MatchQueue.league_id == league_id,
        MatchQueue.tournament_id == tournament_id,
        MatchQueue.user_id != current_user.id
    ).all()
    
    if waiting_players:
        # Create a match with first available player
        opponent = waiting_players[0]
        match = Match(
            player1_id=current_user.id,
            player2_id=opponent.user_id,
            game_type=game_type,
            league_id=league_id,
            tournament_id=tournament_id,
            status='waiting'
        )
        db.session.add(match)
        
        # Remove both from queue
        db.session.delete(queue_entry)
        db.session.delete(opponent)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Match found!",
            "match_id": match.id,
            "opponent": opponent.user.username
        })
    
    return jsonify({
        "success": True,
        "message": "Waiting for opponent...",
        "queue_id": queue_entry.id
    })

@games_bp.route("/check-queue/<int:queue_id>", methods=["GET"])
@login_required
def check_queue(queue_id):
    """Check if match has been found"""
    queue_entry = MatchQueue.query.get(queue_id)
    
    if not queue_entry:
        # Might be in a match already
        match = Match.query.filter(
            db.or_(
                Match.player1_id == current_user.id,
                Match.player2_id == current_user.id
            ),
            Match.status == 'waiting'
        ).first()
        
        if match:
            return jsonify({
                "success": True,
                "found": True,
                "match_id": match.id,
                "opponent": match.player2.username if match.player1_id == current_user.id else match.player1.username
            })
        return jsonify({"success": False, "found": False, "message": "No match yet"})
    
    return jsonify({"success": True, "found": False, "message": "Still waiting..."})

@games_bp.route("/get-match/<int:match_id>", methods=["GET"])
@login_required
def get_match(match_id):
    """Get match details"""
    match = Match.query.get(match_id)
    
    if not match:
        return jsonify({"success": False})
    
    if match.player1_id != current_user.id and match.player2_id != current_user.id:
        return jsonify({"success": False, "error": "Not in this match"})
    
    opponent_id = match.player2_id if match.player1_id == current_user.id else match.player1_id
    opponent = db.session.get_or_404(__import__('models').User, opponent_id) if opponent_id else None
    
    return jsonify({
        "success": True,
        "match": {
            "id": match.id,
            "game_type": match.game_type,
            "status": match.status,
            "opponent": opponent.username if opponent else "AI"
        }
    })

@games_bp.route("/leave-queue/<int:queue_id>", methods=["POST"])
@login_required
def leave_queue(queue_id):
    """Leave the matchmaking queue"""
    queue_entry = MatchQueue.query.get(queue_id)
    
    if queue_entry and queue_entry.user_id == current_user.id:
        db.session.delete(queue_entry)
        db.session.commit()
        return jsonify({"success": True})
    
    return jsonify({"success": False})

@games_bp.route("/play-match/<int:match_id>")
@login_required
def play_match(match_id):
    """Show match info and start game"""
    match = Match.query.get(match_id)
    
    if not match:
        return redirect("/dashboard")
    
    if match.player1_id != current_user.id and match.player2_id != current_user.id:
        return redirect("/dashboard")
    
    opponent = match.player2 if match.player1_id == current_user.id else match.player1
    
    return render_template(
        "match_lobby.html",
        match=match,
        opponent=opponent,
        is_player1=match.player1_id == current_user.id
    )

@games_bp.route("/set-player-ready/<int:match_id>", methods=["POST"])
@login_required
def set_player_ready(match_id):
    """Mark current player as ready"""
    match = Match.query.get(match_id)
    
    if not match:
        return jsonify({"success": False})
    
    data = request.get_json()
    player_num = data.get('player_number')
    
    if match.player1_id == current_user.id and player_num == 1:
        match.player1_ready = True
    elif match.player2_id == current_user.id and player_num == 2:
        match.player2_ready = True
    else:
        return jsonify({"success": False})
    
    db.session.commit()
    return jsonify({"success": True})

@games_bp.route("/check-match-status/<int:match_id>", methods=["GET"])
@login_required
def check_match_status(match_id):
    """Check if both players are ready"""
    match = Match.query.get(match_id)
    
    if not match:
        return jsonify({"success": False})
    
    return jsonify({
        "success": True,
        "player1_ready": match.player1_ready,
        "player2_ready": match.player2_ready,
        "status": match.status
    })

@games_bp.route("/leave-match/<int:match_id>", methods=["POST"])
@login_required
def leave_match(match_id):
    """Leave a match"""
    match = Match.query.get(match_id)
    
    if match and (match.player1_id == current_user.id or match.player2_id == current_user.id):
        if match.status == 'waiting':
            db.session.delete(match)
            db.session.commit()
            return jsonify({"success": True})
    
    return jsonify({"success": False})

@games_bp.route("/start-match/<int:match_id>", methods=["GET", "POST"])
@login_required
def start_match_game(match_id):
    """Start the actual game for the match"""
    match = Match.query.get(match_id)
    
    if not match:
        return redirect("/dashboard")
    
    if match.player1_id != current_user.id and match.player2_id != current_user.id:
        return redirect("/dashboard")
    
    # Update match status
    match.status = 'in_progress'
    db.session.commit()
    
    # Redirect to the appropriate game with match context
    if match.game_type == "tic_tac_toe":
        return redirect(f"/tic-tac-toe?match_id={match_id}")
    elif match.game_type == "checkers":
        return redirect(f"/checkers?match_id={match_id}")
    elif match.game_type == "maze":
        return redirect(f"/maze?match_id={match_id}")
    
    return redirect("/dashboard")


