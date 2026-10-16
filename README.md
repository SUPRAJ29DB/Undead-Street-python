<<<<<<< HEAD
# Undead Streets — Python Zombie Survival

A complete top-down zombie survival game built with **Python 3.10+ and Pygame**. All visuals are drawn in code; no external art assets are required.

## Features
- Real-time top-down survival gameplay
- WASD / arrow-key movement
- Mouse aiming and left-click shooting (hold to autofire)
- Chasing zombie AI and bullet/player collision detection
- Health, temporary invulnerability after damage, and game-over state
- Score for zombie kills and health-pack pickups
- Medkit drops restore health
- Increasing spawn rate and zombie speed in timed waves
- Restart using `R` or the on-screen button
- Neon apocalypse visuals, HUD, health bar, and particle bursts

## Requirements
- Python 3.10 or newer
- Pygame 2.6.1

## Run on Windows
1. Extract this ZIP.
2. Open the extracted `Undead_Streets_Python` folder in VS Code or File Explorer.
3. In the folder address bar, type `powershell` and press Enter.
4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the game:

   ```powershell
   python game.py
   ```

Or double-click `run_game.bat`.

## Controls
| Action | Controls |
|---|---|
| Move | `W A S D` or arrow keys |
| Aim | Mouse pointer |
| Shoot | Left mouse button (hold for autofire) |
| Restart after game over | `R` or click PLAY AGAIN |
| Quit | `Esc` |

## Build a Windows EXE
Double-click `build_exe.bat`, or run:

```powershell
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name UndeadStreets game.py
```

The executable will be created at `dist\UndeadStreets.exe`. Build it on Windows for a Windows executable. The target computer does not need Python installed.

## Project structure
```text
Undead_Streets_Python/
├── game.py
├── requirements.txt
├── run_game.bat
├── build_exe.bat
├── README.md
└── .gitignore
```
=======
# Undead-Street-python
>>>>>>> origin/main
