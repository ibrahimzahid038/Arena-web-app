# ARENA - Game Platform Web Application

A complete web application built with Flask for playing games, spectating live games, and advertising.

## Features

- **User Authentication**: Sign up as Player or Advertiser
- **Games**: Tic Tac Toe, Connect Four, Maze Challenge
- **Spectator Mode**: Watch games without logging in
- **Advertisement System**: Simulated payment gateway for advertisers
- **Real-time Board Updates**: See live game state
- **Responsive Design**: Built with Tailwind CSS

## Project Structure

```
ARENA-WebApp/
├── app.py                    # Main Flask application
├── models.py                 # Database models
├── auth.py                   # Authentication routes
├── games.py                  # Game logic and routes
├── ads.py                    # Advertisement routes
├── requirements.txt          # Python dependencies
└── templates/
    ├── base.html             # Base template
    ├── index.html            # Home page
    ├── signup.html           # Sign up form
    ├── login.html            # Login form
    ├── dashboard.html        # Player dashboard
    ├── tic_tac_toe.html      # Tic Tac Toe game
    ├── connect_four.html     # Connect Four game
    ├── maze.html             # Maze game
    ├── advertiser.html       # Advertiser dashboard
    ├── spectate.html         # Spectator page
    └── ads_display.html      # Advertisement display
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open browser to: `http://localhost:5000`

## Usage

### For Players
1. Sign up with Player role
2. Log in
3. Play Tic Tac Toe, Connect Four, or Maze
4. View advertisements

### For Advertisers
1. Sign up with Advertiser role
2. Log in
3. Create advertisements with:
   - Product name
   - Amount to pay
   - Duration (1 day, 1 week, 1 month, 3 months)
4. View all active advertisements
5. Ads automatically expire after duration

### For Spectators
1. No login required
2. Visit `/spectate` to view active games
3. Watch games in real-time
4. View current advertisements

## Database Models

- **User**: Stores user credentials and role
- **GameState**: Stores game board state and status
- **Advertisement**: Stores advertisement details and expiration
- **Tournament**: Tournament data (future feature)
- **InterestGroup**: Interest groups (future feature)

## Game Rules

### Tic Tac Toe
- 3x3 grid
- Players take turns (X and O)
- Get 3 in a row to win

### Connect Four
- 6x7 grid
- Players drop pieces
- Get 4 in a row (horizontal, vertical, diagonal) to win

### Maze
- 5x5 maze
- Navigate from start (top-left) to goal (bottom-right)
- Use arrow controls to move

## Payment Simulation

The advertiser system simulates real payments by:
1. Recording the amount paid
2. Calculating expiration time based on duration
3. Automatically deactivating expired advertisements
4. No real financial processing involved

This is suitable for educational/university projects and demonstrates realistic software design.

## Deployment

Ready for deployment on:
- **Render** - https://render.com/
- **Railway** - https://railway.app/
- **Heroku** - https://www.heroku.com/
- **PythonAnywhere** - https://www.pythonanywhere.com/

### Deployment Steps for Render

1. Push code to GitHub
2. Create account on Render
3. Create new Web Service
4. Connect GitHub repo
5. Set start command: `python app.py`
6. Deploy

## Technologies Used

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML, Tailwind CSS
- **Database**: SQLite
- **Authentication**: Flask-Login
- **Security**: Werkzeug (password hashing)

## Future Enhancements

- WebSocket support for real-time spectator updates
- Tournament brackets
- User leaderboards
- Interest group notifications
- Multiplayer matchmaking
- Payment gateway integration (Stripe/PayPal)
- User profiles and statistics

## License

MIT License - Feel free to use for educational purposes

## Author

ARENA Development Team
