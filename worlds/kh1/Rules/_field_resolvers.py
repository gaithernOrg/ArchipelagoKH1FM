"""Custom FieldResolvers for Rule args that need more than a direct option attribute read."""

import dataclasses
from typing import TYPE_CHECKING

from typing_extensions import override

from rule_builder.field_resolvers import FieldResolver

if TYPE_CHECKING:
    from .. import KH1World


@dataclasses.dataclass(frozen=True)
class PuppiesRequiredCount(FieldResolver, game="Kingdom Hearts"):
    """Resolves to how many "Puppy" items are needed to cover `puppies_required` actual puppies.

    `FromOption` only does a direct attribute read (e.g. `options.puppy_value.value`); this needs
    the ceil-division Rules.py does (`-(-puppies_required // puppy_value)`), so it gets its own
    resolver instead.
    """

    puppies_required: int

    @override
    def resolve(self, world: "KH1World") -> int:
        puppy_value = world.options.puppy_value.value
        return -(-self.puppies_required // puppy_value)

    @override
    def __str__(self) -> str:
        return f"PuppiesRequiredCount({self.puppies_required})"
