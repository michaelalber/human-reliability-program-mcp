"""HRP-specific Pydantic models for Human Reliability Program data."""

from enum import Enum

from pydantic import BaseModel, Field


class HRPPositionType(str, Enum):
    """Types of HRP positions per 10 CFR 712.10."""

    CATEGORY_I_SNM = "category_i_snm"
    NUCLEAR_EXPLOSIVE = "nuclear_explosive"
    NUCLEAR_EXPLOSIVE_DUTY = "nuclear_explosive_duty"
    HRP_DESIGNATED = "hrp_designated"


class CertificationStatus(str, Enum):
    """HRP certification status."""

    CERTIFIED = "certified"
    PENDING = "pending"
    TEMPORARILY_REMOVED = "temporarily_removed"
    PERMANENTLY_REMOVED = "permanently_removed"
    REINSTATED = "reinstated"


class RemovalType(str, Enum):
    """Types of HRP removal."""

    TEMPORARY = "temporary"
    PERMANENT = "permanent"


class DisqualifyingCategory(str, Enum):
    """Categories of disqualifying factors."""

    SUBSTANCE = "substance"
    MEDICAL = "medical"
    PSYCHOLOGICAL = "psychological"
    BEHAVIORAL = "behavioral"
    SECURITY = "security"


class TestType(str, Enum):
    """Types of HRP testing."""

    DRUG = "drug"
    ALCOHOL = "alcohol"


class HRPRole(str, Enum):
    """Official HRP roles."""

    HRP_CERTIFYING_OFFICIAL = "hrp_certifying_official"
    HRP_MANAGEMENT_OFFICIAL = "hrp_management_official"
    DESIGNATED_PHYSICIAN = "designated_physician"
    DESIGNATED_PSYCHOLOGIST = "designated_psychologist"
    SUPERVISOR = "supervisor"
    MEDICAL_REVIEW_OFFICER = "medical_review_officer"


class PositionTypeInfo(BaseModel):
    """Information about an HRP position type."""

    position_type: HRPPositionType = Field(..., description="Position type enum")
    title: str = Field(..., description="Position type title")
    description: str = Field(..., description="Description of the position type")
    section: str = Field(..., description="CFR section reference")
    access_type: str = Field(..., description="Type of access this position provides")
    requirements: list[str] = Field(
        default_factory=list,
        description="Specific requirements for this position type",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "position_type": self.position_type.value,
            "title": self.title,
            "description": self.description,
            "section": self.section,
            "access_type": self.access_type,
            "requirements": self.requirements,
        }


class CertificationRequirement(BaseModel):
    """A certification requirement for HRP."""

    name: str = Field(..., description="Requirement name")
    description: str = Field(..., description="Detailed description")
    section: str = Field(..., description="CFR section reference")
    frequency: str = Field(default="", description="How often required (initial, annual, etc.)")
    responsible_party: str = Field(default="", description="Who is responsible for this")

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "name": self.name,
            "description": self.description,
            "section": self.section,
            "frequency": self.frequency,
            "responsible_party": self.responsible_party,
        }


class CertificationComponent(BaseModel):
    """One of the four annual certification components."""

    name: str = Field(..., description="Component name")
    description: str = Field(..., description="Component description")
    section: str = Field(..., description="CFR section reference")
    frequency: str = Field(..., description="Required frequency")
    responsible_official: str = Field(..., description="Official responsible for component")
    key_elements: list[str] = Field(
        default_factory=list,
        description="Key elements of this component",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "name": self.name,
            "description": self.description,
            "section": self.section,
            "frequency": self.frequency,
            "responsible_official": self.responsible_official,
            "key_elements": self.key_elements,
        }


class DisqualifyingFactor(BaseModel):
    """A factor that may disqualify an individual from HRP."""

    name: str = Field(..., description="Factor name")
    description: str = Field(..., description="Description of the disqualifying condition")
    category: DisqualifyingCategory = Field(..., description="Category of factor")
    section: str = Field(..., description="CFR section reference")
    is_absolute: bool = Field(
        default=False,
        description="Whether this is an absolute disqualifier vs. requires evaluation",
    )
    evaluation_guidance: str = Field(
        default="",
        description="Guidance on how this factor is evaluated",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "section": self.section,
            "is_absolute": self.is_absolute,
            "evaluation_guidance": self.evaluation_guidance,
        }


class MedicalStandard(BaseModel):
    """A medical standard from Subpart B."""

    name: str = Field(..., description="Standard name")
    description: str = Field(..., description="Description of the standard")
    section: str = Field(..., description="CFR section reference")
    category: str = Field(default="", description="Category (physical, psychological, etc.)")
    conditions: list[str] = Field(
        default_factory=list,
        description="Conditions addressed by this standard",
    )
    evaluation_criteria: list[str] = Field(
        default_factory=list,
        description="Criteria for evaluation",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "name": self.name,
            "description": self.description,
            "section": self.section,
            "category": self.category,
            "conditions": self.conditions,
            "evaluation_criteria": self.evaluation_criteria,
        }


class TestingRequirement(BaseModel):
    """Drug or alcohol testing requirement."""

    test_type: TestType = Field(..., description="Type of test")
    description: str = Field(..., description="Description of the requirement")
    section: str = Field(..., description="CFR section reference")
    timing: str = Field(..., description="When testing is required")
    frequency: str = Field(default="", description="How often for random testing")
    threshold: str = Field(default="", description="Threshold for positive result, if applicable")
    substances: list[str] = Field(
        default_factory=list,
        description="Substances tested for",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "test_type": self.test_type.value,
            "description": self.description,
            "section": self.section,
            "timing": self.timing,
            "frequency": self.frequency,
            "threshold": self.threshold,
            "substances": self.substances,
        }


class RemovalProcess(BaseModel):
    """Process for temporary or permanent removal from HRP."""

    removal_type: RemovalType = Field(..., description="Type of removal")
    description: str = Field(..., description="Description of the process")
    section: str = Field(..., description="CFR section reference")
    grounds: list[str] = Field(
        default_factory=list,
        description="Grounds for this type of removal",
    )
    procedures: list[str] = Field(
        default_factory=list,
        description="Steps in the removal process",
    )
    notification_requirements: str = Field(
        default="",
        description="Notification requirements",
    )
    appeal_rights: str = Field(
        default="",
        description="Appeal rights for the individual",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "removal_type": self.removal_type.value,
            "description": self.description,
            "section": self.section,
            "grounds": self.grounds,
            "procedures": self.procedures,
            "notification_requirements": self.notification_requirements,
            "appeal_rights": self.appeal_rights,
        }


class ReinstatementProcess(BaseModel):
    """Process for reinstatement to HRP."""

    description: str = Field(..., description="Description of the reinstatement process")
    section: str = Field(..., description="CFR section reference")
    eligibility_criteria: list[str] = Field(
        default_factory=list,
        description="Criteria for eligibility to seek reinstatement",
    )
    procedures: list[str] = Field(
        default_factory=list,
        description="Steps in the reinstatement process",
    )
    required_evaluations: list[str] = Field(
        default_factory=list,
        description="Evaluations required for reinstatement",
    )
    decision_authority: str = Field(
        default="",
        description="Who makes the reinstatement decision",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "description": self.description,
            "section": self.section,
            "eligibility_criteria": self.eligibility_criteria,
            "procedures": self.procedures,
            "required_evaluations": self.required_evaluations,
            "decision_authority": self.decision_authority,
        }


class AppealProcess(BaseModel):
    """Administrative review and appeal process."""

    stage: str = Field(..., description="Stage of appeal (reconsideration, administrative review)")
    description: str = Field(..., description="Description of this appeal stage")
    section: str = Field(..., description="CFR section reference")
    timeframe: str = Field(default="", description="Timeframe for this stage")
    procedures: list[str] = Field(
        default_factory=list,
        description="Steps in the appeal process",
    )
    decision_authority: str = Field(
        default="",
        description="Who makes the decision at this stage",
    )
    next_stage: str = Field(
        default="",
        description="Next stage of appeal if denied",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "stage": self.stage,
            "description": self.description,
            "section": self.section,
            "timeframe": self.timeframe,
            "procedures": self.procedures,
            "decision_authority": self.decision_authority,
            "next_stage": self.next_stage,
        }


class HRPRoleInfo(BaseModel):
    """Information about an HRP official role."""

    role: HRPRole = Field(..., description="Role enum")
    title: str = Field(..., description="Official title")
    description: str = Field(..., description="Description of the role")
    responsibilities: list[str] = Field(
        default_factory=list,
        description="Key responsibilities",
    )
    qualifications: list[str] = Field(
        default_factory=list,
        description="Qualifications for the role",
    )
    section: str = Field(default="", description="CFR section reference")

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP tool response."""
        return {
            "role": self.role.value,
            "title": self.title,
            "description": self.description,
            "responsibilities": self.responsibilities,
            "qualifications": self.qualifications,
            "section": self.section,
        }
