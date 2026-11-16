from math import ceil

from rule_builder.rules import Has, HasAll, HasAllCounts, Or, Rule, True_

from worlds.generic.Rules import add_item_rule
from ..Items import item_name_groups
from ._helpers import COMBO_MASTER, DODGE_ROLL_AND_AIR_GUARD, DUMBO_SUMMON, GLIDE
from ._helpers import HIGH_JUMP, HIGH_JUMP_2, HIGH_JUMP_3
from ._helpers import PARASITE_CAGE, by_difficulty, has_all_magic_lvx_rule


def build_door_rules() -> dict[str, Rule]:
    leon_battled = Has("Traverse Town 1st District Leon Battled")
    guard_armor_defeated = Has("Traverse Town 3rd District Guard Armor Defeated")
    merlin_met = Has("Traverse Town Magician's Study Met Merlin")
    red_trinity_rule = Has("Red Trinity") & guard_armor_defeated
    over_the_crates_rule = Has("Traverse Town 1st District Red Trinity Done") & (GLIDE | HIGH_JUMP_2)
    blue_trinity_balcony_rule = by_difficulty(
        beginner=Has("Blue Trinity") & GLIDE,
        proud=GLIDE,
        minimal=DUMBO_SUMMON,
    )
    item_workshop_from_accessory_shop_rule = by_difficulty(
        beginner=Has("Green Trinity"),
        proud=HIGH_JUMP_2 | (DUMBO_SUMMON & Has("Summon Anywhere"))
    )

    return {
        "Traverse Town 1st District Alleyway (Behind Crates) Entrance": red_trinity_rule,
        "Traverse Town 1st District 1st District (Balcony) Entrance": blue_trinity_balcony_rule,
        "Traverse Town Alleyway Alleyway (Behind Crates) Entrance": over_the_crates_rule,
        "Traverse Town Alleyway Red Room Entrance": leon_battled,
        "Traverse Town Alleyway Green Room Entrance": leon_battled,
        "Traverse Town 1st District Geppetto's House Entrance": PARASITE_CAGE,
        "Traverse Town 3rd District Mystical House Entrance": Has("Progressive Fire"),
        "Traverse Town 3rd District 1st District Entrance": leon_battled,
        "Traverse Town Hallway Green Room Entrance": leon_battled,
        "Traverse Town Hallway Red Room Entrance": leon_battled,
        "Traverse Town 1st District Item Workshop Entrance": Has("Traverse Town Item Workshop Back Door Exited"),
        "Traverse Town Secret Waterway Magician's Study Entrance": merlin_met,
        "Traverse Town 2nd District 2nd District (Rooftops) Entrance": guard_armor_defeated | HIGH_JUMP,
        "Traverse Town 1st District 3rd District Entrance": Has("Traverse Town 3rd District 1st District Door Unlocked"),
        "Traverse Town 1st District World Exit": guard_armor_defeated,
        "Traverse Town 2nd District Gizmo Shop By Ladder Entrance": HIGH_JUMP_2 | GLIDE,
        "Traverse Town 3rd District 3rd District (Balcony) Entrance":HIGH_JUMP_3,
        "Traverse Town Accessory Shop Item Workshop Entrance": item_workshop_from_accessory_shop_rule,
        "Traverse Town Alleyway Secret Waterway Entrance": Has("Red Trinity"),
        "Traverse Town Alleyway (Behind Crates) 1st District Entrance": Has("Traverse Town 1st District Red Trinity Done") & (HIGH_JUMP_2 | GLIDE),
        "Traverse Town Alleyway (Behind Crates) Alleyway Entrance": Has("Traverse Town 1st District Red Trinity Done") & HIGH_JUMP_2,
        "Traverse Town Magician's Lab Magician's Study Entrance": merlin_met,
        "Traverse Town Magician's Study Secret Waterway Entrance": Has("Traverse Town Secret Waterway Leon Conversation"),
    }


def build_room_rules() -> dict[str, Rule]:
    leon_battled = Has("Traverse Town 1st District Leon Battled")
    merlin_met = Has("Traverse Town Magician's Study Met Merlin")

    return {
        "Traverse Town Green Room": leon_battled,
        "Traverse Town Red Room": leon_battled,
        "Traverse Town Magician's Lab": merlin_met,
    }


def build_event_rules() -> dict[str, Rule]:
    leon_battled = Has("Traverse Town 1st District Leon Battled")
    guard_armor_defeated = Has("Traverse Town 3rd District Guard Armor Defeated")
    bell_rung_3x = Has("Traverse Town 2nd District (Rooftops) Bell Rung 3x")

    return {
        "Traverse Town Accessory Shop Met Cid": Has("Traverse Town 2nd District Heartless Scene"),
        "Traverse Town 1st District Leon Battled": Has("Traverse Town Accessory Shop Met Cid"),
        "Traverse Town 3rd District Guard Armor Defeated": leon_battled,
        "Traverse Town 1st District Red Trinity Done": Has("Red Trinity") & guard_armor_defeated,
        "Traverse Town Secret Waterway Leon Conversation": guard_armor_defeated,
        "Traverse Town 3rd District Thunder on Exposed Wires": Has("Progressive Thunder"),
        "Traverse Town 2nd District (Rooftops) Bell Rung 3x": guard_armor_defeated & Has("Red Trinity"),
        "Traverse Town 2nd District Opposite Armor Defeated": bell_rung_3x,
    }


def build_rules(kh1world) -> dict[str, Rule]:
    player = kh1world.player
    puppy_value = kh1world.options.puppy_value.value
    leon_battled = Has("Traverse Town 1st District Leon Battled")
    guard_armor_defeated = Has("Traverse Town 3rd District Guard Armor Defeated")
    bell_rung_3x = Has("Traverse Town 2nd District (Rooftops) Bell Rung 3x")
    opposite_armor_defeated = Has("Traverse Town 2nd District Opposite Armor Defeated")
    exposed_wires_powered = Has("Traverse Town 3rd District Thunder on Exposed Wires")
    synth_items_rule = HasAllCounts({"Orichalcum": 17, "Mythril": 16})

    inner_normal = (
        DUMBO_SUMMON
        | HIGH_JUMP_3
        | (COMBO_MASTER & (DODGE_ROLL_AND_AIR_GUARD | HIGH_JUMP_2 | (HIGH_JUMP & Has("Air Combo Plus", count=2))))
    )
    inner_proud = (
        Has("Mermaid Kick")
        | DODGE_ROLL_AND_AIR_GUARD
        | (COMBO_MASTER & (HIGH_JUMP | Has("Air Combo Plus", count=2)))
    )
    summon_gems_rule = HasAll(*sorted(item_name_groups["Summon Gems"]))
    mystical_house_yellow_trinity_rule = by_difficulty(
        beginner=Has("Yellow Trinity"),
        normal=HIGH_JUMP_2,
        proud=HIGH_JUMP | DUMBO_SUMMON,
    )
    mystical_house_glide_rule = by_difficulty(
        beginner=GLIDE,
        proud=inner_normal,
        minimal=inner_proud,
    )
    all_arts_rule = HasAll(*sorted(item_name_groups["Arts"]))
    synth_15_items_rule = Or(
        HasAllCounts({"Orichalcum": 6, "Mythril": 9}),
        HasAllCounts({"Orichalcum": 7, "Mythril": 8}),
        HasAllCounts({"Orichalcum": 8, "Mythril": 7}),
        HasAllCounts({"Orichalcum": 9, "Mythril": 6}),
    )

    for i in range(33):
        add_item_rule(
            kh1world.get_location(f"Traverse Town Synth Item {i + 1:02}"),
            lambda item, _player=player: (item.player != _player or item.name not in ("Orichalcum", "Mythril")),
        )

    return {
        "Traverse Town 1st District Aerith Gift": leon_battled | guard_armor_defeated,
        "Traverse Town 1st District Speak with Cid Event": guard_armor_defeated,
        "Traverse Town 1st District Safe Postcard": leon_battled,
        "Traverse Town 1st District Candle Puzzle Chest": Has("Progressive Blizzard"),
        "Traverse Town 1st District Accessory Shop Roof Chest": HIGH_JUMP,
        "Traverse Town Secret Waterway White Trinity Chest": Has("White Trinity"),
        "Traverse Town Secret Waterway Near Stairs Chest": guard_armor_defeated,
        "Traverse Town Leon Secret Waterway Earthshine Event": guard_armor_defeated,
        "Traverse Town Geppetto's House Chest": PARASITE_CAGE,
        "Traverse Town Defeat Opposite Armor Aero Event": bell_rung_3x,
        "Traverse Town Defeat Opposite Armor Navi-G Piece Event": bell_rung_3x,
        "Traverse Town Magician's Study Obtained All LV1 Magic": has_all_magic_lvx_rule(1),
        "Traverse Town Magician's Study Obtained All LV3 Magic": has_all_magic_lvx_rule(3),
        "Traverse Town Gizmo Shop Postcard 1": exposed_wires_powered,
        "Traverse Town Gizmo Shop Postcard 2": exposed_wires_powered,
        "Traverse Town Geppetto's House Postcard": PARASITE_CAGE,
        "Traverse Town 1st District Blue Trinity by Exit Door": Has("Blue Trinity"),
        "Traverse Town 3rd District Blue Trinity": Has("Blue Trinity"),
        "Traverse Town Magician's Study Blue Trinity": Has("Blue Trinity"),
        "Traverse Town Magician's Study Earthshine Event": Has("Earthshine"),
        "Traverse Town Magician's Study Naturespark Event": Has("Naturespark"),
        "Traverse Town Magician's Study Watergleam Event": Has("Watergleam"),
        "Traverse Town Magician's Study Fireglow Event": Has("Fireglow"),
        "Traverse Town Magician's Study Lord Fortune Event": summon_gems_rule,
        "Traverse Town Mystical House Yellow Trinity Chest": mystical_house_yellow_trinity_rule,
        "Traverse Town Mystical House Glide Chest": mystical_house_glide_rule,
        "Traverse Town Kairi Secret Waterway Oathkeeper Event": guard_armor_defeated,
        "Traverse Town Secret Waterway Navi Gummi Event": guard_armor_defeated,
        "Traverse Town Geppetto's House Geppetto Reward Hyperion Blueprint": summon_gems_rule,
        "Traverse Town Magician's Study Obtained All Arts Items": all_arts_rule,
        "Traverse Town Synth 15 Items": synth_15_items_rule,
        "Traverse Town Piano Room Return 10 Puppies": Has("Puppy", count=ceil(10 / puppy_value)),
        "Traverse Town Piano Room Return 20 Puppies": Has("Puppy", count=ceil(20 / puppy_value)),
        "Traverse Town Piano Room Return 30 Puppies": Has("Puppy", count=ceil(30 / puppy_value)),
        "Traverse Town Piano Room Return 40 Puppies": Has("Puppy", count=ceil(40 / puppy_value)),
        "Traverse Town Piano Room Return 50 Puppies Reward 1": Has("Puppy", count=ceil(50 / puppy_value)),
        "Traverse Town Piano Room Return 50 Puppies Reward 2": Has("Puppy", count=ceil(50 / puppy_value)),
        "Traverse Town Piano Room Return 60 Puppies": Has("Puppy", count=ceil(60 / puppy_value)),
        "Traverse Town Piano Room Return 70 Puppies": Has("Puppy", count=ceil(70 / puppy_value)),
        "Traverse Town Piano Room Return 80 Puppies": Has("Puppy", count=ceil(80 / puppy_value)),
        "Traverse Town Piano Room Return 90 Puppies": Has("Puppy", count=ceil(90 / puppy_value)),
        "Traverse Town Piano Room Return 99 Puppies Reward 1": Has("Puppy", count=ceil(99 / puppy_value)),
        "Traverse Town Piano Room Return 99 Puppies Reward 2": Has("Puppy", count=ceil(99 / puppy_value)),
        "Traverse Town Mail Postcard 01 Event": Has("Postcard", count=1),
        "Traverse Town Mail Postcard 02 Event": Has("Postcard", count=2),
        "Traverse Town Mail Postcard 03 Event": Has("Postcard", count=3),
        "Traverse Town Mail Postcard 04 Event": Has("Postcard", count=4),
        "Traverse Town Mail Postcard 05 Event": Has("Postcard", count=5),
        "Traverse Town Mail Postcard 06 Event": Has("Postcard", count=6),
        "Traverse Town Mail Postcard 07 Event": Has("Postcard", count=7),
        "Traverse Town Mail Postcard 08 Event": Has("Postcard", count=8),
        "Traverse Town Mail Postcard 09 Event": Has("Postcard", count=9),
        "Traverse Town Mail Postcard 10 Event": Has("Postcard", count=10),
        "Traverse Town Synth Item 01": synth_items_rule,
        "Traverse Town Synth Item 02": synth_items_rule,
        "Traverse Town Synth Item 03": synth_items_rule,
        "Traverse Town Synth Item 04": synth_items_rule,
        "Traverse Town Synth Item 05": synth_items_rule,
        "Traverse Town Synth Item 06": synth_items_rule,
        "Traverse Town Synth Item 07": synth_items_rule,
        "Traverse Town Synth Item 08": synth_items_rule,
        "Traverse Town Synth Item 09": synth_items_rule,
        "Traverse Town Synth Item 10": synth_items_rule,
        "Traverse Town Synth Item 11": synth_items_rule,
        "Traverse Town Synth Item 12": synth_items_rule,
        "Traverse Town Synth Item 13": synth_items_rule,
        "Traverse Town Synth Item 14": synth_items_rule,
        "Traverse Town Synth Item 15": synth_items_rule,
        "Traverse Town Synth Item 16": synth_items_rule,
        "Traverse Town Synth Item 17": synth_items_rule,
        "Traverse Town Synth Item 18": synth_items_rule,
        "Traverse Town Synth Item 19": synth_items_rule,
        "Traverse Town Synth Item 20": synth_items_rule,
        "Traverse Town Synth Item 21": synth_items_rule,
        "Traverse Town Synth Item 22": synth_items_rule,
        "Traverse Town Synth Item 23": synth_items_rule,
        "Traverse Town Synth Item 24": synth_items_rule,
        "Traverse Town Synth Item 25": synth_items_rule,
        "Traverse Town Synth Item 26": synth_items_rule,
        "Traverse Town Synth Item 27": synth_items_rule,
        "Traverse Town Synth Item 28": synth_items_rule,
        "Traverse Town Synth Item 29": synth_items_rule,
        "Traverse Town Synth Item 30": synth_items_rule,
        "Traverse Town Synth Item 31": synth_items_rule,
        "Traverse Town Synth Item 32": synth_items_rule,
        "Traverse Town Synth Item 33": synth_items_rule,
        "Traverse Town Red Room White Mushroom Fire x3 Reward": opposite_armor_defeated & Has("Progressive Fire"),
        "Traverse Town 2nd District Sniperwild 30th Defeated Reward": opposite_armor_defeated,
        "Traverse Town Defeat Guard Armor 500 Munny Reward": guard_armor_defeated,
        "Traverse Town Defeat Guard Armor Dodge Roll Event": guard_armor_defeated,
        "Traverse Town Defeat Guard Armor Fire Event": guard_armor_defeated,
        "Traverse Town Defeat Guard Armor Blue Trinity Event": guard_armor_defeated,
        "Traverse Town Defeat Guard Armor Brave Warrior Event": guard_armor_defeated,
        "Traverse Town 1st District Leon Gift": guard_armor_defeated,
    }
