"""Procedural tools for HRP MCP.

Provides tools for HRP removal, reinstatement, appeals, and administrative procedures.
"""

from hrp_mcp.audit import audit_log
from hrp_mcp.resources.reference_data import (
    CERTIFICATION_COMPONENTS,
    HRP_ROLES,
)
from hrp_mcp.server import mcp


@mcp.tool()
@audit_log
async def get_temporary_removal_process() -> dict:
    """
    Get the temporary removal process per 10 CFR 712.19.

    Retrieve information about when and how individuals are temporarily
    removed from HRP duties.

    Returns:
        Temporary removal information including:
        - grounds: Grounds for temporary removal
        - procedures: Steps in the removal process
        - individual_rights: Rights of the removed individual
        - resolution: How temporary removals are resolved
        - section: CFR section reference
    """
    return {
        "section": "712.19",
        "citation": "10 CFR 712.19",
        "title": "Temporary removal from HRP",
        "definition": "Immediate removal from HRP duties when a safety or security concern is identified, pending resolution.",
        "grounds": [
            "Safety concern identified",
            "Security concern identified",
            "Positive drug or alcohol test",
            "Reported behavior of concern",
            "Medical condition affecting reliability",
            "Pending investigation",
            "Request by individual",
        ],
        "authority": "HRP Management Official or designee may order temporary removal",
        "procedures": [
            "Immediate removal from HRP duties",
            "Notification to individual of basis for removal",
            "Assignment to non-HRP duties if available",
            "Investigation or evaluation initiated",
            "Regular status updates to individual",
            "Resolution within reasonable timeframe",
        ],
        "individual_rights": [
            "Notification of reason for removal",
            "Opportunity to respond to concerns",
            "Right to request reconsideration",
            "Pay and benefits generally continue",
            "Representation rights",
        ],
        "resolution_options": [
            "Reinstatement to HRP duties if concern resolved",
            "Permanent removal if concern substantiated and serious",
            "Voluntary withdrawal from HRP",
            "Transfer to non-HRP position",
        ],
        "timeframe": "Should be resolved as expeditiously as possible",
    }


@mcp.tool()
@audit_log
async def get_permanent_removal_process() -> dict:
    """
    Get the permanent removal process per 10 CFR 712.20.

    Retrieve information about permanent removal (revocation) from HRP.

    Returns:
        Permanent removal information including:
        - grounds: Grounds for permanent removal
        - procedures: Steps in the removal process
        - individual_rights: Rights of the removed individual
        - consequences: Consequences of permanent removal
        - section: CFR section reference
    """
    return {
        "section": "712.20",
        "citation": "10 CFR 712.20",
        "title": "Removal from HRP",
        "definition": "Permanent revocation of HRP certification.",
        "grounds": [
            "Substantiated safety or security concern",
            "Disqualifying medical or psychological condition",
            "Positive drug test (verified)",
            "Repeated positive alcohol tests",
            "Hallucinogen use within 5 years",
            "Failure to meet recertification requirements",
            "Dishonesty or integrity concerns",
            "Pattern of unreliable behavior",
            "Refusal to comply with HRP requirements",
        ],
        "authority": "HRP Certifying Official makes permanent removal decisions",
        "procedures": [
            "Review of all relevant information",
            "Consideration of individual's response",
            "Written notification of proposed removal",
            "Opportunity to respond before final decision",
            "Final decision by Certifying Official",
            "Written notification of final decision",
            "Information about appeal rights",
        ],
        "individual_rights": [
            "Written notice of proposed removal",
            "Access to information relied upon (subject to classification)",
            "Opportunity to respond in writing",
            "Opportunity for in-person discussion",
            "Right to representation",
            "Right to appeal",
        ],
        "consequences": [
            "Loss of HRP certification",
            "Removal from HRP position",
            "Potential impact on security clearance",
            "Transfer to non-HRP position if available",
            "Record in HRP personnel file",
        ],
        "appeal_rights": "Individual may request reconsideration per 712.22 and administrative review per 712.23",
    }


@mcp.tool()
@audit_log
async def get_reinstatement_process() -> dict:
    """
    Get the reinstatement process per 10 CFR 712.21.

    Retrieve information about how individuals may be reinstated to HRP
    after removal.

    Returns:
        Reinstatement information including:
        - eligibility: Who may seek reinstatement
        - requirements: Requirements for reinstatement
        - procedures: Steps in the reinstatement process
        - section: CFR section reference
    """
    return {
        "section": "712.21",
        "citation": "10 CFR 712.21",
        "title": "Reinstatement",
        "definition": "Process for returning to HRP certification after temporary or permanent removal.",
        "eligibility": [
            "Individuals temporarily removed whose concern is resolved",
            "Individuals who successfully appeal removal",
            "Individuals who complete required treatment/rehabilitation",
            "Individuals whose circumstances have changed",
        ],
        "requirements": [
            "Resolution of the issue that led to removal",
            "Successful completion of any required treatment",
            "New medical and/or psychological evaluation",
            "Supervisory recommendation",
            "Management evaluation",
            "Security review (if applicable)",
            "Demonstrated reliability",
        ],
        "for_substance_issues": [
            "Completion of treatment program",
            "Evaluation by Substance Abuse Professional",
            "Negative return-to-duty drug/alcohol test",
            "Agreement to follow-up testing program",
            "Demonstrated period of sobriety/recovery",
        ],
        "procedures": [
            "Request for reinstatement submitted",
            "Evaluation of circumstances and resolution",
            "Required evaluations completed",
            "Review by HRP Management Official",
            "Decision by Certifying Official",
            "Written notification of decision",
        ],
        "decision_authority": "HRP Certifying Official",
        "note": "Reinstatement is not guaranteed and depends on individual circumstances and site needs.",
    }


@mcp.tool()
@audit_log
async def get_appeal_process() -> dict:
    """
    Get the administrative review and appeal process per 10 CFR 712.22-712.25.

    Retrieve information about how individuals may appeal HRP decisions.

    Returns:
        Appeal process information including:
        - stages: Different stages of appeal
        - timeframes: Time limits for appeals
        - procedures: Steps at each stage
        - section: CFR section references
    """
    return {
        "title": "Administrative Review and Appeal Process",
        "stages": [
            {
                "stage": "Request for Reconsideration",
                "section": "712.22",
                "citation": "10 CFR 712.22",
                "description": "Initial request to the Certifying Official to reconsider a decision",
                "timeframe": "Submit within 10 business days of receiving removal notification",
                "decision_authority": "HRP Certifying Official",
                "procedures": [
                    "Submit written request for reconsideration",
                    "Include any new information or arguments",
                    "Certifying Official reviews request",
                    "Written response issued",
                ],
            },
            {
                "stage": "Administrative Review",
                "section": "712.23",
                "citation": "10 CFR 712.23",
                "description": "Review by HRP Management Official if reconsideration denied",
                "timeframe": "Submit within 10 business days of reconsideration denial",
                "decision_authority": "HRP Management Official",
                "procedures": [
                    "Submit written request for administrative review",
                    "Management Official reviews record",
                    "May request additional information",
                    "Written decision issued",
                ],
            },
            {
                "stage": "Administrative Judge Hearing",
                "section": "712.24",
                "citation": "10 CFR 712.24",
                "description": "Formal hearing before DOE Administrative Judge",
                "timeframe": "Request within 20 business days of administrative review denial",
                "decision_authority": "DOE Office of Hearings and Appeals Administrative Judge",
                "procedures": [
                    "File request with DOE Office of Hearings and Appeals",
                    "Administrative Judge assigned",
                    "Prehearing conference",
                    "Formal hearing conducted",
                    "Written decision issued",
                ],
            },
            {
                "stage": "Secretary Review",
                "section": "712.25",
                "citation": "10 CFR 712.25",
                "description": "Final review by Secretary of Energy",
                "timeframe": "Request within 30 calendar days of Administrative Judge decision",
                "decision_authority": "Secretary of Energy (or designee)",
                "procedures": [
                    "Submit appeal to Secretary",
                    "Secretary reviews record",
                    "May affirm, reverse, or modify",
                    "Final agency decision",
                ],
            },
        ],
        "individual_rights": [
            "Right to representation at all stages",
            "Access to information relied upon (subject to classification)",
            "Right to present evidence and arguments",
            "Right to written decisions with rationale",
        ],
        "note": "Timeframes are critical - missing deadlines may result in waiver of appeal rights.",
    }


@mcp.tool()
@audit_log
async def get_hrp_roles() -> dict:
    """
    Get information about HRP official roles.

    Retrieve details about the various official roles in the HRP
    and their responsibilities.

    Returns:
        HRP roles information including:
        - roles: List of HRP roles with responsibilities
    """
    roles = []
    for role_info in HRP_ROLES.values():
        roles.append(role_info.to_dict())

    return {
        "title": "HRP Official Roles",
        "roles": roles,
        "note": "Specific responsibilities may vary by site. Consult local HRP procedures for site-specific information.",
    }


@mcp.tool()
@audit_log
async def get_supervisory_review() -> dict:
    """
    Get supervisory review requirements per 10 CFR 712.14.

    Retrieve information about the supervisory review component of HRP.

    Returns:
        Supervisory review information including:
        - purpose: Purpose of supervisory review
        - responsibilities: Supervisor responsibilities
        - what_to_observe: What supervisors should observe
        - reporting: How concerns should be reported
        - section: CFR section reference
    """
    comp = CERTIFICATION_COMPONENTS.get("supervisory_review")

    return {
        "section": "712.14",
        "citation": "10 CFR 712.14",
        "title": "Supervisory review",
        "purpose": "Ongoing observation and evaluation to identify reliability concerns",
        "frequency": comp.frequency if comp else "Continuous (documented at least annually)",
        "responsible_official": "Immediate Supervisor",
        "responsibilities": [
            "Continuous observation of job performance",
            "Monitoring behavior and demeanor",
            "Identifying potential safety or security concerns",
            "Documenting observations",
            "Reporting concerns to HRP management",
            "Annual supervisory review assessment",
        ],
        "what_to_observe": [
            "Job performance quality and consistency",
            "Attendance and punctuality",
            "Interaction with coworkers",
            "Compliance with rules and procedures",
            "Response to stress or pressure",
            "Any concerning behavior changes",
            "Signs of substance use or impairment",
        ],
        "reporting_requirements": [
            "Report safety concerns immediately to HRP management",
            "Report security concerns immediately to security",
            "Document significant observations",
            "Complete annual supervisory review form",
        ],
        "training": "Supervisors must receive training on HRP supervisory responsibilities",
    }


@mcp.tool()
@audit_log
async def get_management_evaluation() -> dict:
    """
    Get management evaluation requirements per 10 CFR 712.16.

    Retrieve information about the management evaluation component of HRP.

    Returns:
        Management evaluation information including:
        - purpose: Purpose of management evaluation
        - what_is_reviewed: Information reviewed in evaluation
        - outcome: Possible outcomes
        - section: CFR section reference
    """
    comp = CERTIFICATION_COMPONENTS.get("management_evaluation")

    return {
        "section": "712.16",
        "citation": "10 CFR 712.16",
        "title": "Management evaluation",
        "purpose": "Holistic review of all reliability factors to determine certification eligibility",
        "frequency": comp.frequency if comp else "Annual",
        "responsible_official": "HRP Management Official",
        "what_is_reviewed": [
            "Supervisory review findings and recommendations",
            "Medical assessment results",
            "Psychological evaluation results (if conducted)",
            "Drug and alcohol testing results",
            "DOE security review findings",
            "Any incidents or concerns during the period",
            "Overall reliability pattern",
        ],
        "evaluation_factors": [
            "Reliability indicators from all components",
            "Resolution of any identified concerns",
            "Overall fitness for HRP duties",
            "Recommendation from Designated Physician",
            "Supervisor recommendation",
        ],
        "outcomes": [
            "Recommendation for certification/recertification",
            "Request for additional information or evaluation",
            "Temporary removal pending resolution of concerns",
            "Recommendation against certification",
        ],
        "decision": "Final certification decision made by HRP Certifying Official",
    }


@mcp.tool()
@audit_log
async def get_security_review() -> dict:
    """
    Get DOE security review requirements per 10 CFR 712.17.

    Retrieve information about the DOE personnel security review component.

    Returns:
        Security review information including:
        - purpose: Purpose of security review
        - what_is_reviewed: Information reviewed
        - relationship_to_clearance: Relationship to security clearance
        - section: CFR section reference
    """
    comp = CERTIFICATION_COMPONENTS.get("security_review")

    return {
        "section": "712.17",
        "citation": "10 CFR 712.17",
        "title": "DOE security review",
        "purpose": "Personnel security determination based on security-related information",
        "frequency": comp.frequency if comp else "Annual",
        "responsible_official": "DOE Security Personnel",
        "what_is_reviewed": [
            "Security clearance status and any issues",
            "Security incidents or violations",
            "Foreign contacts and travel",
            "Financial concerns",
            "Criminal history updates",
            "Counterintelligence information",
            "Any other security-relevant information",
        ],
        "relationship_to_clearance": {
            "clearance_required": "HRP certification requires appropriate DOE security clearance",
            "hrp_additional": "HRP security review is in addition to clearance requirements",
            "clearance_issues": "Clearance issues may affect HRP certification",
        },
        "counterintelligence": {
            "when_required": "For designated positions under 10 CFR Part 709",
            "may_include": "Polygraph examination",
        },
        "outcome": "Security determination provided to HRP management for certification decision",
    }
