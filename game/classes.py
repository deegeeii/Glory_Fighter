#=== Game Package Files ===

# game/classes.py
# Player base class and three subclasses: Settler, Warrior, Merchant.

class Player:
    """Base class — every player type inherits from this."""

    GLORY_TARGET = 10  # class variable — shared by ALL instances

    def __init__(self, name, player_id):
        self.name      = name
        self.player_id = player_id   # int 1-4, one per terminal
        self.glory     = 0
        self.health    = 10          # subclasses override this
        self.attack    = 2
        self.defence   = 2
        self.resources = {
            "ore":    0,
            "grain":  0,
            "lumber": 0,
            "brick":  0,
            "wool":   0,
        }
        self.special_name = "None"

    # ── Properties ─────────────────────────────────
    # @property turns a method into a readable attribute.
    # player.is_alive reads like a variable but runs logic.

    @property
    def is_alive(self):
        return self.health > 0

    @property
    def has_won(self):
        return self.glory >= self.GLORY_TARGET

    # ── Resource methods ────────────────────────────

    def gain_resource(self, resource, amount=1):
        """Add resources. amount defaults to 1 if not specified."""
        if resource in self.resources:
            self.resources[resource] += amount
            print(f"  {self.name} gains {amount} {resource}.")

    def spend_resource(self, resource, amount=1):
        """Spend resources. Returns True if successful, False if not."""
        if self.resources.get(resource, 0) >= amount:
            self.resources[resource] -= amount
            return True
        print(f"  Not enough {resource} (have {self.resources.get(resource,0)}, need {amount}).")
        return False

    # ── Combat methods ──────────────────────────────

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        print(f"  {self.name} takes {amount} damage. HP: {self.health}")

    def use_special(self):
        # Subclasses override this with their unique ability
        print(f"  {self.name} uses {self.special_name}!")

    # ── Display methods ─────────────────────────────

    def status(self):
        """Print a full status readout for this player."""
        r = "  ".join(
            f"{k}:{v}" for k, v in self.resources.items()
        )
        print(f"\n[ {self.name} | {self.__class__.__name__} ]")
        print(f"  HP: {self.health}  ATK: {self.attack}  DEF: {self.defence}  Glory: {self.glory}/{self.GLORY_TARGET}")
        print(f"  Resources: {r}")

    def __repr__(self):
        # __repr__ controls what prints when you do print(player)
        # or inspect it in the Python shell
        return (
            f"<{self.__class__.__name__} '{self.name}' "
            f"HP:{self.health} Glory:{self.glory}>"
        )


# ════════════════════════════════════════════════
# SUBCLASSES
# Each calls super().__init__() first, then overrides
# only what's different from the base Player.
# ════════════════════════════════════════════════

class Settler(Player):
    """Builds fast. Earns Glory through construction.
    Low health and attack — hard to kill, bad at fighting."""

    def __init__(self, name, player_id):
        super().__init__(name, player_id)  # run Player.__init__ first
        self.health       = 8    # override base health
        self.attack       = 1    # override base attack
        self.defence      = 3    # override base defence
        self.build_bonus  = 2    # unique attribute — only Settler has this
        self.special_name = "Rapid Settlement"

    def use_special(self):
        """Spend 1 brick + 1 lumber → gain build_bonus Glory."""
        brick_ok  = self.spend_resource("brick")
        lumber_ok = self.spend_resource("lumber")
        if brick_ok and lumber_ok:
            self.glory += self.build_bonus
            print(f"  {self.name} rapidly settles! +{self.build_bonus} Glory. Total: {self.glory}")
        else:
            print("  Rapid Settlement needs 1 brick + 1 lumber.")


class Warrior(Player):
    """Fights hard. Earns Glory through combat kills.
    High health and attack — fragile defence."""

    def __init__(self, name, player_id):
        super().__init__(name, player_id)
        self.health       = 14
        self.attack       = 4
        self.defence      = 1
        self.rage_stacks  = 0   # unique — tracks how many rages used
        self.special_name = "Battle Rage"

    def use_special(self):
        """Spend 1 ore → +2 attack permanently this session."""
        if self.spend_resource("ore"):
            self.attack      += 2
            self.rage_stacks += 1
            print(
                f"  {self.name} enters Battle Rage! "
                f"Attack now {self.attack}. Rage stacks: {self.rage_stacks}"
            )
        else:
            print("  Battle Rage needs 1 ore.")


class Merchant(Player):
    """Trades resources. Earns Glory through accumulation.
    Balanced stats — wins through economy, not combat."""

    def __init__(self, name, player_id):
        super().__init__(name, player_id)
        self.health       = 10
        self.attack       = 2
        self.defence      = 2
        self.trade_rate   = 2   # unique — trades at 2:1 instead of 4:1
        self.special_name = "Market Surge"

    def use_special(self):
        """Spend 2 wool + 1 grain → gain 1 Glory and 2 ore."""
        wool_ok  = self.spend_resource("wool", 2)
        grain_ok = self.spend_resource("grain")
        if wool_ok and grain_ok:
            self.glory += 1
            self.gain_resource("ore", 2)
            print(f"  {self.name} floods the market! +1 Glory. Total: {self.glory}")
        else:
            print("  Market Surge needs 2 wool + 1 grain.")


