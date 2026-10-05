"""Custom Rule Builder rules for things the built-in primitives can't express."""

import dataclasses
from collections.abc import Mapping
from typing import TYPE_CHECKING

from typing_extensions import override

from BaseClasses import CollectionState
from rule_builder.rules import Rule

if TYPE_CHECKING:
    from .. import KH1World


@dataclasses.dataclass()
class HasCappedSum(Rule["KH1World"], game="Kingdom Hearts"):
    """Checks if the sum of per-item counts (each capped at a max) reaches a threshold.

    No built-in Rule expresses this: HasAllCounts/HasAnyCount apply each item's threshold
    independently (AND/OR), and HasFromList sums counts across items but without a per-item cap,
    so e.g. 20 of a single item would satisfy it - which isn't what Rules.py's
    `min(state.count(...), 9) + min(state.count(...), 9) >= 15` (Synth 15 Items) means.
    """

    item_caps: Mapping[str, int]
    threshold: int

    @override
    def _instantiate(self, world: "KH1World") -> Rule.Resolved:
        return self.Resolved(
            tuple(self.item_caps.items()),
            self.threshold,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    class Resolved(Rule.Resolved):
        item_caps: tuple[tuple[str, int], ...]
        threshold: int

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            player_prog_items = state.prog_items[self.player]
            total = sum(min(player_prog_items[item], cap) for item, cap in self.item_caps)
            return total >= self.threshold

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            return {item: {id(self)} for item, _ in self.item_caps}

        @override
        def __str__(self) -> str:
            items = ", ".join(f"{item} (max {cap})" for item, cap in self.item_caps)
            return f"Has {self.threshold} from capped sum of ({items})"
