#=== Game Package Files ===

## game/engine.py
# Turn loop, shared JSON state, Glory tracking, and win condition.

import json
import os
from pathlib import Path
from dotenv  import load_dotenv

from game.board   import Board
from game.combat  import resolve_combat
from game.visuals import (
    show_turn_banner,
    show_scoreboard,
    show_fireworks,
)

# Load .env values into os.environ as soon as this module imports
load_dotenv()
MAX_PLAYERS = int(os.environ.get("MAX_PLAYERS", 4))
SAVE_PATH   = Path("data/saves/game_state.json")


class GameEngine:
    """Owns the turn loop and game state.

    players — dict of {player_id (int): Player instance}
    All player_ids must be integers matching the keys.
    """

    def __init__(self, players: dict):
        self.players     = players
        self.board       = Board()
        self.turn_number = 1
        # active_ids tracks who is still in the game
        self.active_ids  = list(players.keys())

        # Ensure the save directory exists before the first write
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # ── State persistence ────────────────────────────

    def save_state(self):
        """Serialise current game state to JSON.

        Called after every turn so all terminals
        can read the latest state from disk.
        pathlib.Path.write_text() handles file open/close safely.
        """
        state = {
            "turn": self.turn_number,
            "active_ids": self.active_ids,
            "players": {
                str(pid): {
                    "name":      p.name,
                    "class":     p.__class__.__name__,
                    "glory":     p.glory,
                    "health":    p.health,
                    "attack":    p.attack,
                    "defence":   p.defence,
                    "resources": p.resources,
                }
                for pid, p in self.players.items()
            }
        }
        SAVE_PATH.write_text(json.dumps(state, indent=2))
        print(f"  [State saved — turn {self.turn_number}]")

    def load_state(self):
        """Read the latest saved state from disk.

        Returns the parsed dict, or None if no save exists yet.
        Used by other terminals to read current standings.
        """
        if not SAVE_PATH.exists():
            return None
        return json.loads(SAVE_PATH.read_text())

    # ── Win condition ────────────────────────────────

    def check_winner(self):
        """Return the winning Player if anyone has reached 10 Glory.
        Returns None if no winner yet.
        """
        for p in self.players.values():
            if p.has_won:
                return p
        return None

    # ── Turn actions ─────────────────────────────────

    def action_settle(self, player):
        """Show the board and let the player place a settlement."""
        self.board.show_board()
        try:
            tid = int(input("  Tile ID to settle on (0-18): ").strip())
            self.board.place_settlement(player, tid)
        except ValueError:
            print("  Invalid tile ID.")

    def action_attack(self, player):
        """List living targets and resolve combat against the chosen one."""
        targets = [
            p for p in self.players.values()
            if p.is_alive and p.player_id != player.player_id
        ]
        if not targets:
            print("  No targets available.")
            return

        print("\n  Choose a target:")
        for i, t in enumerate(targets, 1):
            print(f"    {i}. {t.name} ({t.__class__.__name__}) HP:{t.health}")
        try:
            idx = int(input("  Attack who? ").strip()) - 1
            if 0 <= idx < len(targets):
                resolve_combat(player, targets[idx])
                # Remove defeated players from active list
                for t in targets:
                    if not t.is_alive and t.player_id in self.active_ids:
                        self.active_ids.remove(t.player_id)
                        print(f"  {t.name} has been eliminated.")
            else:
                print("  Invalid target.")
        except ValueError:
            print("  Invalid input.")

    def free_placement(self, player, grant_resources: bool = False):
        # Prompt the player to place one free settlement
        # Keep prompting until til is chosen

        self.board.show_board()
        while True:
            try:
                tid = int(input(
                    f"  {player.name} - choose a tile to settle (0-18)"
                ).strip())
                success = self.board.place_free_settlement(
                    player, tid, grant_resources=grant_resources
                )
                if success:
                    break
            except ValueError:
                print("  Please enter a tile number.")

    def setup_phase(self):
        """Run the pre-game setup — two free placements per player.

        Round 1: every player places one settlement, no resources.
        Round 2: every player places a second settlement and
                 immediately receives 1 resource from that tile.

        This guarantees every player has income tiles and
        starting resources before the first real turn.
        """
        print("\n  === SETUP PHASE ===")
        print("  Each player places 2 free settlements.")
        print("  Your second placement grants 1 starting resource.\n")

        player_list = list(self.players.values())

        # Round 1 — forward order, no resources granted
        print("  -- Round 1: first placement --")
        for player in player_list:
            self.free_placement(player, grant_resources=False)

        # Round 2 — reverse order (classic Catan snake draft)
        # and grant 1 resource from the chosen tile
        print("\n  -- Round 2: second placement (grants resources) --")
        for player in reversed(player_list):
            self.free_placement(player, grant_resources=True)

        print("\n  Setup complete. Good luck!\n")
        show_scoreboard(self.players)


    # ── Main turn ────────────────────────────────────

    def run_turn(self, player):
        """Run one full turn for a single player.

        Order: banner → status → dice roll → resource collection
               → action menu → save state → scoreboard.
        """
        show_turn_banner(player.name, self.turn_number)
        player.status()

        # Roll dice and collect resources
        d1, d2, total = self.board.roll_dice()
        print(f"\n  Dice rolled: {d1} + {d2} = {total}")
        self.board.collect_resources(self.players, total)

        # Action menu
        print("\n  Actions:")
        print("    1. Settle a tile  (costs 1 brick, lumber, grain, wool)")
        print("    2. Attack a player")
        print("    3. Use special ability")
        print("    4. Pass")

        action = input("\n  Choose action (1-4): ").strip()

        if   action == "1": self.action_settle(player)
        elif action == "2": self.action_attack(player)
        elif action == "3": player.use_special()
        elif action == "4": print("  Turn passed.")
        else:              print("  Invalid action — turn passed.")

        # Save and display scoreboard after every turn
        self.save_state()
        show_scoreboard(self.players)
        self.turn_number += 1

    # ── Game loop ────────────────────────────────────

    def run(self):
        """Main game loop — cycles through active players until
        someone reaches 10 Glory or only one player remains.
        """
        print("\n  === CATAN FIGHTER BEGINS ===")
        self.board.show_board()

        while True:
            for pid in list(self.active_ids):
                player = self.players[pid]

                # Skip eliminated players
                if not player.is_alive:
                    continue

                self.run_turn(player)

                # Check win condition after every individual turn
                winner = self.check_winner()
                if winner:
                    show_fireworks(winner.name)
                    print(f"\n  Game over. {winner.name} wins with {winner.glory} Glory!")
                    return winner

                # End game if only one player left alive
                if len(self.active_ids) == 1:
                    survivor = self.players[self.active_ids[0]]
                    show_fireworks(survivor.name)
                    print(f"\n  Last one standing: {survivor.name}!")
                    return survivor

            