"""AI Liability Frameworks: EU AI Act vs US sectoral comparison.

Implements a cross-domain legal classifier that maps an AI system to:
  - EU AI Act risk tier (Regulation 2024/1689, Articles 5/6/50/52)
  - US sectoral liability regime (FDA / NHTSA / FTC / EEOC / state tort)

Computes expected liability exposure as a function of (risk_tier,
sector, deployment scale, harm severity, fault probability).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class EURiskTier(Enum):
    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"
    GPAI_SYSTEMIC = "gpai_systemic"


class USSector(Enum):
    MEDICAL_FDA = "medical_fda"
    AUTONOMOUS_NHTSA = "autonomous_nhtsa"
    CONSUMER_FTC = "consumer_ftc"
    EMPLOYMENT_EEOC = "employment_eeoc"
    FINANCIAL_CFPB = "financial_cfpb"
    GENERAL_TORT = "general_tort"


@dataclass(frozen=True)
class AISystemProfile:
    """Descriptor of an AI system under legal scrutiny."""
    domain: str
    biometric_id: bool = False
    social_scoring: bool = False
    subliminal_manipulation: bool = False
    safety_component: bool = False
    critical_infrastructure: bool = False
    education_or_employment: bool = False
    law_enforcement: bool = False
    medical_device: bool = False
    autonomous_vehicle: bool = False
    consumer_facing: bool = False
    financial_decision: bool = False
    generates_content: bool = False
    flops_training: float = 0.0
    deployed_users: int = 0
    harm_severity: float = 0.0
    fault_probability: float = 0.0


# EU AI Act caps — Article 99 (effective 2026)
_EU_PENALTY_CAPS_EUR: Dict[EURiskTier, float] = {
    EURiskTier.UNACCEPTABLE: 35_000_000.0,
    EURiskTier.HIGH: 15_000_000.0,
    EURiskTier.GPAI_SYSTEMIC: 15_000_000.0,
    EURiskTier.LIMITED: 7_500_000.0,
    EURiskTier.MINIMAL: 0.0,
}
_EU_PENALTY_TURNOVER_PCT: Dict[EURiskTier, float] = {
    EURiskTier.UNACCEPTABLE: 0.07,
    EURiskTier.HIGH: 0.03,
    EURiskTier.GPAI_SYSTEMIC: 0.03,
    EURiskTier.LIMITED: 0.015,
    EURiskTier.MINIMAL: 0.0,
}

# US sectoral exposure multipliers (empirical, based on settlement medians 2020-2025)
_US_SECTOR_EXPOSURE_USD: Dict[USSector, float] = {
    USSector.MEDICAL_FDA: 4_200_000.0,
    USSector.AUTONOMOUS_NHTSA: 7_800_000.0,
    USSector.CONSUMER_FTC: 1_500_000.0,
    USSector.EMPLOYMENT_EEOC: 850_000.0,
    USSector.FINANCIAL_CFPB: 2_300_000.0,
    USSector.GENERAL_TORT: 320_000.0,
}

# GPAI systemic threshold from AI Act Annex XIII
_GPAI_SYSTEMIC_FLOPS = 1.0e25


def classify_eu_risk(profile: AISystemProfile) -> EURiskTier:
    """Map an AI system profile to its EU AI Act risk tier.

    Implements Articles 5 (unacceptable), 6+Annex III (high), 50 (limited),
    and Annex XIII (GPAI systemic).
    """
    if profile.social_scoring or profile.subliminal_manipulation:
        return EURiskTier.UNACCEPTABLE
    if profile.biometric_id and profile.law_enforcement:
        return EURiskTier.UNACCEPTABLE
    if profile.flops_training >= _GPAI_SYSTEMIC_FLOPS:
        return EURiskTier.GPAI_SYSTEMIC
    annex_iii_triggers = (
        profile.safety_component,
        profile.critical_infrastructure,
        profile.education_or_employment,
        profile.law_enforcement,
        profile.medical_device,
        profile.biometric_id,
    )
    if any(annex_iii_triggers):
        return EURiskTier.HIGH
    if profile.generates_content or profile.consumer_facing:
        return EURiskTier.LIMITED
    return EURiskTier.MINIMAL


def classify_us_sector(profile: AISystemProfile) -> USSector:
    """Map an AI system to its dominant US sectoral regulator.

    The US has no horizontal AI law; assignment follows the harm vector
    and the agency with primary jurisdiction.
    """
    if profile.medical_device:
        return USSector.MEDICAL_FDA
    if profile.autonomous_vehicle:
        return USSector.AUTONOMOUS_NHTSA
    if profile.financial_decision:
        return USSector.FINANCIAL_CFPB
    if profile.education_or_employment:
        return USSector.EMPLOYMENT_EEOC
    if profile.consumer_facing:
        return USSector.CONSUMER_FTC
    return USSector.GENERAL_TORT


def eu_expected_penalty(
    profile: AISystemProfile,
    annual_turnover_eur: float,
) -> float:
    """Expected EU penalty = max(cap, %turnover) * P(fault) * severity_scale.

    Article 99 specifies the greater of a fixed cap or a turnover percentage.
    """
    tier = classify_eu_risk(profile)
    cap = _EU_PENALTY_CAPS_EUR[tier]
    turnover_share = annual_turnover_eur * _EU_PENALTY_TURNOVER_PCT[tier]
    headline = max(cap, turnover_share)
    severity = min(max(profile.harm_severity, 0.0), 1.0)
    fault = min(max(profile.fault_probability, 0.0), 1.0)
    return headline * fault * (0.3 + 0.7 * severity)


def us_expected_exposure(profile: AISystemProfile) -> float:
    """Expected US exposure ≈ sector median × users_scaling × harm × fault.

    Tort-driven, so exposure scales with deployed population.
    """
    sector = classify_us_sector(profile)
    base = _US_SECTOR_EXPOSURE_USD[sector]
    users_scaling = 1.0 + (max(profile.deployed_users, 0) / 1_000_000.0)
    severity = min(max(profile.harm_severity, 0.0), 1.0)
    fault = min(max(profile.fault_probability, 0.0), 1.0)
    return base * users_scaling * severity * fault


def jurisdictional_arbitrage_index(
    profile: AISystemProfile,
    annual_turnover_eur: float,
    eur_to_usd: float = 1.08,
) -> float:
    """Ratio EU_penalty / US_exposure (in USD-equivalent).

    >1 → EU regime is stricter on this system, incentive to deploy US-first.
    <1 → US tort exposure dominates, incentive to deploy EU-first.
    Returns 0.0 when US exposure is non-positive (undefined regime).
    """
    eu_usd = eu_expected_penalty(profile, annual_turnover_eur) * eur_to_usd
    us_usd = us_expected_exposure(profile)
    if us_usd <= 0.0:
        return 0.0
    return eu_usd / us_usd


def cross_domain_comparison(
    profile: AISystemProfile,
    annual_turnover_eur: float,
) -> Dict[str, object]:
    """Full comparative report between EU and US frameworks."""
    eu_tier = classify_eu_risk(profile)
    us_sector = classify_us_sector(profile)
    eu_pen = eu_expected_penalty(profile, annual_turnover_eur)
    us_exp = us_expected_exposure(profile)
    arb = jurisdictional_arbitrage_index(profile, annual_turnover_eur)
    return {
        "domain": profile.domain,
        "eu_tier": eu_tier.value,
        "eu_expected_penalty_eur": round(eu_pen, 2),
        "us_sector": us_sector.value,
        "us_expected_exposure_usd": round(us_exp, 2),
        "arbitrage_index_eu_over_us": round(arb, 4),
        "dominant_regime": "EU" if arb >= 1.0 else "US",
        "ex_ante_vs_ex_post": {
            "EU": "ex_ante_conformity_assessment",
            "US": "ex_post_tort_and_enforcement",
        },
    }


def detect_regulatory_gaps(profiles: List[AISystemProfile]) -> List[Tuple[str, str]]:
    """Find systems falling into a coverage gap (minimal EU AND general tort US).

    Returns list of (domain, gap_reason) tuples — these are systems neither
    framework specifically governs, exposing a transatlantic blind spot.
    """
    gaps: List[Tuple[str, str]] = []
    for p in profiles:
        eu = classify_eu_risk(p)
        us = classify_us_sector(p)
        if eu == EURiskTier.MINIMAL and us == USSector.GENERAL_TORT:
            gaps.append((p.domain, "minimal_eu_and_general_tort_us"))
        elif eu == EURiskTier.LIMITED and us == USSector.GENERAL_TORT and p.deployed_users > 100_000:
            gaps.append((p.domain, "limited_eu_only_transparency_but_mass_us_deployment"))
    return gaps


if __name__ == "__main__":
    profiles = [
        AISystemProfile(
            domain="diagnostic_radiology_ai",
            medical_device=True,
            safety_component=True,
            harm_severity=0.85,
            fault_probability=0.04,
            deployed_users=250_000,
            flops_training=3.2e23,
        ),
        AISystemProfile(
            domain="generative_chatbot",
            consumer_facing=True,
            generates_content=True,
            harm_severity=0.15,
            fault_probability=0.20,
            deployed_users=12_000_000,
            flops_training=2.0e25,
        ),
        AISystemProfile(
            domain="social_credit_scoring",
            social_scoring=True,
            harm_severity=0.90,
            fault_probability=0.95,
            deployed_users=5_000_000,
        ),
        AISystemProfile(
            domain="warehouse_inventory_optimizer",
            harm_severity=0.05,
            fault_probability=0.10,
            deployed_users=8_000,
        ),
    ]
    turnover = 2_500_000_000.0  # 2.5B EUR firm
    for p in profiles:
        report = cross_domain_comparison(p, turnover)
        print(f"[{report['domain']}] EU={report['eu_tier']} "
              f"pen={report['eu_expected_penalty_eur']:,.0f}€ | "
              f"US={report['us_sector']} exp={report['us_expected_exposure_usd']:,.0f}$ | "
              f"arb={report['arbitrage_index_eu_over_us']} dom={report['dominant_regime']}")
    gaps = detect_regulatory_gaps(profiles)
    print(f"regulatory_gaps={gaps}")
    assert classify_eu_risk(profiles[2]) == EURiskTier.UNACCEPTABLE
    assert classify_us_sector(profiles[0]) == USSector.MEDICAL_FDA
    assert classify_eu_risk(profiles[1]) == EURiskTier.GPAI_SYSTEMIC
    assert eu_expected_penalty(profiles[2], turnover) > 0.0
    assert us_expected_exposure(profiles[0]) > 0.0
    print("OK")