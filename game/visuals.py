#=== Game Package Files ===

# game/visuals.py
# Terminal visuals — ASCII fireworks, skull, and turn banners.

import time
from colorama import init, Fore, Style

# Must be called once before any colored output.
# autoreset=True resets color automatically after each print.

init(autoreset=True)

# --- ASCII art constants -------
# Defined once at module level - imported wherever needed.
# Each uses Fore.COLOR to set color and Style.RESET_ALL to end it


SKULL = f"""
{Fore.RED}
    ░░░░░░░░░
  ░░         ░░
  ░  ◉     ◉  ░
  ░     ▲     ░
  ░   \\___/   ░
  ░░░░░░░░░░░░░
    ░  ░ ░  ░
    ░  ░ ░  ░
{Style.RESET_ALL}"""

# Fireworks animate as two frames printed in sequence
FIREWORK_FRAME_1 = f"""
{Fore.YELLOW}           *
{Fore.YELLOW}         * | *
{Fore.YELLOW}       *   |   *
{Fore.YELLOW}     *  \\  |  /  *
{Fore.YELLOW}  * — — — [*] — — — *
{Fore.YELLOW}     *  /  |  \\  *
{Fore.YELLOW}       *   |   *
{Fore.YELLOW}         * | *
{Fore.YELLOW}           *
{Style.RESET_ALL}"""

FIREWORK_FRAME_2 = f"""
{Fore.GREEN}     \\    |    /
{Fore.GREEN}       \\  |  /
{Fore.GREEN}  — — — [*] — — —
{Fore.GREEN}       /  |  \\
{Fore.GREEN}     /    |    \\
{Style.RESET_ALL}"""

FIREWORK_FRAME_3 = f"""
{Fore.CYAN}   *       *       *
{Fore.CYAN}      *    |    *
{Fore.CYAN}  *  — — [***] — —  *
{Fore.CYAN}      *    |    *
{Fore.CYAN}   *       *       *
{Style.RESET_ALL}"""


# ── Visual functions ─────────────────────────────────────────

def show_skull(player_name: str):
    # Print the skull and defeated message with a pause
    print(SKULL)
    print(Fore.RED + Style.BRIGHT + f"  {player_name} has fallen.")
    time.sleep(1.5)

def show_fireworks(player_name: str):
    # Animate three fireworks frames the print the victory message.
    for frame in [FIREWORK_FRAME_1, FIREWORK_FRAME_2, FIREWORK_FRAME_3]:
        print(frame)
        time.sleep(0.5)
    print(
        Fore.YELLOW + Style.BRIGHT + 
        f"\n  *** {player_name} reaches 10 GLORY!  ***"
        f"\n  *** VICTORY! THE REALM IS YOURS! ***\n"
    )
    time.sleep(2)

def show_turn_banner(player_name: str, turn_number: int):
    # Print a colored turn header at the start of each turn.
    print(Fore.CYAN + Style.BRIGHT + f"/n{'='*48}")
    print(Fore.CYAN + Style.BRIGHT + f"  Turn {turn_number} — {player_name}'s move")
    print(Fore.CYAN + Style.BRIGHT + f"{'='*48}")

def show_glory_bar(player_name: str, glory: int, target: int = 10):
    # """Print a simple ASCII progress bar for Glory."""
    filled = int((glory / target) * 20)
    bar    = "█" * filled + "░" * (20 - filled)
    color  = Fore.YELLOW if glory >= target * 0.8 else Fore.WHITE
    print(color + f"  {player_name:12} [{bar}] {glory}/{target} Glory")


def show_scoreboard(players: dict):
    # """Print a Glory scoreboard for all active players."""
    print(Fore.CYAN + "\n--- Glory Scoreboard ---")
    for player in players.values():
        show_glory_bar(player.name, player.glory)
    print()
