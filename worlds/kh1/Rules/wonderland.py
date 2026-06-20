"""Access rules for every "Wonderland"-prefixed location."""

from rule_builder.rules import Has, HasAll, HasAllCounts, Or, Rule, True_

from ._option_filters import ABOVE_BEGINNER, ABOVE_NORMAL, ABOVE_PROUD
from ._context import RuleContext
from ._helpers import can_early_tea_rule, has_key_item_rule


def build_rules(ctx: RuleContext) -> dict[str, Rule]:
    footprints = has_key_item_rule("Footprints")
    early_tea = can_early_tea_rule()

    queens_castle_hedge = Or(
        footprints,
        ctx.hj1,
        ctx.glide & ABOVE_BEGINNER,
        ctx.dumbo_summon & ABOVE_NORMAL,
    )
    tea_party_garden_above_lotus = Or(
        ctx.glide,
        (ctx.hj2 & footprints) & ABOVE_BEGINNER,
        ((ctx.hj1 | ctx.dumbo_skip) & footprints) & ABOVE_NORMAL,
        early_tea,
    )
    tea_party_garden_chair = footprints | ctx.glide | early_tea

    return {
        "Wonderland Rabbit Hole Green Trinity Chest": Has("Green Trinity"),
        "Wonderland Bizarre Room Green Trinity Chest": Has("Green Trinity"),
        "Wonderland Lotus Forest Thunder Plant Chest": Has("Progressive Thunder") & footprints,
        "Wonderland Lotus Forest Through the Painting Thunder Plant Chest": Has("Progressive Thunder") & footprints,
        "Wonderland Lotus Forest Through the Painting White Trinity Chest": Has("White Trinity") & footprints,
        "Wonderland Bizarre Room Lamp Chest": footprints,
        "Wonderland Defeat Trickmaster Blizzard Event": footprints,
        "Wonderland Defeat Trickmaster Ifrit's Horn Event": footprints,
        "Wonderland Bizarre Room Read Book": footprints,
        "Wonderland Bizarre Room Navi-G Piece Event": footprints,
        "Wonderland Lotus Forest Blue Trinity in Alcove": Has("Blue Trinity"),
        "Wonderland Lotus Forest Blue Trinity by Moving Boulder": Has("Blue Trinity") & footprints,
        "Wonderland Bizarre Room Examine Flower Pot": footprints,
        "Wonderland Lotus Forest Yellow Elixir Flower Through Painting": footprints,
        "Wonderland Lotus Forest Red Flower Raise Lily Pads": footprints,

        "Wonderland Rabbit Hole Defeat Heartless 3 Chest": Or(
            ctx.x_worlds_6,
            ctx.x_worlds_3 & ABOVE_NORMAL,
            True_() & ABOVE_PROUD,
        ),
        "Wonderland Queen's Castle Hedge Left Red Chest": queens_castle_hedge,
        "Wonderland Queen's Castle Hedge Right Blue Chest": queens_castle_hedge,
        "Wonderland Queen's Castle Hedge Right Red Chest": queens_castle_hedge,
        "Wonderland Lotus Forest Glide Chest": Or(
            ctx.glide,
            ((ctx.hj1 | ctx.dumbo_skip) & footprints) & ABOVE_NORMAL,
            early_tea,
        ),
        "Wonderland Lotus Forest Corner Chest": Or(
            ctx.hj_glide_all,
            ctx.hj_glide_any & ABOVE_BEGINNER,
            True_() & ABOVE_NORMAL,
        ),
        "Wonderland Tea Party Garden Above Lotus Forest Entrance 2nd Chest": tea_party_garden_above_lotus,
        "Wonderland Tea Party Garden Above Lotus Forest Entrance 1st Chest": tea_party_garden_above_lotus,
        "Wonderland Tea Party Garden Bear and Clock Puzzle Chest": Or(
            footprints,
            ctx.glide,
            HasAllCounts({"Combo Master": 1, "High Jump": 3, "Air Combo Plus": 2}) & ABOVE_PROUD,
        ),
        "Wonderland Tea Party Garden Across From Bizarre Room Entrance Chest": Or(
            ctx.glide,
            (ctx.hj3 & footprints) & ABOVE_BEGINNER,
            (((HasAll("High Jump", "Combo Master") & footprints) | (ctx.hj2 & footprints))) & ABOVE_NORMAL,
            early_tea,
        ),
        "Wonderland Tea Party Garden Left Cushioned Chair": tea_party_garden_chair,
        "Wonderland Tea Party Garden Left Pink Chair": tea_party_garden_chair,
        "Wonderland Tea Party Garden Right Yellow Chair": tea_party_garden_chair,
        "Wonderland Tea Party Garden Left Gray Chair": tea_party_garden_chair,
        "Wonderland Tea Party Garden Right Brown Chair": tea_party_garden_chair,
    }
