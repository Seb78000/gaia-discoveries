"""Harmonic universality test module: innate vs enculturation hypothesis.

Models the AGI-TEST-004 question: which features of musical perception are
universal (innate, biologically grounded) vs culturally learned (enculturated).

Innate candidates (predicted universal across cultures):
  - Octave equivalence (2:1 frequency ratio)
  - Small-integer ratio consonance bias (perfect fifth 3:2, fourth 4:3)
  - Discrete pitch categorization

Enculturated candidates (predicted to vary across cultures):
  - Scale degree preference (major/minor vs maqam vs raga vs gamelan)
  - Tuning system (12-TET vs Pythagorean vs just intonation vs 5-TET)
  - Rhythmic complexity tolerance
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple


CENTS_PER_OCTAVE = 1200.0
INNATE_RATIOS: Tuple[Fraction, ...] = (
    Fraction(2, 1),
    Fraction(3, 2),
    Fraction(4, 3),
    Fraction(5, 4),
    Fraction(6, 5),
)


def ratio_to_cents(ratio: float) -> float:
    """Convert a frequency ratio to cents (logarithmic pitch distance)."""
    if ratio <= 0:
        raise ValueError("ratio must be strictly positive")
    return CENTS_PER_OCTAVE * math.log2(ratio)


def cents_to_ratio(cents: float) -> float:
    """Inverse of ratio_to_cents."""
    return 2.0 ** (cents / CENTS_PER_OCTAVE)


def consonance_score(ratio: float, max_denominator: int = 16) -> float:
    """Helmholtz/Plomp-style proxy: rationals with small denominators sound consonant.

    Returns a score in [0, 1] where 1 means perfectly consonant (low integer ratio).
    The score decays with the denominator of the closest rational approximation.
    """
    if ratio <= 0:
        return 0.0
    approx = Fraction(ratio).limit_denominator(max_denominator)
    n, d = approx.numerator, approx.denominator
    complexity = math.log2(n * d + 1)
    return 1.0 / (1.0 + complexity)


def octave_equivalence_score(scale_cents: Sequence[float]) -> float:
    """Score how strongly a scale exhibits octave equivalence.

    A scale that repeats every 1200 cents (or a small multiple) scores high.
    Returns 1.0 when the scale span is exactly N*1200 cents for some N>=1.
    """
    if not scale_cents:
        return 0.0
    span = max(scale_cents) - min(scale_cents)
    if span <= 0:
        return 0.0
    nearest_octave = round(span / CENTS_PER_OCTAVE)
    if nearest_octave < 1:
        return 0.0
    deviation = abs(span - nearest_octave * CENTS_PER_OCTAVE)
    return math.exp(-deviation / 50.0)


@dataclass
class CultureScale:
    """A scale identified with a culture, expressed in cents from tonic."""

    name: str
    degrees_cents: Tuple[float, ...]
    origin: str = "unknown"

    def as_ratios(self) -> Tuple[float, ...]:
        return tuple(cents_to_ratio(c) for c in self.degrees_cents)

    def consonance_profile(self) -> Tuple[float, ...]:
        return tuple(consonance_score(r) for r in self.as_ratios())


@dataclass
class UniversalityReport:
    """Result of comparing scales across cultures."""

    octave_universality: float
    consonance_universality: float
    cultural_divergence: float
    per_scale: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def verdict(self) -> str:
        """Plain-text claim about innate vs enculturated weighting."""
        innate_signal = 0.5 * (self.octave_universality + self.consonance_universality)
        cultural_signal = self.cultural_divergence
        if innate_signal > 0.7 and cultural_signal > 0.3:
            return "DUAL: octave+consonance innate, scale shape enculturated"
        if innate_signal > 0.7:
            return "INNATE-DOMINANT: universal structural features"
        if cultural_signal > 0.6:
            return "ENCULTURATION-DOMINANT: cross-cultural divergence high"
        return "INCONCLUSIVE: signals overlap, more data required"


def _pairwise_jaccard_cents(a: Sequence[float], b: Sequence[float], tol: float = 25.0) -> float:
    """Jaccard similarity between two scales (cent positions), tolerant to small detuning."""
    if not a or not b:
        return 0.0
    matched_a = set()
    matched_b = set()
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            if j in matched_b:
                continue
            if abs(ca - cb) <= tol:
                matched_a.add(i)
                matched_b.add(j)
                break
    union = len(a) + len(b) - len(matched_a)
    return len(matched_a) / union if union else 0.0


def analyze_cross_cultural(scales: Sequence[CultureScale]) -> UniversalityReport:
    """Core computation: score innate vs enculturated features across cultures."""
    if not scales:
        raise ValueError("at least one scale required")

    per_scale: Dict[str, Dict[str, float]] = {}
    octave_scores: List[float] = []
    consonance_scores: List[float] = []

    for scale in scales:
        oct_score = octave_equivalence_score(scale.degrees_cents)
        cons_profile = scale.consonance_profile()
        cons_mean = sum(cons_profile) / len(cons_profile) if cons_profile else 0.0
        per_scale[scale.name] = {
            "octave": oct_score,
            "consonance_mean": cons_mean,
            "degree_count": float(len(scale.degrees_cents)),
        }
        octave_scores.append(oct_score)
        consonance_scores.append(cons_mean)

    octave_universality = sum(octave_scores) / len(octave_scores)
    consonance_universality = sum(consonance_scores) / len(consonance_scores)

    divergences: List[float] = []
    for i in range(len(scales)):
        for j in range(i + 1, len(scales)):
            sim = _pairwise_jaccard_cents(scales[i].degrees_cents, scales[j].degrees_cents)
            divergences.append(1.0 - sim)
    cultural_divergence = sum(divergences) / len(divergences) if divergences else 0.0

    return UniversalityReport(
        octave_universality=octave_universality,
        consonance_universality=consonance_universality,
        cultural_divergence=cultural_divergence,
        per_scale=per_scale,
    )


def reference_scales() -> List[CultureScale]:
    """Curated cross-cultural scale set used as ground truth in AGI-TEST-004."""
    return [
        CultureScale(
            name="western_major",
            origin="europe",
            degrees_cents=(0.0, 200.0, 400.0, 500.0, 700.0, 900.0, 1100.0, 1200.0),
        ),
        CultureScale(
            name="pythagorean_diatonic",
            origin="ancient_greece",
            degrees_cents=(0.0, 203.91, 407.82, 498.04, 701.96, 905.87, 1109.78, 1200.0),
        ),
        CultureScale(
            name="hindustani_bhairav",
            origin="india",
            degrees_cents=(0.0, 100.0, 400.0, 500.0, 700.0, 800.0, 1100.0, 1200.0),
        ),
        CultureScale(
            name="arabic_maqam_rast",
            origin="middle_east",
            degrees_cents=(0.0, 200.0, 350.0, 500.0, 700.0, 900.0, 1050.0, 1200.0),
        ),
        CultureScale(
            name="javanese_slendro",
            origin="indonesia",
            degrees_cents=(0.0, 240.0, 480.0, 720.0, 960.0, 1200.0),
        ),
        CultureScale(
            name="japanese_in",
            origin="japan",
            degrees_cents=(0.0, 100.0, 500.0, 700.0, 800.0, 1200.0),
        ),
    ]


def run_innate_vs_enculturation_test() -> UniversalityReport:
    """Top-level entry point: score the dual-hypothesis on reference scales."""
    return analyze_cross_cultural(reference_scales())


if __name__ == "__main__":
    report = run_innate_vs_enculturation_test()
    print(f"octave_universality     = {report.octave_universality:.4f}")
    print(f"consonance_universality = {report.consonance_universality:.4f}")
    print(f"cultural_divergence     = {report.cultural_divergence:.4f}")
    print(f"verdict                 = {report.verdict()}")
    for name, metrics in report.per_scale.items():
        print(f"  {name:30s} oct={metrics['octave']:.3f} cons={metrics['consonance_mean']:.3f}")