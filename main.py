#=== Entry Point ===

# Entry point. Run this file to start the game: python main.py

# main.py imports from game package:

import os
import sys
from dotenv import load_dotenv
from game.classes import Settler, Warrior, Merchant
from game.engine import GameEngine
from game.visuals import show_turn_banner

# Load .env into os.environ before reading any secrets
load_dotenv()
GAME_PASSWORD = os.environ.get("GAME_PASSWORD", "changeme")

# Maps uuser input to the correct class
# Same factory patter from the adventure game, dict of classes

CLASS_MAP = {
    "1": Settler,
    "2": Warrior,
    "3": Merchant,
}

CLASS_INFO = {
    "1": "Settler - HP:8  ATK:1 DEF:3 Special: Rapid Settlement",
    "2": "Warrior - HP:14 ATK:4 DEF:1 Special: Battle Rage",
    "3": "Merchant - HP:10 ATK:2 DEF:2 Special: Market Surge",
}


def authenticate():
    # Gate entry behind the GAME_PASSWORD from .env

    # Gives the player 3 attempts before exiting.
    # sys.exit(1) signals a non-zero exit code.
    # a standard convention for 'program ended due to an error'

    print("\n === CATAN FIGHTER ===")
    print(" Enter the game password to continue.\n")

    for attempt in range(1, 4):
        pw = input("  Password:  ").strip()
        if pw == GAME_PASSWORD:
            print(" Access granted.\n")
            return
        remaining = 3 - attempt
        if remaining > 0:
            print(f"  Wrong password. {remaining} attempt(s) left.")
        else:
            print(" Too many failed attemps. Exiting.")
            sys.exit(1)

def setup_player():
    # Prompt for player ID, name, and class choice.

    # Returns (player_id, Player instance).
    # player_id must be unique per terminal (1 through MAX_PLAYERS)

    print("  --- Player Setup ---\n")

    while True:
        try:
            pid = int(input("  Your player ID (1-4): ").strip())
            if pid in range(1, 5):
                break
            print("  Please enter a number between 1 and 4.")
        except ValueError:
            print("  Please enter a number.")

    name = input("  Your character name: ").strip()
    if not name:
        name = f"Player{pid}"  # fallback if they hit Enter

    print("\n  Choose your class:")
    for key, info in CLASS_INFO.items():
        print(f"  {key}. {info}")

    while True:
        choice = input("\n  Enter 1, 2, or 3: ").strip()
        if choice in CLASS_MAP:
            break
        print("  Invalid choice - enter 1, 2, or 3.")

    CharClass = CLASS_MAP[choice]
    player    = CharClass(name, pid)

    print(f"\n  {name} the {player.__class__.__name__} is ready. \n")
    player.status()
    return pid, player

def setup_all_players():
    # Register between 2 and 4 players on this machine
    # in real multi-terminal session each machine runs main.py
    # once and registers on player. 
    # For local play, this loop lets you add 2-4 player
    # in the same terminal

    players = {}

    while True:
        try:
            count = int(input("  How many players? (2-4): ").strip())
            if count in range(2, 5):
                break
            print("  Enter a number between 2 and 4.")
        except ValueError:
            print("  Please enter a number.")

    for i in range(count):
        print(f"\n  --- Registering player {i + 1} of {count} ---")
        pid, player = setup_player()
        while pid in players:
            print(f"  Player ID {pid} is already taken. Choose another.")
            pid, player = setup_player()
        players[pid] = player
    
    return players

# ---- Entry Point ----
# The if __name__ guard means this black only runs when you 
# execute main.py directly - not when its imported elsewhere

if __name__ == "__main__":
    authenticate()
    players = setup_all_players()
    engine  = GameEngine(players)
    engine.run()
