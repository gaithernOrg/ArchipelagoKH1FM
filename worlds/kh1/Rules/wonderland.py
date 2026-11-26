from rule_builder.rules import Has, Rule

from ._helpers import DUMBO_SKIP, GLIDE, HIGH_JUMP, HIGH_JUMP_2
from ._helpers import HIGH_JUMP_3, HIGH_JUMP_AND_GLIDE, HIGH_JUMP_OR_GLIDE, X_WORLDS_3
from ._helpers import X_WORLDS_6, by_difficulty, can_early_tea_rule, has_key_item_rule


def build_door_rules() -> dict[str, Rule]:
    early_tea = can_early_tea_rule()
    pot_filled = Has("Wonderland Bizarre Room (Sideways Chimney) Pot Filled")
    clock_moved = Has("Wonderland Bizarre Room (Large) Move Clock")
    top_of_pot = pot_filled & (HIGH_JUMP | Has("Progressive Glide", count=2))
    stump_stomped = Has("Wonderland Lotus Forest (Large) Stump Stomped")
    can_rotate_tree = Has("Wonderland Lotus Forest (Large) Can Rotate Tree")
    boulder_moved = Has("Wonderland Lotus Forest (Large) Boulder Moved")
    tea_party_garden_above_lotus = by_difficulty(
        beginner=GLIDE | early_tea,
        normal=HIGH_JUMP_2 & stump_stomped,
        proud=(HIGH_JUMP | DUMBO_SKIP) & stump_stomped,
    )
    lotus_forest_corner_chest_rule = by_difficulty(
        beginner=HIGH_JUMP_AND_GLIDE,
        normal=HIGH_JUMP_OR_GLIDE,
        proud=True,
    )
    alice_trial = Has("Wonderland Queen's Castle Alice's Trial")

    return {
        "Wonderland Bizarre Room (Faucet) Bizarre Room (On Stove) Entrance": by_difficulty(proud=True),
        "Wonderland Bizarre Room (Faucet) Bizarre Room (Shelf) Entrance": GLIDE,
        "Wonderland Bizarre Room (Sideways Chimney) Queen's Castle (Right Hedge) Entrance": pot_filled,
        "Wonderland Bizarre Room (Sideways Painting) Tea Party Garden (Awning) Entrance": clock_moved,
        "Wonderland Bizarre Room (Small) Bizarre Room (On Stove) Entrance": HIGH_JUMP_OR_GLIDE,
        "Wonderland Bizarre Room (Small) Queen's Castle (Right Hedge) Entrance": top_of_pot,
        "Wonderland Bizarre Room (Small) Tea Party Garden (Awning) Entrance": clock_moved,
        "Wonderland Lotus Forest (Alcove) Lotus Forest Entrance": stump_stomped,
        "Wonderland Lotus Forest Bizarre Room (Sideways Chimney) Entrance": can_rotate_tree,
        "Wonderland Lotus Forest Lotus Forest (Above Tea Party Garden Ground Entrance) Entrance": can_rotate_tree,
        "Wonderland Lotus Forest Lotus Forest (Alcove) Entrance": boulder_moved,
        "Wonderland Lotus Forest Lotus Forest (By Upper Tea Party Garden Entrance) Entrance": tea_party_garden_above_lotus,
        "Wonderland Lotus Forest Lotus Forest (Faucet Corner) Entrance": stump_stomped | GLIDE,
        "Wonderland Lotus Forest Lotus Forest (Corner by Lower Tea Party Garden Entrance) Entrance": lotus_forest_corner_chest_rule,
        "Wonderland Lotus Forest Tea Party Garden Entrance": alice_trial,
        "Wonderland Queen's Castle Queen's Castle (Left Hedge) Entrance": by_difficulty(beginner=HIGH_JUMP, normal=GLIDE),
        "Wonderland Queen's Castle Queen's Castle (Right Hedge) Entrance": by_difficulty(beginner=HIGH_JUMP, normal=GLIDE),
        "Wonderland Tea Party Garden (Above Lotus Forest) Tea Party Garden (Side Hedge) Entrance": by_difficulty(beginner=GLIDE, normal=HIGH_JUMP_3),
        "Wonderland Tea Party Garden (Side Hedge) Tea Party Garden (Awning) Entrance": GLIDE,
        "Wonderland Tea Party Garden Bizarre Room (Upside Down) Entrance": alice_trial,
        "Wonderland Tea Party Garden Tea Party Garden (Above Lotus Forest) Entrance": HIGH_JUMP_3,
        "Wonderland Tea Party Garden Tea Party Garden (Side Hedge) Entrance": HIGH_JUMP_3,
        "Wonderland Tea Party Garden Tea Party Garden (Awning) Entrance": HIGH_JUMP_3,
    }


def build_room_rules() -> dict[str, Rule]:
    talked_to_doorknob = Has("Wonderland Bizarre Room (Large) Talked to Doorknob")

    return {
        "Wonderland Bizarre Room (Small)": talked_to_doorknob,
        "Wonderland Bizarre Room (Faucet)": talked_to_doorknob,
        "Wonderland Bizarre Room (Shelf)": talked_to_doorknob,
        "Wonderland Bizarre Room (On Stove)": talked_to_doorknob,
        "Wonderland Queen's Castle": talked_to_doorknob,
        "Wonderland Queen's Castle (Left Hedge)": talked_to_doorknob,
        "Wonderland Queen's Castle (Right Hedge)": talked_to_doorknob,
    }


def build_event_rules() -> dict[str, Rule]:
    lamps_lit = Has("Wonderland Bizarre Room (Upside Down) Lamps Lit")
    bear_dropped = Has("Wonderland Bizarre Room (Sideways Painting) Bear Dropped")
    alice_trial = Has("Wonderland Queen's Castle Alice's Trial")
    met_cheshire = Has("Wonderland Lotus Forest Met Cheshire Cat")
    footprints = has_key_item_rule("Footprints")

    return {
        "Wonderland Bizarre Room (Upside Down) Lamps Lit": alice_trial,
        "Wonderland Bizarre Room (Small) Trickmaster Defeated": lamps_lit,
        "Wonderland Lotus Forest (Large) Boulder Moved": alice_trial,
        "Wonderland Queen's Castle Alice's Trial": met_cheshire & footprints,
        "Wonderland Bizarre Room (Large) Move Clock": bear_dropped,
        "Wonderland Bizarre Room (Large) Move Bear": bear_dropped,
    }


def build_rules() -> dict[str, Rule]:
    lamps_lit = Has("Wonderland Bizarre Room (Upside Down) Lamps Lit")
    bear_dropped = Has("Wonderland Bizarre Room (Sideways Painting) Bear Dropped")
    boulder_moved = Has("Wonderland Lotus Forest (Large) Boulder Moved")
    trickmaster_defeated = Has("Wonderland Bizarre Room (Small) Trickmaster Defeated")

    rabbit_hole_defeat_heartless_3_chest_rule = by_difficulty(
        beginner=X_WORLDS_6,
        proud=X_WORLDS_3,
        minimal=True,
    )

    return {
        "Wonderland Rabbit Hole Green Trinity Chest": Has("Green Trinity"),
        "Wonderland Bizarre Room Green Trinity Chest": Has("Green Trinity"),
        "Wonderland Lotus Forest Thunder Plant Chest": Has("Progressive Thunder"),
        "Wonderland Lotus Forest Through the Painting Thunder Plant Chest": Has("Progressive Thunder"),
        "Wonderland Lotus Forest Through the Painting White Trinity Chest": Has("White Trinity"),
        "Wonderland Defeat Trickmaster Blizzard Event": trickmaster_defeated,
        "Wonderland Defeat Trickmaster Ifrit's Horn Event": trickmaster_defeated,
        "Wonderland Bizarre Room Read Book": bear_dropped,
        "Wonderland Bizarre Room Navi-G Piece Event": trickmaster_defeated,
        "Wonderland Lotus Forest Blue Trinity in Alcove": Has("Blue Trinity"),
        "Wonderland Lotus Forest Blue Trinity by Moving Boulder": Has("Blue Trinity") & boulder_moved,
        "Wonderland Bizarre Room Examine Flower Pot": lamps_lit,
        "Wonderland Rabbit Hole Defeat Heartless 3 Chest": rabbit_hole_defeat_heartless_3_chest_rule,
        "Wonderland Lotus Forest White Mushroom Blizzard x3 Reward": trickmaster_defeated & Has("Progressive Blizzard"),
        "Wonderland Bizarre Room Gigas Shadow 7th Defeated Reward": trickmaster_defeated,
    }
