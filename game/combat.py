#=== Game Package Files ===

# game/combat.py
# Combat resolution — dice rolls modified by resources spent.

# combat.py imports from visuals only:
import random

def roll_combat_dice(bonus: int = 0) -> int:
    # Roll 2d6 and add a bonus

    # returns the total as a single integet.
    # bonus comes from the player's attack or defence stat
    # plus anuy resources they choose to spend.

    return random.randint(1, 6) + random.randint(1, 6) + bonus

def get_combat_boost(player, role: str) -> int:
    # Ask the active player if they want to spend resources to boost.

    # role is either "attack" or "defence".
    # Attack boost costs ore - each ore spent = +2 to attack roll.
    # Defence boost costs wool - each wool spen = +2 to defence roll
    # Returns the total bonus as an integer.

    resource = "ore" if role == "attack" else "wool"
    available = player.resources.get(resource, 0)

    if available == 0:
        # No resources to spend - skip the prompt entirely
        return 0
    
    print(f"\n  {player.name}: spend {resource} for +2 per unit?")
    print(f" You have {available} {resource} available.")

    try:
        raw     = input(f"  How many to spend: (0-{available}): ").strip()
        spend   = int(raw)
        # Clamp between 0 and what they actually have
        spend= max(0, min(spend, available))
        player.spend_resource(resource, spend)
        return spend * 2
    except ValueError:
        # If they type something that isn't a number, spend nothing
        print("  Invalid input - spending 0.")
        return 0
    
def resolve_combat(attacker, defender):
    # Full combat resolution between two players.
    """
    Flow:
    1. Both sides optionally spend resources for a boost.
    2. both sides roll 2d6 + stat + boost.
    3. Damage = max(0, attacker roll - defender roll)
    4. Defender takes damage.
    5. If defender dies -> attacker gains 3 Glory.
    6. Visuals fire if kill or win condition reached.

    Imports visuals inside the function so that the module 
    can be imported safely even before visuals.py is complete.
    """

    from game.visuals import show_skull, show_fireworks

    print(f"\n{'='*48}")
    print(f"  COMBAT: {attacker.name} attacks {defender.name}!")
    print(f"{'='*48}")

# --- Resource boost phase -----

    atk_boost = get_combat_boost(attacker, "attack")
    def_boost = get_combat_boost(defender, "defence")

    # ---- Roll Phase ----

    atk_roll = roll_combat_dice(attacker.attack + atk_boost)
    def_roll = roll_combat_dice(defender.defence + def_boost)

    print(f"\n  {attacker.name} rolls:  {atk_roll}")
    print(f"  {defender.name} rolls: {def_roll}")

    # --- Damage Phase ----

    damage = max(0, atk_roll - def_roll)
    print(f"\n  Damage dealt: {damage}")
    defender.take_damage(damage)

    # ── Outcome phase ───────────────────────────────
    if not defender.is_alive:
        print(f"\n  {defender.name} has been defeated!")
        show_skull(defender.name)
        attacker.glory += 3
        print(f"  {attacker.name} earns 3 Glory! Total: {attacker.glory}")
        if attacker.has_won:
            show_fireworks(attacker.name)
    else:
        print(
            f"\n  {defender.name} survives with {defender.health} HP."
        )
    print(f"{'='*48}\n")
