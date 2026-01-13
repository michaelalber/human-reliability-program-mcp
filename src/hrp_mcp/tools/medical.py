"""Medical standards tools for HRP MCP.

Provides tools for HRP medical standards from Subpart B.
"""

from dataclasses import dataclass, field

from hrp_mcp.audit import audit_log
from hrp_mcp.resources.reference_data import (
    MEDICAL_STANDARDS,
    get_hrp_role,
    get_medical_standard,
)
from hrp_mcp.server import mcp

# --- Medical Condition Evaluation Helpers ---


@dataclass
class ConditionMatcher:
    """Configuration for matching a medical condition to standards."""

    standard_id: str
    keywords: tuple[str, ...]
    considerations: list[str] = field(default_factory=list)


# Keyword mappings for medical condition evaluation
CONDITION_MATCHERS: list[ConditionMatcher] = [
    ConditionMatcher(
        standard_id="psychological_evaluation",
        keywords=("depression", "anxiety", "bipolar", "ptsd", "psychiatric", "mental"),
        considerations=[
            "Current symptom status and stability",
            "Medication regimen and compliance",
            "Treatment history and response",
            "Impact on job performance",
            "Risk of decompensation under stress",
        ],
    ),
    ConditionMatcher(
        standard_id="physical_examination",
        keywords=(
            "heart",
            "cardiac",
            "hypertension",
            "diabetes",
            "seizure",
            "vision",
            "hearing",
            "back",
            "injury",
        ),
        considerations=[
            "Condition stability and control",
            "Medication side effects",
            "Risk of sudden incapacitation",
            "Ability to perform essential job functions",
            "Need for accommodations",
        ],
    ),
    ConditionMatcher(
        standard_id="substance_use",
        keywords=("alcohol", "drug", "substance", "addiction", "recovery"),
        considerations=[
            "Duration of sobriety/recovery",
            "Participation in treatment program",
            "Ongoing support system",
            "Risk of relapse",
            "Compliance with random testing",
        ],
    ),
]

DEFAULT_CONSIDERATIONS = [
    "Current status and stability of condition",
    "Impact on ability to perform HRP duties safely",
    "Risk assessment for self and others",
]

EVALUATION_PROCESS = [
    "Review of medical documentation",
    "Physical examination by Designated Physician",
    "Psychological evaluation if indicated",
    "Job task analysis comparison",
    "Determination of fitness for duty",
]


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    """Check if text contains any of the keywords."""
    return any(keyword in text for keyword in keywords)


def _find_matching_standards(
    condition_lower: str,
) -> tuple[list[dict], list[str]]:
    """
    Find medical standards and considerations matching the condition.

    Returns tuple of (standards list, considerations list).
    """
    standards: list[dict] = []
    considerations: list[str] = []
    matched_standard_ids: set[str] = set()

    for matcher in CONDITION_MATCHERS:
        if _contains_any(condition_lower, matcher.keywords):
            std = get_medical_standard(matcher.standard_id)
            if std and matcher.standard_id not in matched_standard_ids:
                standards.append(std.to_dict())
                matched_standard_ids.add(matcher.standard_id)
                considerations.extend(matcher.considerations)

    # Always include general medical standard
    gen_std = get_medical_standard("general_medical")
    if gen_std and "general_medical" not in matched_standard_ids:
        standards.append(gen_std.to_dict())

    return standards, considerations


def _build_medical_condition_response(
    condition: str,
    standards: list[dict],
    considerations: list[str],
) -> dict:
    """Build the response dictionary for medical condition evaluation."""
    return {
        "condition": condition,
        "relevant_standards": standards,
        "evaluation_process": EVALUATION_PROCESS,
        "key_considerations": considerations if considerations else DEFAULT_CONSIDERATIONS,
        "recommendation": "Formal evaluation by Designated Physician required for official determination.",
        "disclaimer": "This is informational guidance only. All medical fitness determinations must be made by the Designated Physician.",
    }


@mcp.tool()
@audit_log
async def get_medical_standards(category: str | None = None) -> dict:
    """
    Get HRP medical standards from 10 CFR 712 Subpart B.

    Retrieve information about medical standards that apply to HRP
    candidates and certified individuals.

    Args:
        category: Optional category to filter standards:
                  - "general" - General medical standards (712.30)
                  - "physical" - Physical examination requirements (712.32)
                  - "psychological" - Psychological evaluation (712.34)
                  - "substance" - Substance use standards (712.13)
                  Leave empty for all standards.

    Returns:
        Medical standards information including:
        - standards: List of medical standards with details
        - subpart: Subpart B reference
    """
    standards = []

    if category:
        category_lower = category.lower().strip()
        for key, standard in MEDICAL_STANDARDS.items():
            if standard.category == category_lower or category_lower in key:
                standards.append(standard.to_dict())
    else:
        for standard in MEDICAL_STANDARDS.values():
            standards.append(standard.to_dict())

    if not standards and category:
        return {
            "error": f"Unknown category: {category}",
            "valid_categories": ["general", "physical", "psychological", "substance"],
        }

    return {
        "subpart": "B",
        "citation": "10 CFR Part 712, Subpart B",
        "title": "Medical Standards",
        "standards": standards,
        "note": "Medical standards are evaluated by the Designated Physician based on job task analysis requirements.",
    }


@mcp.tool()
@audit_log
async def get_psychological_evaluation() -> dict:
    """
    Get psychological evaluation requirements per 10 CFR 712.34.

    Retrieve information about psychological evaluation criteria and
    procedures for HRP candidates and certified individuals.

    Returns:
        Psychological evaluation information including:
        - purpose: Purpose of psychological evaluation
        - when_required: When evaluation is required
        - evaluation_areas: Areas assessed in evaluation
        - evaluator: Who conducts the evaluation
        - section: CFR section reference
    """
    psych_standard = get_medical_standard("psychological_evaluation")

    return {
        "section": "712.34",
        "citation": "10 CFR 712.34",
        "title": "Psychological evaluation",
        "purpose": "To determine the psychological fitness of HRP candidates and certified individuals for HRP duties",
        "when_required": [
            "Initial HRP certification (if indicated by medical assessment)",
            "Annual recertification (if indicated)",
            "For-cause evaluation based on observed behavior",
            "Return-to-work evaluation after psychological issue",
            "Following any concerning behavioral observation",
        ],
        "evaluation_areas": psych_standard.evaluation_criteria
        if psych_standard
        else [
            "Emotional stability",
            "Judgment and decision-making",
            "Impulse control",
            "Stress tolerance",
            "Interpersonal functioning",
            "Honesty and integrity",
        ],
        "conditions_of_concern": psych_standard.conditions
        if psych_standard
        else [
            "Mood disorders",
            "Anxiety disorders",
            "Personality disorders",
            "Psychotic disorders",
            "Cognitive impairments",
        ],
        "evaluator": "Designated Psychologist",
        "outcome": "Recommendation to Designated Physician regarding psychological fitness for HRP duties",
        "note": "Psychological conditions that are well-controlled and do not impair reliability may not be disqualifying.",
    }


@mcp.tool()
@audit_log
async def check_medical_condition(condition: str) -> dict:
    """
    Evaluate a medical condition against HRP medical standards.

    Analyze a described medical condition to understand how it may be
    evaluated under HRP medical standards.

    Args:
        condition: Description of the medical condition. Examples:
                   - "controlled hypertension on medication"
                   - "history of depression, currently in remission"
                   - "type 2 diabetes"
                   - "back injury limiting lifting"

    Returns:
        Evaluation information including:
        - condition: The input condition
        - relevant_standards: Applicable medical standards
        - evaluation_process: How this would typically be evaluated
        - key_considerations: Important factors in evaluation
        - recommendation: Recommended next steps
    """
    condition_lower = condition.lower()

    # Find matching standards and considerations
    standards, considerations = _find_matching_standards(condition_lower)

    return _build_medical_condition_response(condition, standards, considerations)


@mcp.tool()
@audit_log
async def get_designated_physician_role() -> dict:
    """
    Get information about the Designated Physician role per 10 CFR 712.33.

    Retrieve details about the responsibilities and qualifications of
    the Designated Physician in the HRP.

    Returns:
        Designated Physician information including:
        - title: Role title
        - responsibilities: List of responsibilities
        - qualifications: Required qualifications
        - section: CFR section reference
    """
    dp_info = get_hrp_role("designated_physician")

    return {
        "section": "712.33",
        "citation": "10 CFR 712.33",
        "title": dp_info.title if dp_info else "Designated Physician",
        "description": dp_info.description
        if dp_info
        else "A licensed physician designated to provide medical evaluations of HRP candidates and certified individuals.",
        "responsibilities": dp_info.responsibilities
        if dp_info
        else [
            "Conduct medical assessments",
            "Review medical history",
            "Perform physical examinations",
            "Determine medical fitness for duty",
            "Recommend accommodations if appropriate",
            "Report medical concerns to HRP management",
        ],
        "qualifications": dp_info.qualifications
        if dp_info
        else [
            "Licensed physician (MD or DO)",
            "Designated by HRP Management Official",
            "Training in occupational medicine preferred",
            "Knowledge of HRP medical requirements",
        ],
        "relationship_to_hrp": [
            "Reports medical fitness determinations to HRP management",
            "Coordinates with Designated Psychologist as needed",
            "Maintains confidentiality of medical information",
            "Provides return-to-work evaluations",
        ],
    }
