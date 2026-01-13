from flask import Blueprint, render_template, request, redirect, jsonify
from flask_login import login_required, current_user
from models import db, GameState, Advertisement
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

def get_best_move_cf(board):
    """Simple AI for Connect Four"""
    ROWS, COLS = 6, 7
    
    # Check for winning move
    for col in range(COLS):
        for row in reversed(range(ROWS)):
            if board[row][col] is None:
                board[row][col] = "O"
                if check_cf_winner(board, "O"):
                    board[row][col] = None
                    return col
                board[row][col] = None
                break
    
    # Block opponent winning move
    for col in range(COLS):
        for row in reversed(range(ROWS)):
            if board[row][col] is None:
                board[row][col] = "X"
                if check_cf_winner(board, "X"):
                    board[row][col] = None
                    return col
                board[row][col] = None
                break
    
    # Take center column
    if board[0][3] is None:
        return 3
    
    # Random valid move
    valid_cols = [c for c in range(COLS) if board[0][c] is None]
    return random.choice(valid_cols) if valid_cols else 0

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
    
    game = GameState.query.filter_by(game_type="tic_tac_toe").first()

    # Handle replay button
    if request.method == "POST" and request.form.get("action") == "replay":
        if game:
            game.state = json.dumps([None]*9)
            game.current_turn = "X"
            game.winner = None
            db.session.commit()
        else:
            game = GameState(
                game_type="tic_tac_toe",
                state=json.dumps([None]*9),
                current_turn="X"
            )
            db.session.add(game)
            db.session.commit()

    # Create game only if it doesn't exist
    if not game:
        game = GameState(
            game_type="tic_tac_toe",
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
                
                if not game.winner and None in board and vs_computer and game.current_turn == "X":
                    game.current_turn = "O"
                    ai_move = get_best_move_ttt(board.copy())
                    board[ai_move] = "O"
                    game.winner = check_ttt_winner(board)
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
        ads=active_ads
    )

# ============== CONNECT FOUR ==============

ROWS, COLS = 6, 7

def check_cf_winner(board, piece):
    # Check horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    # Check vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    # Check diagonal \
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    # Check diagonal /
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    return False

@games_bp.route("/connect-four", methods=["GET", "POST"])
def connect_four():
    vs_computer = request.args.get("vs_computer", "false").lower() == "true"
    
    game = GameState.query.filter_by(game_type="connect_four").first()

    # Handle replay button
    if request.method == "POST" and request.form.get("action") == "replay":
        board = [[None]*COLS for _ in range(ROWS)]
        if game:
            game.state = json.dumps(board)
            game.current_turn = "X"
            game.winner = None
            db.session.commit()
        else:
            game = GameState(
                game_type="connect_four",
                state=json.dumps(board),
                current_turn="X"
            )
            db.session.add(game)
            db.session.commit()
    
    # Create game only if it doesn't exist
    if not game:
        board = [[None]*COLS for _ in range(ROWS)]
        game = GameState(
            game_type="connect_four",
            state=json.dumps(board),
            current_turn="X"
        )
        db.session.add(game)
        db.session.commit()

    board = json.loads(game.state)

    # Handle move
    if request.method == "POST" and request.form.get("action") == "move" and not game.winner:
        if current_user.is_authenticated:
            col = int(request.form.get("col"))
            if 0 <= col < COLS:
                for row in reversed(range(ROWS)):
                    if board[row][col] is None:
                        board[row][col] = game.current_turn
                        if check_cf_winner(board, game.current_turn):
                            game.winner = game.current_turn
                        
                        if not game.winner and vs_computer and game.current_turn == "X":
                            game.current_turn = "O"
                            ai_col = get_best_move_cf([row[:] for row in board])
                            for ai_row in reversed(range(ROWS)):
                                if board[ai_row][ai_col] is None:
                                    board[ai_row][ai_col] = "O"
                                    if check_cf_winner(board, "O"):
                                        game.winner = "O"
                                    else:
                                        game.current_turn = "X"
                                    break
                        else:
                            game.current_turn = "O" if game.current_turn == "X" else "X"
                        
                        game.state = json.dumps(board)
                        db.session.commit()
                        break

    now = datetime.now()
    active_ads = Advertisement.query.filter(
        Advertisement.expires_at > now,
        Advertisement.active == True
    ).all()

    return render_template(
        "connect_four.html",
        board=board,
        winner=game.winner,
        turn=game.current_turn,
        vs_computer=vs_computer,
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
    game = GameState.query.filter_by(game_type="maze").first()

    # Handle replay button
    if request.method == "POST" and request.form.get("action") == "replay":
        maze_board = create_random_maze()
        if game:
            game.state = json.dumps({"maze": maze_board, "player_pos": [1, 1], "moves": 0})
            db.session.commit()
        else:
            game = GameState(
                game_type="maze",
                state=json.dumps({"maze": maze_board, "player_pos": [1, 1], "moves": 0}),
                current_turn="X"
            )
            db.session.add(game)
            db.session.commit()

    # Create game only if it doesn't exist
    if not game:
        maze_board = create_random_maze()
        game = GameState(
            game_type="maze",
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

    # Handle move
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
        ads=active_ads
    )
