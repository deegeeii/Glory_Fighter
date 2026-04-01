#=== Game Package Files ===

# Without __init__.py: Python sees game/ as a plain directory. Importing from it fails.
# With __init__.py: Python treats game/ as a package. You can import any module inside it using dot notation.
# With content in __init__.py: You control what gets exposed at the top level — so from game import Settler works instead of from game.classes import Settler.

# game/__init__.py
# Exposes key classes at the package level.
# Allows: from game import Settler, Warrior, Merchant, GameEngine


from game.classes import Settler, Warrior, Merchant
from game.engine import GameEngine




