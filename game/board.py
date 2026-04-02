#=== Game Package Files ===

# game/board.py
# Board layout, resource tiles, dice engine, and settlement placement.

import random
from dataclasses import dataclass, field
from typing import List, Dict


# @dataclass --- auto-generates __init__, __repr__, and __eq__
# so we don't have to write them manually for a simple container.

@dataclass
class Tile:
    # One resource tile on the board.

    resource: str       # "ore", "grain", "lumber", "brick", "wool", "desert"
    number:   int       # dice roll that activates this tile (2-12)
    tile_id:  int       # index 0-18
    owners:   List[int] = field(default_factory=list)

    # owners = list of player_ids with a settlement here
    # field(default_factory=list) is REQUIRED for mutable defaults
    # in dataclasses - never write owners=[] directly

class Board:
    # The game board -- 19 tiles, classic Catan layout.
    # Tiles are stored as a flat list indexed by tile_id.
    # the layout tuple defines (resource, activation_number) pairs

    # Classic Catan layout --  Numbers chosen to match real Catan probability distribution.

    TILE_LAYOUT = [
        ("ore",     10), ("grain",  2), ("lumber",  9),
        ("brick",   12), ("wool",   6),  ("grain",  4),  ("lumber", 10),
        ("ore",    9),  ("wool",   11), ("desert", 7),  ("wool",   3),
        ("ore",    8),  ("lumber", 8),  ("brick",  3),  ("grain",  4),
        ("wool",   5),  ("brick",  5),  ("grain",  6),  ("lumber", 11),
    ]

    # Emoji icons for display - maps resource name to symbol
    ICONS = {
        "ore":      "[ORE]",
        "grain":    "[GRN]",
        "lumber":   "[LMB]",
        "brick":    "[BRK]",
        "wool":     "[WOL]",
        "desert":   "[DST]",
    }

    def __init__(self):
        # List comprehension builds all 19 Tile objects at once
        self.tiles: List[Tile] = [
            Tile(resource=r, number=n, tile_id=i)
            for i, (r, n) in enumerate(self.TILE_LAYOUT)
        ]

#--- DICE ----


    def roll_dice(self):
        # Roll two six sided dice.

        # Returns (die1, die2, total).
        # Two dice = bell curve distribution

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        return d1, d2, d1 + d2

    #---  Resources  -----

    def collect_resources(self, players: Dict, roll_total: int):
        # Pay out resources to every player settled on a matching tile. 

        # Players is a dict {player_id: Player}
        # roll_total is the sum of both dice

        if roll_total == 7:
            print("  Rolled 7 - robber blocks! No resources paid out.")
            return
        
        paid = False
        for tile in self.tiles:
            if tile.number == roll_total and tile.resource != "desert":
                for pid in tile.owners:
                    if pid in players:
                        players[pid].gain_resource(tile.resource)
                        paid = True
        if not paid:
            print("  No settlements on active tiles. No resources paid.")


    #--- Settlements ------

    def place_settlement(self, player, tile_id: int):
        # place a settlement on a tile.
        # awards 1 Glory for the settlement.
        # a tile can have multiple owners - each gets paid on roll.

        if tile_id < 0 or tile_id >= len(self.tiles):
            print(f"  Tile {tile_id} doesn't exist. Choose 0-18.")
            return
        tile = self.tiles[tile_id]

        if tile.resource == "desert":
            print("  Can't settle the desert - no resources there.")
            return
        
        if player.player_id in tile.owners:
            print(f"  {player.name} already has a settlement on tile {tile_id}.")
            return
        
        # check build cost: 1 brick + 1 lumber + 1 grain + 1 wool
        costs = [("brick", 1), ("lumber", 1), ("grain", 1), ("wool", 1)]
        for resource, amount in costs:
            if player.resources.get(resource, 0) < amount:
                print(
                    f"  Not enough resources to settle.\n"
                    f"  Need: 1 brick, 1 lumber, 1 grain, 1 wool."
                )
                return
        
        for resource, amount in costs:
            player.spend_resource(resource, amount)

        tile.owners.append(player.player_id)
        player.glory += 1
        print(
            f"  {player.name} settles tile {tile_id} "
            f"({self.ICONS[tile.resource]} #{tile.number}). "
            f"+1 Glory. Total: {player.glory}"
        )

#--- Display ----

    def show_board(self):
        """Print a readable board summary."""
        print("\n--- Board (19 tiles) ---")
        print(f"  {'ID':>2}  {'Resource':<8}  {'#':>2}  Owners")
        print(f"  {'--':>2}  {'--------':<8}  {'--':>2}  ------")
        for t in self.tiles:
            icon    = self.ICONS[t.resource]
            owners  = ", ".join(str(o) for o in t.owners) or "—"
            print(f"  {t.tile_id:>2}  {icon:<8}  {t.number:>2}  {owners}")
        print()
