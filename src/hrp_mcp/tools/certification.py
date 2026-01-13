"""Certification tools for HRP MCP.

Provides tools for HRP certification requirements, position types,
and disqualifying factors.
"""

from dataclasses import dataclass

from hrp_mcp.audit import audit_log
from hrp_mcp.models.hrp import DisqualifyingFactor
from hrp_mcp.resources.reference_data import (
    CERTIFICATION_COMPONENTS,
    HRP_POSITION_TYPES,
    get_disqualifying_factor,
    get_position_type,
)
from hrp_mcp.server import mcp

# --- Disqualifying Factor Evaluation Helpers ---


@dataclass
class FactorMatcher:
    """Configuration for matching a disqualifying factor."""

    factor_id: str
    keywords: tuple[str, ...]
    is_absolute: bool = False
    secondary_keywords: tuple[str, ...] | None = None  # Additional required keywords


# Keyword mappings for disqualifying factor detection
# Order matters: hallucinogen checks come first due to special time-based logic
FACTOR_MATCHERS: list[FactorMatcher] = [
    # Drug-related factors
    FactorMatcher(
        factor_id="drug_test_positive",
        keywords=("drug", "marijuana", "cocaine", "opioid", "positive test"),
    ),
    FactorMatcher(
        factor_id="substance_use_disorder",
        keywords=("drug", "marijuana", "cocaine", "opioid"),
        secondary_keywords=("disorder", "addiction", "dependence"),
    ),
    # Alcohol-related factors
    FactorMatcher(
        factor_id="alcohol_test_positive",
        keywords=("alcohol", "drinking", "dui", "dwi"),
    ),
    FactorMatcher(
        factor_id="alcohol_use_disorder",
        keywords=("alcohol", "drinking"),
        secondary_keywords=("disorder", "alcoholism", "dependence"),
    ),
    # Mental health conditions
    FactorMatcher(
        factor_id="mental_health_condition",
        keywords=(
            "depression",
            "anxiety",
            "bipolar",
            "ptsd",
            "mental",
            "psychiatric",
            "psychological",
        ),
    ),
    # Physical conditions
    FactorMatcher(
        factor_id="physical_condition",
        keywords=("physical", "disability", "chronic", "medical condition"),
    ),
    # Behavioral issues
    FactorMatcher(
        factor_id="behavioral_issue",
        keywords=("violation", "dishonest", "misconduct", "behavioral"),
    ),
    # Security concerns
    FactorMatcher(
        factor_id="security_concern",
        keywords=("security", "clearance", "foreign", "criminal"),
    ),
]

HALLUCINOGEN_KEYWORDS = ("hallucinogen", "lsd", "mushroom", "psilocybin", "mescaline", "peyote")


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    """Check if text contains any of the keywords."""
    return any(keyword in text for keyword in keywords)


def _check_hallucinogen_factors(factor_lower: str) -> list[tuple[DisqualifyingFactor, bool]]:
    """
    Check for hallucinogen-related disqualifying factors.

    Returns list of (factor, is_absolute) tuples.
    """
    results: list[tuple[DisqualifyingFactor, bool]] = []

    if not _contains_any(factor_lower, HALLUCINOGEN_KEYWORDS):
        return results

    # Check for use within 5 years (absolute disqualifier)
    within_5_years = "5 year" in factor_lower or any(
        f"{i} year" in factor_lower for i in range(1, 5)
    )
    if within_5_years:
        factor = get_disqualifying_factor("hallucinogen_use")
        if factor:
            results.append((factor, True))

    # Check for flashback (absolute disqualifier)
    if "flashback" in factor_lower:
        factor = get_disqualifying_factor("hallucinogen_flashback")
        if factor:
            results.append((factor, True))

    return results


def _check_standard_factors(factor_lower: str) -> list[tuple[DisqualifyingFactor, bool]]:
    """
    Check for standard (non-hallucinogen) disqualifying factors.

    Returns list of (factor, is_absolute) tuples.
    """
    results: list[tuple[DisqualifyingFactor, bool]] = []

    for matcher in FACTOR_MATCHERS:
        if not _contains_any(factor_lower, matcher.keywords):
            continue

        # Check secondary keywords if required
        if matcher.secondary_keywords and not _contains_any(
            factor_lower, matcher.secondary_keywords
        ):
            continue

        factor = get_disqualifying_factor(matcher.factor_id)
        if factor:
            results.append((factor, matcher.is_absolute))

    return results


def _build_disqualifying_response(
    factor_description: str,
    matching_factors: list[dict],
    is_absolute: bool,
) -> dict:
    """Build the response dictionary for disqualifying factor evaluation."""
    if not matching_factors:
        return {
            "factor_description": factor_description,
            "matching_factors": [],
            "is_absolute_disqualifier": False,
            "guidance": "No specific disqualifying factors identified based on the description provided.",
            "recommendation": "Consult with your HRP management official or Designated Physician for a formal evaluation.",
            "disclaimer": "This is informational guidance only. All HRP eligibility determinations must be made by authorized HRP officials.",
        }

    guidance_lines = [
        f"{match['name']}: {match['evaluation_guidance']}" for match in matching_factors
    ]

    recommendation = (
        "Immediate consultation with HRP management official required."
        if is_absolute
        else "Formal evaluation by appropriate HRP official recommended."
    )

    return {
        "factor_description": factor_description,
        "matching_factors": matching_factors,
        "is_absolute_disqualifier": is_absolute,
        "guidance": "\n".join(guidance_lines),
        "recommendation": recommendation,
        "disclaimer": "This is informational guidance only. All HRP eligibility determinations must be made by authorized HRP officials.",
    }


@mcp.tool()
@audit_log
async def get_certification_requirements(position_type: str | None = None) -> dict:
    """
    Get the requirements for initial HRP certification per 10 CFR 712.11.

    Retrieve the requirements that must be met for an individual to receive
    initial HRP certification. Requirements may vary by position type.

    Args:
        position_type: Optional position type to get specific requirements.
                       Options:
                       - "category_i_snm" - Category I SNM access
                       - "nuclear_explosive" - Nuclear explosive access
                       - "nuclear_explosive_duty" - Nuclear explosive duties
                       - "hrp_designated" - HRP-designated positions
                       Leave empty for general certification requirements.

    Returns:
        Certification requirements including:
        - position_type: Position type (if specified)
        - general_requirements: Requirements for all HRP positions
        - specific_requirements: Position-specific requirements (if applicable)
        - four_components: The four annual certification components
        - section: CFR section reference
    """
    general_requirements = [
        "Completion of initial HRP instruction",
        "Successful completion of supervisory review",
        "Successful completion of medical assessment",
        "Successful completion of management evaluation",
        "Successful completion of DOE personnel security review",
        "No use of hallucinogens in the preceding 5 years",
        "No flashback from hallucinogen use",
        "Initial drug test with negative result",
        "Initial alcohol test with negative result",
        "For designated positions: successful counterintelligence evaluation (may include polygraph)",
    ]

    # Get four components
    components = []
    for comp in CERTIFICATION_COMPONENTS.values():
        components.append(comp.to_dict())

    result = {
        "section": "712.11",
        "citation": "10 CFR 712.11",
        "general_requirements": general_requirements,
        "four_components": components,
    }

    if position_type:
        pos_info = get_position_type(position_type)
        if pos_info:
            result["position_type"] = pos_info.position_type.value
            result["position_title"] = pos_info.title
            result["specific_requirements"] = pos_info.requirements
            result["access_type"] = pos_info.access_type
        else:
            result["position_type_error"] = f"Unknown position type: {position_type}"
            result["valid_types"] = list(HRP_POSITION_TYPES.keys())

    return result


@mcp.tool()
@audit_log
async def get_recertification_requirements() -> dict:
    """
    Get the requirements for annual HRP recertification per 10 CFR 712.12.

    Retrieve the requirements for maintaining HRP certification through
    annual recertification.

    Returns:
        Recertification requirements including:
        - annual_requirements: List of annual requirements
        - four_components: The four components that must be completed annually
        - random_testing: Random testing requirements
        - section: CFR section reference
    """
    annual_requirements = [
        "Annual completion of HRP instruction",
        "Successful annual supervisory review",
        "Successful annual medical assessment",
        "Successful annual management evaluation",
        "Successful annual DOE personnel security review",
        "Random drug testing at least once every 12 months",
        "Random alcohol testing at least once every 12 months",
        "Continuous observation by supervisors",
        "Immediate reporting of any safety or security concerns",
    ]

    components = []
    for comp in CERTIFICATION_COMPONENTS.values():
        components.append(comp.to_dict())

    return {
        "section": "712.12",
        "citation": "10 CFR 712.12",
        "annual_requirements": annual_requirements,
        "four_components": components,
        "random_testing": {
            "drug_testing": "At least once every 12 months from previous test",
            "alcohol_testing": "At least once every 12 months from previous test",
            "for_cause_testing": "If involved in incident, unsafe practice, or reasonable suspicion",
        },
        "recertification_frequency": "Annual",
    }


@mcp.tool()
@audit_log
async def check_disqualifying_factors(factor_description: str) -> dict:
    """
    Evaluate potential disqualifying factors for HRP certification.

    Analyze a described condition or circumstance against HRP disqualifying
    factors to determine potential impact on certification.

    Args:
        factor_description: Description of the condition or circumstance to evaluate.
                           Examples:
                           - "used marijuana 2 years ago"
                           - "diagnosed with depression"
                           - "positive alcohol test last month"
                           - "hallucinogen use 6 years ago"

    Returns:
        Evaluation including:
        - factor_description: The input description
        - matching_factors: List of potentially matching disqualifying factors
        - is_absolute: Whether any matching factor is an absolute disqualifier
        - guidance: Guidance on how the factor is typically evaluated
        - recommendation: Recommended next steps
    """
    factor_lower = factor_description.lower()

    # Collect all matching factors from both checkers
    all_matches = _check_hallucinogen_factors(factor_lower) + _check_standard_factors(factor_lower)

    # Convert to dicts and determine if any are absolute disqualifiers
    matching_factors = [factor.to_dict() for factor, _ in all_matches]
    is_absolute = any(is_abs for _, is_abs in all_matches)

    return _build_disqualifying_response(factor_description, matching_factors, is_absolute)


@mcp.tool()
@audit_log
async def get_hrp_position_types() -> dict:
    """
    Get information about all HRP position types per 10 CFR 712.10.

    Retrieve details about the four types of positions that require
    HRP certification.

    Returns:
        Position types information including:
        - section: CFR section reference
        - position_types: List of all position types with details
    """
    position_types = []
    for pos_info in HRP_POSITION_TYPES.values():
        position_types.append(pos_info.to_dict())

    return {
        "section": "712.10",
        "citation": "10 CFR 712.10",
        "title": "Designation of HRP positions",
        "position_types": position_types,
        "note": "DOE/NNSA sites may designate additional positions as HRP positions based on specific site requirements and national security considerations.",
    }
