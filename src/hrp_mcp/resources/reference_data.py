"""Reference data for HRP regulations and terminology.

Contains static reference data from 10 CFR Part 712 including:
- Definitions (712.3)
- Position types (712.10)
- Section information
- Certification components
- Disqualifying factors
- Controlled substances
- HRP roles
- Medical standards
"""

from hrp_mcp.models.hrp import (
    CertificationComponent,
    DisqualifyingCategory,
    DisqualifyingFactor,
    HRPPositionType,
    HRPRole,
    HRPRoleInfo,
    MedicalStandard,
    PositionTypeInfo,
)

# =============================================================================
# HRP DEFINITIONS (10 CFR 712.3)
# =============================================================================

HRP_DEFINITIONS: dict[str, dict] = {
    "access": {
        "term": "Access",
        "definition": "(1) A situation that may provide an individual proximity to or control over Category I special nuclear material (SNM); or (2) The proximity to a nuclear explosive and/or Category I SNM that allows the opportunity to divert, steal, tamper with, and/or damage the nuclear explosive or material in spite of any controls that have been established to prevent such unauthorized actions.",
        "section": "712.3",
    },
    "alcohol": {
        "term": "Alcohol",
        "definition": "The intoxicating agent in beverage alcohol, ethyl alcohol or other low molecular weight alcohols, including methyl or isopropyl alcohol.",
        "section": "712.3",
    },
    "alcohol_use_disorder": {
        "term": "Alcohol Use Disorder",
        "definition": "A problematic pattern of alcohol use leading to clinically significant impairment or distress, as manifested by at least 2 of 11 specific criteria occurring within a 12-month period, as defined in the DSM-5.",
        "section": "712.3",
    },
    "certifying_official": {
        "term": "Certifying Official",
        "definition": "The individual, appointed by the HRP management official, who has final authority to approve certification or recertification of an individual for HRP duties.",
        "section": "712.3",
    },
    "critical_position": {
        "term": "Critical Position",
        "definition": "A position that requires a nuclear explosive safety study or formal safety review and has the potential to significantly affect nuclear explosive operations or the safety of Category I SNM.",
        "section": "712.3",
    },
    "designated_physician": {
        "term": "Designated Physician",
        "definition": "A physician who is designated by the HRP management official to provide medical evaluations of HRP candidates and HRP-certified individuals.",
        "section": "712.3",
    },
    "designated_psychologist": {
        "term": "Designated Psychologist",
        "definition": "A psychologist who is designated by the HRP management official to provide psychological evaluations of HRP candidates and HRP-certified individuals.",
        "section": "712.3",
    },
    "human_reliability_program": {
        "term": "Human Reliability Program (HRP)",
        "definition": "A security and safety reliability program designed to ensure that individuals with access to certain materials, nuclear explosive devices, facilities, and programs meet the highest standards of reliability and physical and mental suitability.",
        "section": "712.3",
    },
    "hrp_candidate": {
        "term": "HRP Candidate",
        "definition": "An individual who is being considered for assignment to an HRP position.",
        "section": "712.3",
    },
    "hrp_certified_individual": {
        "term": "HRP-Certified Individual",
        "definition": "An individual who is certified under the HRP.",
        "section": "712.3",
    },
    "hrp_management_official": {
        "term": "HRP Management Official",
        "definition": "The individual designated by the DOE or NNSA to manage the HRP at a DOE or NNSA site.",
        "section": "712.3",
    },
    "illegal_drug": {
        "term": "Illegal Drug",
        "definition": "A controlled substance as defined in 21 U.S.C. 802; illegal drugs include prescription drugs obtained without a valid prescription or used in a manner inconsistent with their prescribed use.",
        "section": "712.3",
    },
    "immediate_supervisor": {
        "term": "Immediate Supervisor",
        "definition": "The first-line supervisor who assigns, reviews, and approves the day-to-day work of an HRP candidate or HRP-certified individual.",
        "section": "712.3",
    },
    "job_task_analysis": {
        "term": "Job Task Analysis",
        "definition": "A formal process that identifies the physical and mental demands of an HRP position.",
        "section": "712.3",
    },
    "management_evaluation": {
        "term": "Management Evaluation",
        "definition": "An evaluation by the HRP management official based on a review of the results of the supervisory review, medical assessment, and drug and alcohol testing to determine if an individual should be certified or recertified.",
        "section": "712.3",
    },
    "medical_assessment": {
        "term": "Medical Assessment",
        "definition": "A medical evaluation that includes a physical examination, medical history, and psychological evaluation to determine an individual's physical and mental suitability for HRP certification.",
        "section": "712.3",
    },
    "nuclear_explosive": {
        "term": "Nuclear Explosive",
        "definition": "An assembly containing fissionable and/or fusionable materials and main charge high explosive parts or propellants capable of producing a nuclear detonation.",
        "section": "712.3",
    },
    "nuclear_explosive_duty": {
        "term": "Nuclear Explosive Duty",
        "definition": "Work assignments or responsibilities that afford access to a nuclear explosive or require the individual to perform or direct nuclear explosive operations.",
        "section": "712.3",
    },
    "random_testing": {
        "term": "Random Testing",
        "definition": "A testing process that results in unpredictable selection for testing.",
        "section": "712.3",
    },
    "recertification": {
        "term": "Recertification",
        "definition": "The process of reevaluating the continued suitability of an HRP-certified individual for HRP duties.",
        "section": "712.3",
    },
    "safety_concern": {
        "term": "Safety Concern",
        "definition": "Any condition or circumstance that may reasonably be expected to have an adverse effect on the reliability of an HRP-certified individual or HRP candidate to safely perform HRP duties.",
        "section": "712.3",
    },
    "security_concern": {
        "term": "Security Concern",
        "definition": "Any condition or circumstance that may reasonably be expected to have an adverse effect on the reliability of an HRP-certified individual or HRP candidate, as determined by an evaluation of security-related information.",
        "section": "712.3",
    },
    "substance_use_disorder": {
        "term": "Substance Use Disorder",
        "definition": "A problematic pattern of substance use leading to clinically significant impairment or distress, as defined in the DSM-5.",
        "section": "712.3",
    },
    "supervisory_review": {
        "term": "Supervisory Review",
        "definition": "An ongoing process of observation and evaluation of an HRP candidate or HRP-certified individual by the immediate supervisor and other designated officials.",
        "section": "712.3",
    },
    "temporary_removal": {
        "term": "Temporary Removal",
        "definition": "The action of immediately removing an HRP-certified individual from HRP duties when a safety or security concern is identified, pending resolution of the concern.",
        "section": "712.3",
    },
    "unsafe_practice": {
        "term": "Unsafe Practice",
        "definition": "Any intentional or unintentional act or omission that results in an uncontrolled, unplanned, or undesirable event, or series of events, that has the potential to adversely impact safety.",
        "section": "712.3",
    },
}

# =============================================================================
# HRP POSITION TYPES (10 CFR 712.10)
# =============================================================================

HRP_POSITION_TYPES: dict[str, PositionTypeInfo] = {
    "category_i_snm": PositionTypeInfo(
        position_type=HRPPositionType.CATEGORY_I_SNM,
        title="Category I Special Nuclear Material Access",
        description="Positions requiring access to Category I quantities of special nuclear material.",
        section="712.10(a)(1)",
        access_type="Category I SNM",
        requirements=[
            "DOE Q or L clearance",
            "Successful completion of HRP certification",
            "Annual recertification",
            "Random drug and alcohol testing",
        ],
    ),
    "nuclear_explosive": PositionTypeInfo(
        position_type=HRPPositionType.NUCLEAR_EXPLOSIVE,
        title="Nuclear Explosive Access",
        description="Positions requiring access to nuclear explosive devices.",
        section="712.10(a)(2)",
        access_type="Nuclear explosive devices",
        requirements=[
            "DOE Q clearance",
            "Successful completion of HRP certification",
            "Annual recertification",
            "Random drug and alcohol testing",
            "Additional nuclear explosive safety training",
        ],
    ),
    "nuclear_explosive_duty": PositionTypeInfo(
        position_type=HRPPositionType.NUCLEAR_EXPLOSIVE_DUTY,
        title="Nuclear Explosive Duty",
        description="Positions involving work assignments that afford access to nuclear explosives or require performance of nuclear explosive operations.",
        section="712.10(a)(3)",
        access_type="Nuclear explosive operations",
        requirements=[
            "DOE Q clearance",
            "Successful completion of HRP certification",
            "Annual recertification",
            "Random drug and alcohol testing",
            "Nuclear explosive duty-specific training",
            "Job task analysis completion",
        ],
    ),
    "hrp_designated": PositionTypeInfo(
        position_type=HRPPositionType.HRP_DESIGNATED,
        title="HRP-Designated Position",
        description="Other positions determined by DOE/NNSA to have significant impact on national security that warrant HRP requirements.",
        section="712.10(a)(4)",
        access_type="Varies by position designation",
        requirements=[
            "Appropriate DOE clearance",
            "Successful completion of HRP certification",
            "Annual recertification",
            "Random drug and alcohol testing",
        ],
    ),
}

# =============================================================================
# HRP SECTIONS (10 CFR 712)
# =============================================================================

HRP_SECTIONS: dict[str, dict] = {
    # Subpart A - Procedures
    "712.1": {
        "section": "712.1",
        "title": "Purpose",
        "subpart": "A",
        "description": "Establishes the purpose of the Human Reliability Program.",
    },
    "712.2": {
        "section": "712.2",
        "title": "Scope",
        "subpart": "A",
        "description": "Defines the scope and applicability of HRP requirements.",
    },
    "712.3": {
        "section": "712.3",
        "title": "Definitions",
        "subpart": "A",
        "description": "Provides definitions for terms used throughout Part 712.",
    },
    "712.10": {
        "section": "712.10",
        "title": "Designation of HRP positions",
        "subpart": "A",
        "description": "Specifies the types of positions that require HRP certification.",
    },
    "712.11": {
        "section": "712.11",
        "title": "General requirements for HRP certification",
        "subpart": "A",
        "description": "Lists the requirements for initial HRP certification.",
    },
    "712.12": {
        "section": "712.12",
        "title": "HRP recertification",
        "subpart": "A",
        "description": "Describes the annual recertification process and requirements.",
    },
    "712.13": {
        "section": "712.13",
        "title": "Medical assessment",
        "subpart": "A",
        "description": "Establishes medical assessment requirements for HRP.",
    },
    "712.14": {
        "section": "712.14",
        "title": "Supervisory review",
        "subpart": "A",
        "description": "Defines supervisory review responsibilities and procedures.",
    },
    "712.15": {
        "section": "712.15",
        "title": "Drug and alcohol testing",
        "subpart": "A",
        "description": "Establishes drug and alcohol testing requirements.",
    },
    "712.16": {
        "section": "712.16",
        "title": "Management evaluation",
        "subpart": "A",
        "description": "Describes the management evaluation process.",
    },
    "712.17": {
        "section": "712.17",
        "title": "DOE security review",
        "subpart": "A",
        "description": "Establishes DOE personnel security review requirements.",
    },
    "712.18": {
        "section": "712.18",
        "title": "Transferring HRP certification",
        "subpart": "A",
        "description": "Procedures for transferring HRP certification between sites.",
    },
    "712.19": {
        "section": "712.19",
        "title": "Temporary removal from HRP",
        "subpart": "A",
        "description": "Procedures for temporary removal from HRP duties.",
    },
    "712.20": {
        "section": "712.20",
        "title": "Removal from HRP",
        "subpart": "A",
        "description": "Procedures for permanent removal from HRP.",
    },
    "712.21": {
        "section": "712.21",
        "title": "Reinstatement",
        "subpart": "A",
        "description": "Requirements and procedures for reinstatement to HRP.",
    },
    "712.22": {
        "section": "712.22",
        "title": "Request for reconsideration",
        "subpart": "A",
        "description": "Process for requesting reconsideration of HRP decisions.",
    },
    "712.23": {
        "section": "712.23",
        "title": "Administrative review",
        "subpart": "A",
        "description": "Administrative review procedures.",
    },
    "712.24": {
        "section": "712.24",
        "title": "Administrative Judge",
        "subpart": "A",
        "description": "Role and procedures for Administrative Judge hearings.",
    },
    "712.25": {
        "section": "712.25",
        "title": "Secretary review",
        "subpart": "A",
        "description": "Secretary of Energy review procedures.",
    },
    # Subpart B - Medical Standards
    "712.30": {
        "section": "712.30",
        "title": "Medical standards - general",
        "subpart": "B",
        "description": "General medical standards for HRP.",
    },
    "712.31": {
        "section": "712.31",
        "title": "Application of medical standards",
        "subpart": "B",
        "description": "How medical standards are applied.",
    },
    "712.32": {
        "section": "712.32",
        "title": "Physical examination",
        "subpart": "B",
        "description": "Physical examination requirements.",
    },
    "712.33": {
        "section": "712.33",
        "title": "Designated Physician",
        "subpart": "B",
        "description": "Designated Physician responsibilities and qualifications.",
    },
    "712.34": {
        "section": "712.34",
        "title": "Psychological evaluation",
        "subpart": "B",
        "description": "Psychological evaluation requirements and procedures.",
    },
    "712.35": {
        "section": "712.35",
        "title": "Return to work evaluation",
        "subpart": "B",
        "description": "Requirements for return to work after medical issue.",
    },
    "712.36": {
        "section": "712.36",
        "title": "Medical disqualification",
        "subpart": "B",
        "description": "Criteria and procedures for medical disqualification.",
    },
    "712.37": {
        "section": "712.37",
        "title": "Medical removal protection",
        "subpart": "B",
        "description": "Protections for individuals removed for medical reasons.",
    },
    "712.38": {
        "section": "712.38",
        "title": "Medical records",
        "subpart": "B",
        "description": "Medical record retention and access requirements.",
    },
}

# =============================================================================
# CERTIFICATION COMPONENTS (Four Annual Components)
# =============================================================================

CERTIFICATION_COMPONENTS: dict[str, CertificationComponent] = {
    "supervisory_review": CertificationComponent(
        name="Supervisory Review",
        description="Ongoing behavioral observation and reporting by immediate supervisors to identify reliability concerns.",
        section="712.14",
        frequency="Continuous (documented at least annually)",
        responsible_official="Immediate Supervisor",
        key_elements=[
            "Observation of job performance",
            "Observation of behavior and demeanor",
            "Reporting of safety or security concerns",
            "Documentation of unusual incidents",
            "Assessment of reliability indicators",
        ],
    ),
    "medical_assessment": CertificationComponent(
        name="Medical Assessment",
        description="Physical and psychological evaluation by the Designated Physician to determine medical suitability.",
        section="712.13",
        frequency="Annual",
        responsible_official="Designated Physician",
        key_elements=[
            "Physical examination",
            "Medical history review",
            "Psychological evaluation (if indicated)",
            "Review of current medications",
            "Assessment of fitness for duty",
            "Job task analysis review",
        ],
    ),
    "management_evaluation": CertificationComponent(
        name="Management Evaluation",
        description="Holistic review by HRP management to evaluate overall reliability based on all components.",
        section="712.16",
        frequency="Annual",
        responsible_official="HRP Management Official",
        key_elements=[
            "Review of supervisory review findings",
            "Review of medical assessment results",
            "Review of drug and alcohol testing results",
            "Review of security review findings",
            "Overall reliability determination",
            "Certification or recertification decision",
        ],
    ),
    "security_review": CertificationComponent(
        name="DOE Security Review",
        description="Personnel security determination by DOE security personnel based on security-related information.",
        section="712.17",
        frequency="Annual",
        responsible_official="DOE Security Personnel",
        key_elements=[
            "Review of security clearance status",
            "Evaluation of security incidents",
            "Assessment of foreign contacts",
            "Review of criminal history updates",
            "Counterintelligence evaluation (if required)",
        ],
    ),
}

# =============================================================================
# DISQUALIFYING FACTORS
# =============================================================================

DISQUALIFYING_FACTORS: dict[str, DisqualifyingFactor] = {
    "hallucinogen_use": DisqualifyingFactor(
        name="Hallucinogen Use",
        description="Use of any hallucinogen within the preceding 5 years.",
        category=DisqualifyingCategory.SUBSTANCE,
        section="712.13(c)",
        is_absolute=True,
        evaluation_guidance="Any use of hallucinogens (LSD, psilocybin, mescaline, etc.) within 5 years is disqualifying. No exceptions.",
    ),
    "hallucinogen_flashback": DisqualifyingFactor(
        name="Hallucinogen Flashback",
        description="Experience of flashback resulting from hallucinogen use more than 5 years before applying.",
        category=DisqualifyingCategory.SUBSTANCE,
        section="712.13(c)",
        is_absolute=True,
        evaluation_guidance="Flashbacks from prior hallucinogen use are disqualifying regardless of when use occurred.",
    ),
    "drug_test_positive": DisqualifyingFactor(
        name="Positive Drug Test",
        description="Positive result on any drug test while in HRP or during certification process.",
        category=DisqualifyingCategory.SUBSTANCE,
        section="712.15",
        is_absolute=False,
        evaluation_guidance="Positive drug test results require medical review and may result in temporary or permanent removal.",
    ),
    "alcohol_test_positive": DisqualifyingFactor(
        name="Positive Alcohol Test",
        description="Blood alcohol concentration at or above the cutoff level.",
        category=DisqualifyingCategory.SUBSTANCE,
        section="712.15",
        is_absolute=False,
        evaluation_guidance="BAC at or above 0.02% during random testing requires evaluation. BAC at or above 0.04% may result in removal.",
    ),
    "substance_use_disorder": DisqualifyingFactor(
        name="Substance Use Disorder",
        description="Diagnosis of a substance use disorder that could affect reliability.",
        category=DisqualifyingCategory.MEDICAL,
        section="712.13",
        is_absolute=False,
        evaluation_guidance="Requires evaluation by Designated Physician. May be reinstated after successful treatment and sustained recovery.",
    ),
    "alcohol_use_disorder": DisqualifyingFactor(
        name="Alcohol Use Disorder",
        description="Diagnosis of alcohol use disorder that could affect reliability.",
        category=DisqualifyingCategory.MEDICAL,
        section="712.13",
        is_absolute=False,
        evaluation_guidance="Requires evaluation by Designated Physician. May be reinstated after successful treatment and sustained recovery.",
    ),
    "mental_health_condition": DisqualifyingFactor(
        name="Mental Health Condition",
        description="Mental or psychological condition that could impair judgment or reliability.",
        category=DisqualifyingCategory.PSYCHOLOGICAL,
        section="712.34",
        is_absolute=False,
        evaluation_guidance="Evaluated case-by-case by Designated Psychologist. Well-controlled conditions may not be disqualifying.",
    ),
    "physical_condition": DisqualifyingFactor(
        name="Physical Condition",
        description="Physical condition that could prevent safe performance of HRP duties.",
        category=DisqualifyingCategory.MEDICAL,
        section="712.32",
        is_absolute=False,
        evaluation_guidance="Evaluated based on job task analysis requirements. Accommodations may be possible.",
    ),
    "behavioral_issue": DisqualifyingFactor(
        name="Behavioral Issues",
        description="Pattern of behavior indicating unreliability (e.g., rule violations, honesty concerns).",
        category=DisqualifyingCategory.BEHAVIORAL,
        section="712.14",
        is_absolute=False,
        evaluation_guidance="Evaluated as part of supervisory review. May require corrective action or removal.",
    ),
    "security_concern": DisqualifyingFactor(
        name="Security Concern",
        description="Information from security review indicating potential reliability or trustworthiness issues.",
        category=DisqualifyingCategory.SECURITY,
        section="712.17",
        is_absolute=False,
        evaluation_guidance="Evaluated by DOE security personnel. May result in removal pending further investigation.",
    ),
}

# =============================================================================
# CONTROLLED SUBSTANCES (Drug Testing Panel)
# =============================================================================

CONTROLLED_SUBSTANCES: list[dict] = [
    {
        "substance": "Marijuana (THC)",
        "category": "Cannabinoid",
        "initial_cutoff": "50 ng/mL",
        "confirmatory_cutoff": "15 ng/mL",
    },
    {
        "substance": "Cocaine",
        "category": "Stimulant",
        "initial_cutoff": "150 ng/mL",
        "confirmatory_cutoff": "100 ng/mL",
    },
    {
        "substance": "Amphetamines",
        "category": "Stimulant",
        "initial_cutoff": "500 ng/mL",
        "confirmatory_cutoff": "250 ng/mL",
    },
    {
        "substance": "Opiates (Codeine/Morphine)",
        "category": "Narcotic",
        "initial_cutoff": "2000 ng/mL",
        "confirmatory_cutoff": "2000 ng/mL",
    },
    {
        "substance": "6-Acetylmorphine (Heroin)",
        "category": "Narcotic",
        "initial_cutoff": "10 ng/mL",
        "confirmatory_cutoff": "10 ng/mL",
    },
    {
        "substance": "Phencyclidine (PCP)",
        "category": "Hallucinogen",
        "initial_cutoff": "25 ng/mL",
        "confirmatory_cutoff": "25 ng/mL",
    },
    {
        "substance": "MDMA/MDA",
        "category": "Stimulant/Hallucinogen",
        "initial_cutoff": "500 ng/mL",
        "confirmatory_cutoff": "250 ng/mL",
    },
    {
        "substance": "Oxycodone",
        "category": "Narcotic",
        "initial_cutoff": "100 ng/mL",
        "confirmatory_cutoff": "100 ng/mL",
    },
]

# =============================================================================
# HRP ROLES
# =============================================================================

HRP_ROLES: dict[str, HRPRoleInfo] = {
    "certifying_official": HRPRoleInfo(
        role=HRPRole.HRP_CERTIFYING_OFFICIAL,
        title="HRP Certifying Official",
        description="The individual with final authority to approve or deny HRP certification or recertification.",
        responsibilities=[
            "Make final certification and recertification decisions",
            "Review all HRP evaluation components",
            "Ensure compliance with HRP requirements",
            "Approve or deny HRP candidate applications",
            "Document certification decisions",
        ],
        qualifications=[
            "Appointed by HRP Management Official",
            "Knowledge of HRP requirements",
            "Security clearance appropriate for position",
        ],
        section="712.3",
    ),
    "management_official": HRPRoleInfo(
        role=HRPRole.HRP_MANAGEMENT_OFFICIAL,
        title="HRP Management Official",
        description="The individual designated to manage the HRP at a DOE/NNSA site.",
        responsibilities=[
            "Oversee site HRP implementation",
            "Designate HRP officials",
            "Ensure HRP compliance",
            "Coordinate with DOE headquarters",
            "Approve temporary removals",
            "Review removal and reinstatement decisions",
        ],
        qualifications=[
            "Designated by DOE or NNSA",
            "Senior management position",
            "Knowledge of site operations",
            "Appropriate security clearance",
        ],
        section="712.3",
    ),
    "designated_physician": HRPRoleInfo(
        role=HRPRole.DESIGNATED_PHYSICIAN,
        title="Designated Physician",
        description="A licensed physician designated to provide medical evaluations of HRP candidates and certified individuals.",
        responsibilities=[
            "Conduct medical assessments",
            "Review medical history",
            "Perform physical examinations",
            "Determine medical fitness for duty",
            "Recommend accommodations if appropriate",
            "Report medical concerns to HRP management",
        ],
        qualifications=[
            "Licensed physician (MD or DO)",
            "Designated by HRP Management Official",
            "Training in occupational medicine preferred",
            "Knowledge of HRP medical requirements",
        ],
        section="712.33",
    ),
    "designated_psychologist": HRPRoleInfo(
        role=HRPRole.DESIGNATED_PSYCHOLOGIST,
        title="Designated Psychologist",
        description="A psychologist designated to provide psychological evaluations of HRP candidates and certified individuals.",
        responsibilities=[
            "Conduct psychological evaluations",
            "Administer psychological tests",
            "Assess mental health status",
            "Evaluate fitness for duty",
            "Report psychological concerns",
            "Recommend treatment when appropriate",
        ],
        qualifications=[
            "Licensed psychologist",
            "Designated by HRP Management Official",
            "Experience in personnel assessment",
            "Knowledge of HRP requirements",
        ],
        section="712.34",
    ),
    "supervisor": HRPRoleInfo(
        role=HRPRole.SUPERVISOR,
        title="Immediate Supervisor",
        description="The first-line supervisor who assigns, reviews, and approves the day-to-day work of HRP individuals.",
        responsibilities=[
            "Observe job performance daily",
            "Monitor behavior and demeanor",
            "Report safety or security concerns",
            "Document unusual incidents",
            "Conduct supervisory review assessments",
            "Communicate concerns to HRP management",
        ],
        qualifications=[
            "First-line supervisory position",
            "Training in HRP supervisory responsibilities",
            "Knowledge of subordinate's job duties",
        ],
        section="712.14",
    ),
    "medical_review_officer": HRPRoleInfo(
        role=HRPRole.MEDICAL_REVIEW_OFFICER,
        title="Medical Review Officer (MRO)",
        description="A licensed physician responsible for reviewing and interpreting drug test results.",
        responsibilities=[
            "Review laboratory drug test results",
            "Contact individuals with positive results",
            "Verify legitimate medical explanations",
            "Make final determination on test results",
            "Report verified results to HRP management",
        ],
        qualifications=[
            "Licensed physician",
            "MRO certification",
            "Training in drug testing procedures",
            "Knowledge of DOT/HHS guidelines",
        ],
        section="712.15",
    ),
}

# =============================================================================
# MEDICAL STANDARDS (Subpart B)
# =============================================================================

MEDICAL_STANDARDS: dict[str, MedicalStandard] = {
    "general_medical": MedicalStandard(
        name="General Medical Standards",
        description="Overall medical requirements for HRP certification.",
        section="712.30",
        category="general",
        conditions=[
            "Physical conditions that could affect reliability",
            "Mental conditions that could affect reliability",
            "Use of medications that could affect performance",
        ],
        evaluation_criteria=[
            "Ability to perform job duties safely",
            "No condition that could impair judgment",
            "No condition that could affect alertness",
            "No condition that increases risk to self or others",
        ],
    ),
    "physical_examination": MedicalStandard(
        name="Physical Examination Requirements",
        description="Requirements for physical examination of HRP candidates and certified individuals.",
        section="712.32",
        category="physical",
        conditions=[
            "Cardiovascular conditions",
            "Neurological conditions",
            "Musculoskeletal conditions",
            "Sensory impairments",
            "Chronic diseases",
        ],
        evaluation_criteria=[
            "Based on job task analysis",
            "Ability to perform essential functions",
            "Risk of sudden incapacitation",
            "Need for accommodations",
        ],
    ),
    "psychological_evaluation": MedicalStandard(
        name="Psychological Evaluation Requirements",
        description="Requirements for psychological evaluation of HRP candidates and certified individuals.",
        section="712.34",
        category="psychological",
        conditions=[
            "Mood disorders",
            "Anxiety disorders",
            "Personality disorders",
            "Psychotic disorders",
            "Cognitive impairments",
        ],
        evaluation_criteria=[
            "Emotional stability",
            "Judgment and decision-making",
            "Impulse control",
            "Stress tolerance",
            "Interpersonal functioning",
            "Honesty and integrity",
        ],
    ),
    "substance_use": MedicalStandard(
        name="Substance Use Standards",
        description="Standards related to alcohol and drug use.",
        section="712.13",
        category="substance",
        conditions=[
            "Alcohol use disorder",
            "Substance use disorder",
            "Current illegal drug use",
            "Prescription drug misuse",
        ],
        evaluation_criteria=[
            "History of substance use",
            "Current substance use",
            "Treatment history",
            "Recovery status",
            "Risk of relapse",
        ],
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_definition(term: str) -> dict | None:
    """Look up an HRP definition by term."""
    term_lower = term.lower().replace(" ", "_").replace("-", "_")
    if term_lower in HRP_DEFINITIONS:
        return HRP_DEFINITIONS[term_lower]
    # Try fuzzy match
    for key, value in HRP_DEFINITIONS.items():
        if term_lower in key or key in term_lower:
            return value
        if term.lower() in value["term"].lower():
            return value
    return None


def get_position_type(position_type: str) -> PositionTypeInfo | None:
    """Look up an HRP position type."""
    key = position_type.lower().replace(" ", "_").replace("-", "_")
    return HRP_POSITION_TYPES.get(key)


def get_section_info(section: str) -> dict | None:
    """Look up information about a specific section."""
    # Normalize section number
    if not section.startswith("712."):
        section = f"712.{section}"
    return HRP_SECTIONS.get(section)


def get_certification_component(component: str) -> CertificationComponent | None:
    """Look up a certification component."""
    key = component.lower().replace(" ", "_").replace("-", "_")
    return CERTIFICATION_COMPONENTS.get(key)


def get_disqualifying_factor(factor: str) -> DisqualifyingFactor | None:
    """Look up a disqualifying factor."""
    key = factor.lower().replace(" ", "_").replace("-", "_")
    return DISQUALIFYING_FACTORS.get(key)


def get_hrp_role(role: str) -> HRPRoleInfo | None:
    """Look up an HRP role."""
    key = role.lower().replace(" ", "_").replace("-", "_")
    return HRP_ROLES.get(key)


def get_medical_standard(standard: str) -> MedicalStandard | None:
    """Look up a medical standard."""
    key = standard.lower().replace(" ", "_").replace("-", "_")
    return MEDICAL_STANDARDS.get(key)
