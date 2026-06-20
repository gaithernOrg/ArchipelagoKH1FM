"""Exports the Rules package's unresolved rule trees as JSON-compatible dicts.

Because every rule this package builds is option-generic (see the package docstring in
__init__.py), the exported `args`/`options`/`resolver` data is valid regardless of what options the
`kh1world` passed in here happened to have - that world is only consulted to decide which
locations/entrances *exist* (a Locations/Regions concept Rule Builder can't express), not to
resolve any rule logic. Pass a `kh1world` built with every togglable area on (super_bosses, a cups
tier, hundred_acre_wood, atlantica, destiny_islands, jungle_slider) to get the maximal location set.
"""

from typing import Any

from . import build_rule_dicts


def export_rules_to_dict(kh1world) -> dict[str, Any]:
    location_rules, entrance_rules = build_rule_dicts(kh1world)
    return {
        "locations": {name: rule.to_dict() for name, rule in location_rules.items()},
        "entrances": {name: rule.to_dict() for name, rule in entrance_rules.items()},
    }
