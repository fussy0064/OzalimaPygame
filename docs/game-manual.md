# DebtCollector Game Manual

## What The Game Is

DebtCollector is a 2D collector game built with Python and Pygame. You control Ozalima and try to catch falling notes while avoiding coins.

## Quick Start

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

## Controls

- Left Arrow: move Ozalima left
- Right Arrow: move Ozalima right
- P: pause or resume
- R: restart after a win or loss
- Escape: quit the game

## Core Rules

- Notes are the correct targets.
- Coins are hazards.
- Catching a note gives +10 score.
- Catching a coin removes 1 life and subtracts 5 score.
- Ozalima starts with 3 lives.
- The game ends when lives reach 0.

## Levels

Progress is based on collected notes.

- 25 notes: Level 2 starts, speed bonus becomes +2
- 50 notes: Level 3 starts, speed bonus becomes +4
- 75 notes: Win state, speed bonus becomes +6

The speed bonus increases the falling speed of objects and makes the game harder over time.

## User Interface

The HUD shows:

- Current score
- Remaining lives
- Current level
- Notes collected
- Active speed bonus

The game also shows temporary banners when a level is completed, when Ozalima wins, and when Ozalima dies.

## Assets

The game tries to load these image files when they exist:

- `background.jpeg`
- `assets/woman.png`
- `assets/coin.png`
- `assets/coin1.png`
- `assets/note.jpeg`
- `assets/Note1.png`

If an image is missing, the game uses built-in fallback graphics so it still runs.

## Technical Notes

- The game uses object-oriented Python code.
- The background image is loaded during game setup, after the display is created.
- The falling objects are generated randomly from the top of the screen.
- The game includes pause, restart, win, and game-over states.

## Project Files

- `main.py`: main game source code
- `README.md`: project overview and documentation link
- `requirements.txt`: Python dependency list
- `assets/`: sprite assets used by the game
- `background.jpeg`: background image for the game

## Troubleshooting

- Install `pygame` if the game will not start.
- Make sure `background.jpeg` stays in the project root.
- If an asset file is missing, the fallback graphics should still keep the game playable.
