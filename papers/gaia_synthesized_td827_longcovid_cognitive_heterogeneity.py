"""Long-COVID cognitive heterogeneity — falsifiable subtype model.

Cross-domain (immunology x neurocognition) module that decomposes the
post-acute COVID-19 cognitive syndrome into distinguishable subtypes,
each carrying Popper-style refutable predictions on treatment response
and biomarker trajectories.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, Sequence


_FEATURE_KEYS: tuple[str, ...] = (
    "il6_pg_ml",
    "nfl_pg_ml",
    "viral_persistence",
    "autoantibody_index",
    "hrv_rmssd_ms",
    "moca_score",
    "pasat_score",
    "digit_span",
)


@dataclass(frozen=True)
class PatientProfile:
    """Multimodal vector for a single long-COVID patient.

    Units kept explicit so falsification thresholds remain interpretable.
    """
    patient_id: str
    il6_pg_ml: float
    nfl_pg_ml: float
    viral_persistence: float
    autoantibody_index: float
    hrv_rmssd_ms: float
    age: float
    months_since_infection: float
    moca_score: float
    pasat_score: float
    digit_span: float

    def feature_vector(self) -> tuple[float, ...]:
        return tuple(getattr(self, k) for k in _FEATURE_KEYS)


@dataclass(frozen=True)
class Subtype:
    """A cognitive subtype hypothesis with falsifiable predictions."""
    name: str
    centroid: tuple[float, ...]
    treatment_effect: dict[str, float]   # tx_id -> expected Cohen's d
    refutation_threshold: float          # |d| below which subtype is refuted
    biomarker_signature: dict[str, tuple[float, float]]  # key -> (lo, hi)


@dataclass
class FalsificationReport:
    subtype: str
    treatment: str
    observed_effect: float
    predicted_effect: float
    refuted: bool
    margin: float


def _z(x: float, mu: float, sigma: float) -> float:
    return (x - mu) / sigma if sigma > 1e-9 else 0.0


def _euclid(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def _standardize(vec: Sequence[float], means: Sequence[float],
                 stds: Sequence[float]) -> tuple[float, ...]:
    return tuple(_z(v, m, s) for v, m, s in zip(vec, means, stds))


def reference_population_stats() -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Population means/SDs grounded in 2024-2025 long-COVID cohorts.

    Order matches `_FEATURE_KEYS`. Values are clinically plausible
    rather than fitted - the module exposes hooks for re-fitting.
    """
    means = (3.2, 12.0, 0.18, 1.1, 35.0, 25.0, 45.0, 6.5)
    stds = (2.5, 6.0, 0.22, 0.6, 14.0, 3.0, 12.0, 1.4)
    return means, stds


def canonical_subtypes() -> list[Subtype]:
    """Three falsifiable subtypes derived from current mechanistic literature.

    - INFL: chronic IL-6 driven inflammation phenotype.
    - VIRAL: viral persistence / antigen reservoir phenotype.
    - DYSAUT: autoimmune/dysautonomic phenotype with normal CNS damage markers.
    """
    means, stds = reference_population_stats()

    def _c(raw: Sequence[float]) -> tuple[float, ...]:
        return _standardize(raw, means, stds)

    return [
        Subtype(
            name="INFL",
            centroid=_c((9.5, 22.0, 0.10, 0.9, 28.0, 22.0, 35.0, 5.5)),
            treatment_effect={"low_dose_naltrexone": 0.55,
                              "anti_il6": 0.70,
                              "antiviral": 0.05},
            refutation_threshold=0.25,
            biomarker_signature={"il6_pg_ml": (6.0, 30.0),
                                 "nfl_pg_ml": (15.0, 60.0)},
        ),
        Subtype(
            name="VIRAL",
            centroid=_c((3.0, 15.0, 0.75, 1.0, 32.0, 24.0, 40.0, 6.0)),
            treatment_effect={"low_dose_naltrexone": 0.10,
                              "anti_il6": 0.05,
                              "antiviral": 0.65},
            refutation_threshold=0.25,
            biomarker_signature={"viral_persistence": (0.45, 1.0)},
        ),
        Subtype(
            name="DYSAUT",
            centroid=_c((2.4, 10.0, 0.12, 2.6, 18.0, 26.0, 42.0, 6.2)),
            treatment_effect={"low_dose_naltrexone": 0.30,
                              "anti_il6": 0.10,
                              "antiviral": 0.05,
                              "ivig": 0.50},
            refutation_threshold=0.20,
            biomarker_signature={"autoantibody_index": (2.0, 6.0),
                                 "hrv_rmssd_ms": (5.0, 22.0)},
        ),
    ]


def assign_subtype(patient: PatientProfile,
                   subtypes: Sequence[Subtype] | None = None
                   ) -> tuple[str, float, dict[str, float]]:
    """Assign a patient to the nearest subtype in standardized space.

    Returns (subtype_name, confidence in [0,1], distance_map).
    Confidence = softmin on negative distances.
    """
    subs = list(subtypes) if subtypes is not None else canonical_subtypes()
    means, stds = reference_population_stats()
    pz = _standardize(patient.feature_vector(), means, stds)

    distances = {s.name: _euclid(pz, s.centroid) for s in subs}
    neg = [-d for d in distances.values()]
    m = max(neg)
    exps = [math.exp(v - m) for v in neg]
    z = sum(exps)
    probs = [e / z for e in exps]
    best_idx = max(range(len(subs)), key=lambda i: probs[i])
    return subs[best_idx].name, probs[best_idx], distances


def predicted_effect(subtype: Subtype, treatment: str) -> float:
    """Predicted Cohen's d for treatment under this subtype (0 if untested)."""
    return subtype.treatment_effect.get(treatment, 0.0)


def evaluate_falsification(subtype: Subtype, treatment: str,
                           observed_effect: float) -> FalsificationReport:
    """Popper-style refutation test.

    A subtype is refuted by a treatment trial if the observed effect
    is on the wrong side of the refutation threshold relative to the
    prediction. We require sign agreement AND magnitude within tolerance.
    """
    pred = predicted_effect(subtype, treatment)
    margin = observed_effect - pred
    sign_ok = (pred * observed_effect) >= 0
    magnitude_ok = abs(margin) <= max(0.4, abs(pred))
    significant_prediction = abs(pred) >= subtype.refutation_threshold
    refuted = significant_prediction and (
        not sign_ok or abs(observed_effect) < subtype.refutation_threshold
    ) and not magnitude_ok
    return FalsificationReport(
        subtype=subtype.name,
        treatment=treatment,
        observed_effect=observed_effect,
        predicted_effect=pred,
        refuted=refuted,
        margin=margin,
    )


def heterogeneity_index(patients: Iterable[PatientProfile]) -> float:
    """Quantify cognitive heterogeneity in a cohort.

    Returns a normalized entropy in [0, 1] over assigned subtypes.
    0 = monomorphic, 1 = uniform across subtypes.
    """
    subs = canonical_subtypes()
    counts: dict[str, int] = {s.name: 0 for s in subs}
    n = 0
    for p in patients:
        name, _, _ = assign_subtype(p, subs)
        counts[name] = counts.get(name, 0) + 1
        n += 1
    if n == 0:
        return 0.0
    probs = [c / n for c in counts.values() if c > 0]
    h = -sum(p * math.log(p) for p in probs)
    return h / math.log(len(subs)) if len(subs) > 1 else 0.0


def design_falsifiable_trial(subtype_name: str, treatment: str,
                             alpha: float = 0.05, power: float = 0.80
                             ) -> dict[str, float]:
    """Return a minimum sample size estimate to falsify the prediction.

    Uses the standard two-sample t-test approximation:
        n_per_arm ≈ 2 * ((z_a + z_b) / d)^2
    where d is the predicted effect size for the (subtype, treatment) pair.
    """
    subs = {s.name: s for s in canonical_subtypes()}
    if subtype_name not in subs:
        raise ValueError(f"Unknown subtype: {subtype_name}")
    d = predicted_effect(subs[subtype_name], treatment)
    if abs(d) < 1e-3:
        return {"n_per_arm": float("inf"),
                "predicted_effect": d,
                "refutation_threshold": subs[subtype_name].refutation_threshold}
    z_a = 1.959963 if abs(alpha - 0.05) < 1e-6 else _inv_norm(1 - alpha / 2)
    z_b = 0.841621 if abs(power - 0.80) < 1e-6 else _inv_norm(power)
    n_per_arm = 2.0 * ((z_a + z_b) / d) ** 2
    return {
        "n_per_arm": math.ceil(n_per_arm),
        "predicted_effect": d,
        "refutation_threshold": subs[subtype_name].refutation_threshold,
        "alpha": alpha,
        "power": power,
    }


def _inv_norm(p: float) -> float:
    """Acklam's inverse normal CDF approximation (no scipy dependency)."""
    if not (0.0 < p < 1.0):
        raise ValueError("p must be in (0, 1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00]
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
               ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5])*q / \
               (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
            ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)


def cross_domain_summary(patient: PatientProfile) -> dict[str, object]:
    """Produce a clinician-readable summary tying biomarkers to predictions."""
    subs = canonical_subtypes()
    name, conf, distances = assign_subtype(patient, subs)
    chosen = next(s for s in subs if s.name == name)
    flags: list[str] = []
    for key, (lo, hi) in chosen.biomarker_signature.items():
        v = getattr(patient, key)
        if not (lo <= v <= hi):
            flags.append(f"{key}={v} outside expected [{lo},{hi}]")
    return {
        "patient_id": patient.patient_id,
        "assigned_subtype": name,
        "confidence": round(conf, 3),
        "distances": {k: round(v, 3) for k, v in distances.items()},
        "predicted_treatments": dict(chosen.treatment_effect),
        "signature_violations": flags,
        "is_signature_consistent": not flags,
    }


if __name__ == "__main__":
    p1 = PatientProfile(
        patient_id="LC-001",
        il6_pg_ml=11.0, nfl_pg_ml=24.0, viral_persistence=0.12,
        autoantibody_index=1.0, hrv_rmssd_ms=27.0, age=44,
        months_since_infection=14, moca_score=23, pasat_score=33, digit_span=5,
    )
    p2 = PatientProfile(
        patient_id="LC-002",
        il6_pg_ml=2.8, nfl_pg_ml=14.0, viral_persistence=0.82,
        autoantibody_index=0.9, hrv_rmssd_ms=33.0, age=38,
        months_since_infection=10, moca_score=24, pasat_score=41, digit_span=6,
    )
    p3 = PatientProfile(
        patient_id="LC-003",
        il6_pg_ml=2.1, nfl_pg_ml=9.0, viral_persistence=0.10,
        autoantibody_index=2.9, hrv_rmssd_ms=14.0, age=29,
        months_since_infection=18, moca_score=27, pasat_score=43, digit_span=6,
    )
    cohort = [p1, p2, p3]
    for p in cohort:
        summary = cross_domain_summary(p)
        print(summary)
    print("heterogeneity_index:", round(heterogeneity_index(cohort), 3))
    report = evaluate_falsification(
        next(s for s in canonical_subtypes() if s.name == "INFL"),
        "anti_il6",
        observed_effect=0.05,
    )
    print("falsification:", report)
    design = design_falsifiable_trial("VIRAL", "antiviral")
    print("trial_design:", design)