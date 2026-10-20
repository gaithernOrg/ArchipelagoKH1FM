import csv
from importlib.resources import files
from typing import Dict, List, NamedTuple, Optional


class SpellLevel(NamedTuple):
    index: int
    name: str
    sysmsg_index: int


def load_rows(file_name: str, encoding: Optional[str] = None) -> List[Dict[str, str]]:
    with files(__name__).joinpath(file_name).open(encoding=encoding) as file:
        return list(csv.DictReader(file))


def group_spell_levels_by_spell(rows: List[Dict[str, str]]) -> Dict[str, List[SpellLevel]]:
    levels_by_spell: Dict[str, List[SpellLevel]] = {}
    for index, row in enumerate(rows):
        level = SpellLevel(index, row["level"], int(row["sysmsg_index"]))
        levels_by_spell.setdefault(row["item"], []).append(level)
    return levels_by_spell


def group_rows_by_character(rows: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    rows_by_character: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        rows_by_character.setdefault(row["character"], []).append(row)
    return rows_by_character


items = load_rows("items.csv")
event_items = load_rows("event_items.csv")
locations = load_rows("locations.csv")
event_locations = load_rows("event_locations.csv")

weapon_stats = load_rows("weapon_stats.csv")
ability_ap_costs = load_rows("ability_ap_costs.csv", "utf-8")
spells = load_rows("spells.csv")
level_up_stats = load_rows("level_up_stats.csv")
party_level_ups = load_rows("party_level_ups.csv")

char_to_kh = load_rows("char_to_kh.csv", "utf-8")
item_help = load_rows("item_help.csv", "utf-8")
words = load_rows("words.csv", "utf-8")
system_messages = load_rows("system_messages.csv", "utf-8")

CHAR_TO_KH = {row["char"]: int(row["byte"], 16) for row in char_to_kh}
MP_COST_LABELS = {15: "0.5 CP", 30: "1 CP", 100: "1 MP", 200: "2 MP", 300: "3 MP"}
POSSIBLE_SPELL_COSTS = list(MP_COST_LABELS)

WORD = [row["text"] for row in words]
ITEMHELP = [row["text"] for row in item_help]
SYSMSG = [row["text"] for row in system_messages]

SPELL_LEVELS_BY_SPELL = group_spell_levels_by_spell(spells)
VANILLA_SPELL_LEVEL_COSTS = [int(row["vanilla_cost"]) for row in spells]
VANILLA_SPELL_COSTS = [30, 30, 100, 100, 100, 200, 200]
VANILLA_SPELL_EFFECTIVENESS = [int(row["vanilla_effectiveness"]) for row in spells]
VANILLA_LEVEL_UP_STATS = {int(row["level"]): row["item"] for row in level_up_stats}
VANILLA_PARTY_LEVEL_UPS = group_rows_by_character(party_level_ups)
VANILLA_WEAPON_STATS = group_rows_by_character(weapon_stats)
WEAPON_ITEM_HELP_START = {"Sora": 80, "Donald": 102, "Goofy": 118}
WEAPON_STAT_NAMES = ["STR", "CRR", "CRB", "REC", "MP"]

PARTY_LEVEL_UP_CODES = {
    "None": 0x00,
    "HP": 0x01,
    "MP": 0x02,
    "AP": 0x03,
    "STR": 0x04,
    "DEF": 0x05,
    "Item Slot": 0x06,
    "Accessory Slot": 0x07,
    "Treasure Magnet": 0x85,
    "Second Wind": 0x89,
    "MP Haste": 0x97,
    "MP Rage": 0x98,
    "Second Chance": 0x99,
    "Berserk": 0x9A,
    "Jackpot": 0x9B,
    "Lucky Strike": 0x9C,
    "Charge": 0x9D,
    "Rocket": 0x9E,
    "Tornado": 0x9F,
    "MP Gift": 0xA0,
    "Leaf Bracer": 0xBE,
    "Evolution": 0xBF,
}

CHEST_KEYBLADES = {
    "Destiny Islands": "Oathkeeper",
    "Traverse Town": "Lionheart",
    "Wonderland": "Lady Luck",
    "Olympus Coliseum": "Olympia",
    "Deep Jungle": "Jungle King",
    "Agrabah": "Three Wishes",
    "Monstro": "Wishing Star",
    "Atlantica": "Crabclaw",
    "Halloween Town": "Pumpkinhead",
    "Neverland": "Fairy Harp",
    "Hollow Bastion": "Divine Rose",
    "End of the World": "Oblivion",
    "100 Acre Wood": "Spellbinder",
}

WORLD_KEY_ITEMS = {
    "Footprints": "Wonderland",
    "Entry Pass": "Olympus Coliseum",
    "Slide 1": "Deep Jungle",
    "Crystal Trident": "Atlantica",
    "Forget-Me-Not": "Halloween Town",
    "Jack-In-The-Box": "Halloween Town",
    "Theon Vol. 6": "Hollow Bastion",
}

DOOR_KEY_LOCATIONS = {
    "sephiroth": "Olympus Coliseum Defeat Sephiroth Ansem's Report 12",
    "unknown": "Hollow Bastion Defeat Unknown Ansem's Report 13",
    "final_rest": "End of the World Final Rest Chest",
}
