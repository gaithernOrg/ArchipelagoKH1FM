"""
Shared OptionFilter constants, built once at import time and reused across the whole package.

Using OptionFilter (instead of branching on an already-resolved Python value at construction time)
is what makes a Rule tree option-generic: the condition becomes data inside the tree, checked at
`.resolve(world)` time against whatever world is being resolved, rather than being baked in when
the tree was built. That's what lets `Rule.to_dict()` exported JSON stay valid across any options.

Don't use these for conditions that gate whether a *location* is created at all (e.g. super_bosses/
cups/hundred_acre_wood/atlantica/jungle_slider/destiny_islands/final_rest_door_key, per Regions.py)
- those must stay a plain Python condition, since OptionFilter only affects rule resolution, not
location existence.
"""

from rule_builder.options import OptionFilter

from ..Data import LOGIC_BEGINNER, LOGIC_NORMAL, LOGIC_PROUD, LOGIC_MINIMAL
from ..Options import (
    EndoftheWorldUnlock,
    FinalRestDoorKey,
    HalloweenTownKeyItemBundle,
    HundredAcreWood,
    KeybladesUnlockChests,
    LogicDifficulty,
    StackingWorldItems,
)

ABOVE_BEGINNER = OptionFilter(LogicDifficulty, LOGIC_BEGINNER, "gt")
ABOVE_NORMAL = OptionFilter(LogicDifficulty, LOGIC_NORMAL, "gt")
ABOVE_PROUD = OptionFilter(LogicDifficulty, LOGIC_PROUD, "gt")
AT_LEAST_MINIMAL = OptionFilter(LogicDifficulty, LOGIC_MINIMAL, "ge")
BELOW_MINIMAL = OptionFilter(LogicDifficulty, LOGIC_MINIMAL, "lt")
EXACTLY_BEGINNER = OptionFilter(LogicDifficulty, LOGIC_BEGINNER, "eq")
NOT_EXACTLY_BEGINNER = OptionFilter(LogicDifficulty, LOGIC_BEGINNER, "ne")

HUNDRED_ACRE_WOOD_ON = OptionFilter(HundredAcreWood, True, "eq")
HUNDRED_ACRE_WOOD_OFF = OptionFilter(HundredAcreWood, False, "eq")
KEYBLADES_UNLOCK_CHESTS_ON = OptionFilter(KeybladesUnlockChests, True, "eq")
KEYBLADES_UNLOCK_CHESTS_OFF = OptionFilter(KeybladesUnlockChests, False, "eq")
STACKING_WORLD_ITEMS_ON = OptionFilter(StackingWorldItems, True, "eq")
HALLOWEEN_TOWN_KEY_ITEM_BUNDLE_ON = OptionFilter(HalloweenTownKeyItemBundle, True, "eq")

FINAL_REST_DOOR_LUCKY_EMBLEMS = OptionFilter(FinalRestDoorKey, "lucky_emblems", "eq")
FINAL_REST_DOOR_NOT_LUCKY_EMBLEMS = OptionFilter(FinalRestDoorKey, "lucky_emblems", "ne")
EOTW_UNLOCK_LUCKY_EMBLEMS = OptionFilter(EndoftheWorldUnlock, "lucky_emblems", "eq")
