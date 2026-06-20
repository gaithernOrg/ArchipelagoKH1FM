"""
KH1's access rules, built with Rule Builder. Originally a from-scratch Rule Builder port written
side-by-side with the old hand-written Rules.py (a `state.has(...)`/`add_rule(...)` style module),
verified equivalent to it across a representative matrix of player options and item states, then
wired in to replace it once that equivalence was proven by tests. Rules.py no longer exists in this
repo; the "Translation notes" below are kept as historical context for why some rules look the way
they do (preserved quirks, past crash-bug fixes) even though there's nothing left to diff against.

Layout: each KH1 world area gets its own module (traverse_town.py, wonderland.py, ...) exposing a
`build_rules(ctx, ...)` function that returns a `dict[str, Rule]` for that area's locations.
`build_rule_dicts()` below builds the shared `RuleContext` (see `_context.py`), calls each area
module, and merges everything plus the handful of rules that don't belong to one area (level
checks, Final Ansem, accessories, the generic "behind boss"/"keyblade-locked chest" pass over every
location, entrances). `set_rules2()` is a thin wrapper that applies the result via `world.set_rule`
and sets the completion condition.

Every rule this package builds is option-generic: branches on difficulty/toggles/choices are
expressed as `OptionFilter`s (see `_option_filters.py`) and option-derived counts as `FromOption`/
custom `FieldResolver`s (see `_field_resolvers.py`) rather than as Python `if`s over an
already-resolved value. That means the *unresolved* `Rule` trees `build_rule_dicts()` returns -
notably via `export_rules_to_dict()` in `_export.py` - are valid regardless of what options the
world that happened to build them had; only `.resolve(world)` (called by `world.set_rule`, or by a
JSON consumer re-checking the OptionFilters/FieldResolvers) is where a specific world's options
actually get read. The one thing that can't be made generic this way is which locations/entrances
*exist* at all (`super_bosses`/`cups`/`hundred_acre_wood`/`atlantica`/`destiny_islands`/
`jungle_slider`/`final_rest_door_key` per Regions.py) - that's decided by plain Python conditions,
same as today, since it's a Locations/Regions concept Rule Builder doesn't model.

Translation notes / known quirks intentionally preserved from the original Rules.py (do not "fix"
these without confirming with the user which behavior is actually wanted - they may be deliberate):

  * "Traverse Town 1st District Accessory Shop Roof Chest" - the original has
    `add_rule(loc, lambda state: ...) or difficulty > LOGIC_BEGINNER` - the `or` is OUTSIDE the
    add_rule() call and so is dead code (it operates on add_rule's return value, not the rule).
    The actual rule is just `Has("High Jump")`, ungated by difficulty. Replicated as-is here.
  * has_oogie_manor / "Traverse Town Mystical House Yellow Trinity Chest" - `and` binds tighter
    than `or` in Python, so a couple of sub-clauses that look indented under a
    `difficulty > LOGIC_X and (...)` guard are actually NOT gated by that guard. Replicated as-is
    (see comments in _helpers.py and traverse_town.py).
  * "Halloween Town Oogie's Manor Upper Iron Cage Chest" and "Hollow Bastion Rising Falls Floating
    Platform Near Bubble Chest" used to have actual crash bugs in Rules.py (missing `player`
    arguments to `state.has_all(...)` / `state.has(...)`, raising TypeError/KeyError when that
    branch was reached - this equivalence test suite is what caught them). Both were fixed directly
    in Rules.py; this package already had the intended behavior.
  * `magic_costs` / dynamic per-seed `spell_costs` are intentionally NOT ported: every call site in
    Rules.py that would use them is commented out in favor of `has_offensive_magic`, so they are
    dead code as of this writing.
  * `has_basic_tools` calls `has_offensive_magic(state, player, LOGIC_BEGINNER)` - i.e. it always
    passes the *constant* LOGIC_BEGINNER, not the world's configured difficulty. Replicated as-is
    (see _helpers.py's has_basic_tools_rule).
  * "Traverse Town Magician's Study Obtained All Arts Items" similarly pins its has_x_worlds check
    to LOGIC_BEGINNER regardless of configured difficulty (softlock prevention) - see
    has_x_worlds_rule_pinned_to_beginner in _helpers.py.
  * "Traverse Town Synth 15 Items" uses a min-capped sum (`HasCappedSum`, see _custom_rules.py) -
    no built-in Rule expresses that.
  * `add_item_rule` (item placement rules, as opposed to access rules) has no Rule Builder
    equivalent, so those calls are left untouched, using the original `worlds.generic.Rules` helper.
    The per-location item_rule on each "Traverse Town Synth Item NN" location (forbidding
    Orichalcum/Mythril from being placed there, see traverse_town.py) was initially missed in this
    port - the original equivalence tests only ever compared access_rule, never item_rule, so this
    went undetected until the test suite was extended to check item_rule too.
"""

from rule_builder.field_resolvers import FromOption
from rule_builder.rules import Has, Or, Rule, True_

from worlds.generic.Rules import add_item_rule
from ..Locations import location_table
from ..Items import item_table
from ..Options import HomecomingMaterials
from . import (
    agrabah,
    atlantica,
    deep_jungle,
    destiny_islands,
    end_of_the_world,
    halloween_town,
    hollow_bastion,
    hundred_acre_wood,
    monstro,
    neverland,
    olympus_coliseum,
    traverse_town,
    wonderland,
)
from ._constants import KEYBLADES, WORLDS
from ._context import build_context
from ._custom_rules import HasCappedSum
from ._helpers import has_final_rest_door_rule, has_lucky_emblems_rule, has_x_worlds_rule
from ._option_filters import (
    EOTW_UNLOCK_LUCKY_EMBLEMS,
    EXACTLY_BEGINNER,
    KEYBLADES_UNLOCK_CHESTS_OFF,
    KEYBLADES_UNLOCK_CHESTS_ON,
    NOT_EXACTLY_BEGINNER,
)

__all__ = ["set_rules", "build_rule_dicts", "export_rules_to_dict", "HasCappedSum"]


def build_rule_dicts(kh1world) -> tuple[dict[str, Rule], dict[str, Rule]]:
    """Builds KH1's (unresolved) access rules. Doesn't touch the world - callers either
    resolve+apply them (set_rules) or export them (_export.py)."""
    player = kh1world.player
    options = kh1world.options

    ctx = build_context()

    location_rules: dict[str, Rule] = {}
    location_rules.update(traverse_town.build_rules(ctx, kh1world))
    location_rules.update(wonderland.build_rules(ctx))
    location_rules.update(deep_jungle.build_rules(ctx, bool(options.jungle_slider)))
    location_rules.update(agrabah.build_rules(ctx, bool(options.super_bosses)))
    location_rules.update(monstro.build_rules(ctx))
    location_rules.update(halloween_town.build_rules(ctx))
    location_rules.update(olympus_coliseum.build_rules(
        ctx, options.cups.current_key, bool(options.super_bosses), options.final_rest_door_key.current_key,
    ))
    location_rules.update(neverland.build_rules(ctx, bool(options.super_bosses)))
    location_rules.update(hollow_bastion.build_rules(
        ctx, bool(options.super_bosses), options.final_rest_door_key.current_key,
    ))
    location_rules.update(end_of_the_world.build_rules(ctx))
    location_rules.update(hundred_acre_wood.build_rules(ctx, bool(options.hundred_acre_wood)))
    location_rules.update(atlantica.build_rules(ctx, bool(options.atlantica)))
    location_rules.update(destiny_islands.build_rules(ctx, bool(options.destiny_islands)))

    # ---- rules that don't belong to one area ----
    for i in range(1, options.level_checks + 1):
        level_world_rule = has_x_worlds_rule(min(((i // 10) * 2), 8))
        location_rules[f"Level {i + 1:03} (Slot 1)"] = level_world_rule
        if i + 1 in kh1world.get_slot_2_levels():
            location_rules[f"Level {i + 1:03} (Slot 2)"] = level_world_rule

    eotw_access = Or(has_lucky_emblems_rule() & EOTW_UNLOCK_LUCKY_EMBLEMS, Has("End of the World"))
    location_rules["Final Ansem"] = (
        ctx.x_worlds_8
        & (
            (Has("Destiny Islands") & Has("Raft Materials", count=FromOption(HomecomingMaterials)))
            | (eotw_access & has_final_rest_door_rule())
        )
        & ctx.defensive_tools
    )

    for accessory in kh1world.get_accessory_locations():
        location_rules[accessory] = Has(accessory.replace("Accessory ", ""))

    for location_name, location_data in location_table.items():
        try:
            kh1world.get_location(location_name)
        except KeyError:
            continue
        if location_data.behind_boss:
            location_rules[location_name] = location_rules.get(location_name, True_()) & Or(
                ctx.basic_tools & EXACTLY_BEGINNER,
                True_() & NOT_EXACTLY_BEGINNER,
            )
        if options.remote_items.current_key == "off" and location_data.type == "Synth":
            add_item_rule(kh1world.get_location(location_name),
                          lambda i: (i.player != player or item_table[i.name].type == "Item"))
        if location_data.type == "Chest":
            location_world = location_data.category
            location_required_keyblade = KEYBLADES[WORLDS.index(location_world)]
            location_rules[location_name] = location_rules.get(location_name, True_()) & Or(
                Has(location_required_keyblade) & KEYBLADES_UNLOCK_CHESTS_ON,
                True_() & KEYBLADES_UNLOCK_CHESTS_OFF,
            )

    entrance_rules: dict[str, Rule] = {}
    if options.destiny_islands:
        entrance_rules["Destiny Islands"] = Has("Destiny Islands")
    entrance_rules["Wonderland"] = Has("Wonderland") & ctx.x_worlds_3
    entrance_rules["Olympus Coliseum"] = Has("Olympus Coliseum") & ctx.x_worlds_3
    entrance_rules["Deep Jungle"] = Has("Deep Jungle") & ctx.x_worlds_3
    entrance_rules["Agrabah"] = Has("Agrabah") & ctx.x_worlds_3
    entrance_rules["Monstro"] = Has("Monstro") & ctx.x_worlds_3
    if options.atlantica:
        entrance_rules["Atlantica"] = Has("Atlantica") & ctx.x_worlds_3
    entrance_rules["Halloween Town"] = Has("Halloween Town") & ctx.x_worlds_3
    entrance_rules["Neverland"] = Has("Neverland") & ctx.x_worlds_4
    entrance_rules["Hollow Bastion"] = Has("Hollow Bastion") & ctx.x_worlds_6
    entrance_rules["End of the World"] = ctx.x_worlds_8 & eotw_access
    entrance_rules["100 Acre Wood"] = Has("Progressive Fire")

    return location_rules, entrance_rules


def set_rules(kh1world) -> None:
    """Builds and applies KH1's access rules to kh1world. Called by KH1World.set_rules()."""
    location_rules, entrance_rules = build_rule_dicts(kh1world)

    for name, rule in entrance_rules.items():
        kh1world.set_rule(kh1world.get_entrance(name), rule)
    for name, rule in location_rules.items():
        kh1world.set_rule(kh1world.get_location(name), rule)

    kh1world.multiworld.completion_condition[kh1world.player] = lambda state: state.has("Victory", kh1world.player)


# Imported last - _export.py imports build_rule_dicts from this module, so this must come after
# build_rule_dicts is defined above to avoid a circular-import error on partial initialization.
from ._export import export_rules_to_dict  # noqa: E402
