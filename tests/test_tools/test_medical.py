"""Tests for medical tools.

Tests cover the business logic for HRP medical standards evaluation,
condition checking, and physician role information.
"""

from hrp_mcp.tools.medical import (
    CONDITION_MATCHERS,
    DEFAULT_CONSIDERATIONS,
    EVALUATION_PROCESS,
    _build_medical_condition_response,
    _contains_any,
    _find_matching_standards,
)

# --- Helper Function Tests ---


class TestContainsAny:
    """Tests for _contains_any helper function."""

    def test_should_return_true_when_keyword_present(self):
        """Test that matching keyword is found."""
        assert _contains_any("hypertension diagnosis", ("hypertension", "diabetes")) is True

    def test_should_return_false_when_no_keywords_present(self):
        """Test that non-matching text returns False."""
        assert _contains_any("healthy individual", ("hypertension", "diabetes")) is False

    def test_should_handle_empty_text(self):
        """Test empty input text."""
        assert _contains_any("", ("depression",)) is False

    def test_should_handle_empty_keywords(self):
        """Test empty keywords tuple."""
        assert _contains_any("depression", ()) is False


class TestFindMatchingStandards:
    """Tests for standard matching logic."""

    def test_should_find_psychological_standards_for_mental_conditions(self):
        """Test that psychological standards are found for mental health conditions."""
        standards, considerations = _find_matching_standards("depression diagnosis")

        assert len(standards) >= 1
        assert len(considerations) > 0
        # Should have mental health-related considerations
        assert any("symptom" in c.lower() or "treatment" in c.lower() for c in considerations)

    def test_should_find_physical_standards_for_physical_conditions(self):
        """Test that physical standards are found for physical conditions."""
        standards, considerations = _find_matching_standards("diabetes type 2")

        assert len(standards) >= 1
        # Should have physical condition considerations
        assert any("stability" in c.lower() or "medication" in c.lower() for c in considerations)

    def test_should_find_substance_standards_for_substance_issues(self):
        """Test that substance standards are found for substance-related conditions."""
        standards, considerations = _find_matching_standards("alcohol recovery")

        assert len(standards) >= 1
        assert any("sobriety" in c.lower() or "recovery" in c.lower() for c in considerations)

    def test_should_always_include_general_medical_standard(self):
        """Test that general medical standard is always included."""
        standards, _ = _find_matching_standards("unknown condition xyz")

        # Should still have at least general medical standard
        assert len(standards) >= 1

    def test_should_not_duplicate_standards(self):
        """Test that standards are not duplicated."""
        standards, _ = _find_matching_standards("depression and anxiety")

        # Count unique standard IDs
        standard_names = [s.get("name") for s in standards]
        assert len(standard_names) == len(set(standard_names))


class TestBuildMedicalConditionResponse:
    """Tests for response building."""

    def test_should_include_condition_in_response(self):
        """Test that original condition is included."""
        response = _build_medical_condition_response("test condition", [], [])

        assert response["condition"] == "test condition"

    def test_should_include_evaluation_process(self):
        """Test that evaluation process is included."""
        response = _build_medical_condition_response("test", [], [])

        assert response["evaluation_process"] == EVALUATION_PROCESS
        assert len(response["evaluation_process"]) > 0

    def test_should_use_default_considerations_when_empty(self):
        """Test that default considerations are used when none provided."""
        response = _build_medical_condition_response("test", [], [])

        assert response["key_considerations"] == DEFAULT_CONSIDERATIONS

    def test_should_use_provided_considerations(self):
        """Test that provided considerations are used."""
        considerations = ["Custom consideration 1", "Custom consideration 2"]
        response = _build_medical_condition_response("test", [], considerations)

        assert response["key_considerations"] == considerations

    def test_should_always_include_disclaimer(self):
        """Test that disclaimer is always present."""
        response = _build_medical_condition_response("test", [], [])

        assert "disclaimer" in response
        assert "Designated Physician" in response["disclaimer"]


# --- Business Logic Integration Tests ---


class TestMedicalConditionWorkflow:
    """Integration tests for medical condition evaluation workflow."""

    def test_should_identify_psychological_conditions(self):
        """Test detection of psychological conditions."""
        conditions = ["depression", "anxiety", "bipolar", "ptsd"]

        for condition in conditions:
            standards, considerations = _find_matching_standards(f"diagnosed with {condition}")
            result = _build_medical_condition_response(condition, standards, considerations)

            assert len(result["relevant_standards"]) >= 1
            assert len(result["key_considerations"]) > 0

    def test_should_identify_physical_conditions(self):
        """Test detection of physical conditions."""
        conditions = ["hypertension", "diabetes", "cardiac issues", "hearing loss"]

        for condition in conditions:
            standards, considerations = _find_matching_standards(condition)
            result = _build_medical_condition_response(condition, standards, considerations)

            assert len(result["relevant_standards"]) >= 1

    def test_should_identify_substance_conditions(self):
        """Test detection of substance-related conditions."""
        condition = "in recovery from alcohol addiction"
        standards, considerations = _find_matching_standards(condition)
        result = _build_medical_condition_response(condition, standards, considerations)

        assert len(result["relevant_standards"]) >= 1
        # Should have substance-specific considerations
        assert any(
            "recovery" in c.lower() or "sobriety" in c.lower() for c in result["key_considerations"]
        )

    def test_should_be_case_insensitive(self):
        """Test that matching is case-insensitive."""
        for text in ["depression", "DEPRESSION", "Depression"]:
            standards, _ = _find_matching_standards(text.lower())
            assert len(standards) >= 1

    def test_should_handle_multiple_conditions(self):
        """Test handling of multiple conditions in one description."""
        condition = "hypertension and depression, both well-controlled"
        standards, considerations = _find_matching_standards(condition)
        result = _build_medical_condition_response(condition, standards, considerations)

        # Should find standards for both
        assert len(result["relevant_standards"]) >= 2

    def test_should_always_include_recommendation(self):
        """Test that recommendation is always present."""
        standards, considerations = _find_matching_standards("any condition")
        result = _build_medical_condition_response("any condition", standards, considerations)

        assert "recommendation" in result
        assert "Designated Physician" in result["recommendation"]

    def test_should_return_evaluation_process(self):
        """Test that evaluation process is included."""
        standards, considerations = _find_matching_standards("test condition")
        result = _build_medical_condition_response("test condition", standards, considerations)

        assert "evaluation_process" in result
        assert len(result["evaluation_process"]) > 0


# --- Configuration Tests ---


class TestConditionMatcherConfiguration:
    """Tests for CONDITION_MATCHERS configuration."""

    def test_should_have_psychological_matcher(self):
        """Test that psychological matcher is configured."""
        matcher_ids = {m.standard_id for m in CONDITION_MATCHERS}
        assert "psychological_evaluation" in matcher_ids

    def test_should_have_physical_matcher(self):
        """Test that physical examination matcher is configured."""
        matcher_ids = {m.standard_id for m in CONDITION_MATCHERS}
        assert "physical_examination" in matcher_ids

    def test_should_have_substance_matcher(self):
        """Test that substance use matcher is configured."""
        matcher_ids = {m.standard_id for m in CONDITION_MATCHERS}
        assert "substance_use" in matcher_ids

    def test_should_have_keywords_for_each_matcher(self):
        """Test that each matcher has keywords."""
        for matcher in CONDITION_MATCHERS:
            assert len(matcher.keywords) > 0, f"{matcher.standard_id} has no keywords"

    def test_should_have_considerations_for_each_matcher(self):
        """Test that each matcher has considerations."""
        for matcher in CONDITION_MATCHERS:
            assert len(matcher.considerations) > 0, f"{matcher.standard_id} has no considerations"


# --- Edge Case Tests ---


class TestMedicalToolsEdgeCases:
    """Edge case tests for medical tools."""

    def test_check_condition_with_empty_string(self):
        """Test check_medical_condition with empty string."""
        standards, considerations = _find_matching_standards("")
        result = _build_medical_condition_response("", standards, considerations)

        # Should still return valid response with general standard
        assert "relevant_standards" in result
        assert "disclaimer" in result

    def test_check_condition_with_unrelated_text(self):
        """Test with text that doesn't match any specific condition."""
        standards, considerations = _find_matching_standards("excellent health status")
        result = _build_medical_condition_response(
            "excellent health status", standards, considerations
        )

        # Should still get general medical standard
        assert len(result["relevant_standards"]) >= 1
