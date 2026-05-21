# DebtCollector

DebtCollector is a beginner-friendly 2D collector game built with Python and Pygame.
The player controls Ozalima and must catch falling notes while avoiding coins.

Full documentation is available in [docs/game-manual.md](/home/fussy/Desktop/DebtCollector/docs/game-manual.md).

## Overview

- Single-player arcade game
- 2D falling-object collector
- Background image based scene with simple animated gameplay objects
- Score, lives, level progression, pause, restart, win, and loss states

## Run

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

## Controls

- Left Arrow: move Ozalima left
- Right Arrow: move Ozalima right
- P: pause or resume
- R: restart after game over or win
- Escape: quit

## Gameplay Rules

- Catch falling notes to gain $10 score each.
- Catching a coin costs $5 score and 1 life.
- The player starts with 3 lives.
- The game ends when lives reach 0.

## Level Progression

The game uses note collection to drive level changes.

- 25 notes: Level 2, speed bonus +2
- 50 notes: Level 3, speed bonus +4
- 75 notes: Win state, speed bonus +6

The speed bonus increases the falling speed of objects and also makes the spawn rate harder over time.

## On-Screen UI

The HUD shows:

- Current score
- Remaining lives
- Current level
- Notes collected
- Active speed bonus

The game also shows temporary banners when a level is finished or when Ozalima wins or dies.

## Assets

The game uses image assets when they are available in the project folder.

- [background.jpeg](/home/fussy/Desktop/DebtCollector/background.jpeg): main background image
- [assets/woman.png](/home/fussy/Desktop/DebtCollector/assets/woman.png): Ozalima sprite
- [assets/coin.png](/home/fussy/Desktop/DebtCollector/assets/coin.png): coin sprite
- [assets/coin1.png](/home/fussy/Desktop/DebtCollector/assets/coin1.png): alternate coin asset
- [assets/note.jpeg](/home/fussy/Desktop/DebtCollector/assets/note.jpeg): note sprite
- [assets/Note1.png](/home/fussy/Desktop/DebtCollector/assets/Note1.png): alternate note asset

If an image is missing, the game falls back to built-in placeholder graphics so it still runs.

## Folder Structure

- [main.py](/home/fussy/Desktop/DebtCollector/main.py) - game source code
- [requirements.txt](/home/fussy/Desktop/DebtCollector/requirements.txt) - Python dependency list
- [README.md](/home/fussy/Desktop/DebtCollector/README.md) - game documentation
- [assets/](/home/fussy/Desktop/DebtCollector/assets) - image assets used by the game

## How The Game Works

Ozalima moves left and right at the bottom of the screen. Notes and coins fall from the top with random spawn positions. Notes are the correct targets and coins are hazards. The game gradually gets faster as time passes and as more notes are collected.

## Technical Notes

- Built with object-oriented Python code
- Uses `pygame` for rendering, input, and the game loop
- Loads the background image during game setup so the window is ready first
- Includes safe fallback art so the game can still run if an asset is missing

## Troubleshooting

- If the game does not open, make sure `pygame` is installed.
- If an image file is missing, the fallback graphics will still let the game run.
- If you want to change the visuals, replace the image files in `assets/` or `background.jpeg`.
