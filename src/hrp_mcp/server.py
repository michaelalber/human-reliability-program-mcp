"""Human Reliability Program MCP Server - 10 CFR Part 712 access."""

import logging

from fastmcp import FastMCP

from hrp_mcp.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

mcp = FastMCP(
    "hrp-mcp",
    instructions="""
    Human Reliability Program (HRP) MCP Server for DOE/NNSA sites.

    This server provides tools for 10 CFR Part 712 - Human Reliability Program:

    **Regulation Search:**
    - search_10cfr712: Semantic search across all HRP regulations
    - get_section: Get specific section text (e.g., 712.11)
    - get_subpart: Get all sections in Subpart A or B
    - explain_term: Look up HRP definitions from 712.3

    **Certification:**
    - get_certification_requirements: Initial certification requirements
    - get_recertification_requirements: Annual recertification requirements
    - check_disqualifying_factors: Evaluate potential disqualifying conditions
    - get_hrp_position_types: Types of HRP positions (712.10)

    **Medical Standards (Subpart B):**
    - get_medical_standards: Medical requirements for HRP
    - get_psychological_evaluation: Psychological evaluation criteria
    - check_medical_condition: Evaluate conditions against HRP standards
    - get_designated_physician_role: Designated Physician responsibilities

    **Drug & Alcohol Testing:**
    - get_drug_testing_requirements: Drug testing procedures (712.15)
    - get_alcohol_testing_requirements: Alcohol testing procedures
    - get_testing_frequency: Random testing requirements
    - get_substance_list: Controlled substances tested

    **Procedures:**
    - get_temporary_removal_process: Temporary removal (712.19)
    - get_permanent_removal_process: Permanent removal (712.20)
    - get_reinstatement_process: Reinstatement procedures (712.21)
    - get_appeal_process: Administrative review and appeals (712.22-712.25)
    - get_hrp_roles: Official HRP roles and responsibilities
    - get_supervisory_review: Supervisory review requirements (712.14)
    - get_management_evaluation: Management evaluation process (712.16)
    - get_security_review: DOE security review requirements (712.17)

    All queries are logged for audit purposes. This server provides
    informational guidance only - all HRP determinations must be made
    by authorized HRP officials per site-specific procedures.

    For official guidance, consult your site's HRP Management Official
    or the applicable DOE Order.
    """,
)

# Import tools to register them with FastMCP via @mcp.tool() decorators
# These imports must happen after mcp is defined
from hrp_mcp.tools import (  # noqa: E402
    certification,  # noqa: F401
    medical,  # noqa: F401
    procedures,  # noqa: F401
    regulations,  # noqa: F401
    testing,  # noqa: F401
)


def main() -> None:
    """Run the MCP server with configured transport."""
    transport = settings.mcp_transport

    if transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            host=settings.mcp_host,
            port=settings.mcp_port,
        )
    elif transport == "sse":
        mcp.run(
            transport="sse",
            host=settings.mcp_host,
            port=settings.mcp_port,
        )
    else:
        # Default: stdio for Claude Desktop integration
        mcp.run()


if __name__ == "__main__":
    main()
