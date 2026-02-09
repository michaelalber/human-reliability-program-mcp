"""Testing tools for HRP MCP.

Provides tools for HRP drug and alcohol testing requirements.
"""

from typing import Any

from hrp_mcp.audit import audit_log
from hrp_mcp.resources.reference_data import CONTROLLED_SUBSTANCES
from hrp_mcp.server import mcp


@mcp.tool()
@audit_log
async def get_drug_testing_requirements() -> dict[str, Any]:
    """
    Get drug testing requirements per 10 CFR 712.15.

    Retrieve information about HRP drug testing procedures, timing,
    and requirements.

    Returns:
        Drug testing requirements including:
        - types_of_testing: Different types of drug tests
        - timing: When testing occurs
        - substances: Substances tested for
        - consequences: Consequences of positive tests
        - section: CFR section reference
    """
    return {
        "section": "712.15",
        "citation": "10 CFR 712.15",
        "title": "Drug and alcohol testing",
        "types_of_testing": {
            "initial": "Required before initial HRP certification",
            "random": "At least once every 12 months (unpredictable selection)",
            "for_cause": "When involved in incident, unsafe practice, or based on reasonable suspicion",
            "post_incident": "Following any safety-significant incident",
            "return_to_duty": "Before returning to HRP duties after treatment",
            "follow_up": "After return to duty, unannounced testing for specified period",
        },
        "substances_tested": CONTROLLED_SUBSTANCES,
        "testing_procedures": [
            "Collection by trained personnel",
            "Split specimen collection",
            "Chain of custody maintained",
            "Testing by certified laboratory",
            "Medical Review Officer (MRO) review of positive results",
        ],
        "consequences_of_positive": [
            "Immediate temporary removal from HRP duties",
            "MRO verification process",
            "Evaluation by Designated Physician",
            "Potential referral to Employee Assistance Program",
            "Possible permanent removal from HRP",
        ],
        "note": "Prescription medications must be reported and evaluated for impact on HRP duties.",
    }


@mcp.tool()
@audit_log
async def get_alcohol_testing_requirements() -> dict[str, Any]:
    """
    Get alcohol testing requirements per 10 CFR 712.15.

    Retrieve information about HRP alcohol testing procedures, timing,
    and thresholds.

    Returns:
        Alcohol testing requirements including:
        - types_of_testing: Different types of alcohol tests
        - timing: When testing occurs
        - thresholds: BAC thresholds and their significance
        - consequences: Consequences of positive tests
        - section: CFR section reference
    """
    return {
        "section": "712.15",
        "citation": "10 CFR 712.15",
        "title": "Drug and alcohol testing",
        "types_of_testing": {
            "initial": "Required before initial HRP certification",
            "random": "At least once every 12 months (unpredictable selection)",
            "for_cause": "When involved in incident, unsafe practice, or based on reasonable suspicion",
            "post_incident": "Following any safety-significant incident",
            "return_to_duty": "Before returning to HRP duties after treatment",
            "follow_up": "After return to duty, unannounced testing for specified period",
        },
        "testing_method": "Breath alcohol test using evidential breath testing (EBT) device",
        "thresholds": {
            "zero_tolerance": {
                "bac": "Below 0.02%",
                "result": "Negative - no action required",
            },
            "concern_level": {
                "bac": "0.02% to 0.039%",
                "result": "Requires evaluation, temporary removal until BAC below 0.02%",
            },
            "positive_level": {
                "bac": "0.04% or higher",
                "result": "Positive test - immediate temporary removal, evaluation required",
            },
        },
        "consequences_of_positive": [
            "Immediate temporary removal from HRP duties",
            "Evaluation by Designated Physician",
            "Assessment for alcohol use disorder",
            "Potential referral to Employee Assistance Program",
            "Possible permanent removal from HRP",
        ],
        "return_to_duty_requirements": [
            "Completion of recommended treatment",
            "Evaluation by Substance Abuse Professional",
            "Negative return-to-duty test",
            "Follow-up testing schedule",
            "Demonstrated reliability for HRP duties",
        ],
    }


@mcp.tool()
@audit_log
async def get_testing_frequency() -> dict[str, Any]:
    """
    Get information about HRP testing frequency requirements.

    Retrieve details about how often HRP-certified individuals are
    subject to random drug and alcohol testing.

    Returns:
        Testing frequency information including:
        - random_testing_rate: Required random testing frequency
        - selection_process: How individuals are selected
        - testing_pool: How the testing pool is managed
        - section: CFR section reference
    """
    return {
        "section": "712.15",
        "citation": "10 CFR 712.15",
        "title": "Testing frequency requirements",
        "random_testing_rate": {
            "drug_testing": "At least once every 12 months from previous test",
            "alcohol_testing": "At least once every 12 months from previous test",
            "note": "Sites may test more frequently based on site-specific requirements",
        },
        "selection_process": {
            "method": "Random selection using scientifically valid method",
            "unpredictability": "Selection must be unpredictable and provide equal probability",
            "timing": "Testing may occur at any time during work hours",
            "notice": "Minimal advance notice to prevent evasion",
        },
        "testing_pool": {
            "composition": "All HRP-certified individuals at the site",
            "management": "Pool managed by site HRP administration",
            "confidentiality": "Selection information kept confidential",
        },
        "special_circumstances": {
            "for_cause": "Testing required when reasonable suspicion exists",
            "post_incident": "Testing required after safety-significant incidents",
            "follow_up": "Enhanced testing frequency after return to duty",
        },
    }


@mcp.tool()
@audit_log
async def get_substance_list() -> dict[str, Any]:
    """
    Get the list of controlled substances tested in HRP drug testing.

    Retrieve the specific substances included in HRP drug testing panels
    with cutoff levels.

    Returns:
        Substance list including:
        - substances: List of substances with categories and cutoff levels
        - testing_standard: Reference to testing standards used
        - section: CFR section reference
    """
    return {
        "section": "712.15",
        "citation": "10 CFR 712.15",
        "title": "Controlled substances tested",
        "substances": CONTROLLED_SUBSTANCES,
        "testing_standard": "Testing follows HHS Mandatory Guidelines for Federal Workplace Drug Testing Programs",
        "cutoff_levels": {
            "initial_screening": "Immunoassay screening at specified cutoff levels",
            "confirmatory_testing": "GC/MS confirmation at specified cutoff levels for positive screens",
        },
        "important_notes": [
            "Prescription medications may explain positive results but must be evaluated",
            "CBD products may cause positive THC results",
            "Medical Review Officer reviews all positive results before reporting",
            "Dilute specimens may require retesting",
        ],
    }
