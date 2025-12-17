#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, override


class Decomposable(Protocol):
    def decompose(self) -> dict[Raw, float]: ...


@dataclass(frozen=True)
class Chemical:
    name: str
    cas: str


@dataclass(frozen=True)
class Raw:
    chemical: Chemical
    percent: float

    def decompose(self) -> dict[Raw, float]:
        return {self: 1.0}


@dataclass(frozen=True, eq=False)
class Compound:
    ingredients: dict[Ingredient, float]

    @override
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.ingredients.items(), key=lambda x: hash(x[0]))))

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Compound):
            return NotImplemented
        return self.ingredients == other.ingredients

    def decompose(self) -> dict[Raw, float]:
        result: dict[Raw, float] = {}
        for ingredient, amount in self.ingredients.items():
            for raw, raw_amount in ingredient.decompose().items():
                result[raw] = result.get(raw, 0.0) + raw_amount * amount
        total = sum(result.values())
        return {raw: amount / total for raw, amount in result.items()}

Ingredient = Compound | Raw


def industrial(decomposition: dict[Raw, float]) -> tuple[dict[Chemical, float], float]:
    chemicals: dict[Chemical, float] = {}
    solvent = 0.0
    for raw, amount in decomposition.items():
        chemical_fraction = raw.percent / 100.0
        chemicals[raw.chemical] = chemicals.get(raw.chemical, 0.0) + amount * chemical_fraction
        solvent += amount * (1.0 - chemical_fraction)
    return chemicals, solvent


black_pepper = Raw(Chemical("black pepper", "8006-82-4"), 1.04)

aag = Raw(Chemical("allyl amyl glyconate", "67634-00-8"), 1.04)

rose = Raw(Chemical("rose absolute", "8007-01-0"), 2.09)

frankincense = Raw(Chemical("frankincense", "8016-36-2"), 0.78)

coumarin = Raw(Chemical("coumarin", "91-64-5"), 2.42)

e1_2025_11_30 = Compound({
        black_pepper: 200,
        aag: 100,
        rose: 200,
        frankincense: 100,
        coumarin: 300
    })

immortelle = Raw(Chemical("immortelle", "8023-95-8"), 0.37)

musk = Raw(Chemical("musk ketone", "81-14-1"), 6.13)

e2_2025_11_30 = Compound({
        e1_2025_11_30 : 400,
        immortelle: 80,
        musk: 80
    })


# TODO: Try above with lower musk percentage.
# Musk seems to be less volatile and so the smell becomes overly musky after a while.
# TODO: Try more BP
# TODO: Try Habanolide instead of Musk for safety concerns.

habanolide = Raw(Chemical("habanolide", "111879-80-2"), 7.99)

e3_2025_12_16 = Compound({
                         e1_2025_11_30: 900,
                         habanolide: 200,
                         musk: 100
})

def main():
    chemicals, solvent = industrial(e3_2025_12_16.decompose())
    print("name,cas,percent")
    for chemical, percent in chemicals.items():
        print(f"{chemical.name},{chemical.cas},{percent * 100:.4f}")
    print(f"solvent,,{solvent * 100:.4f}")


if __name__ == "__main__":
    main()
