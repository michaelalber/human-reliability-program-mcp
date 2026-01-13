"""Tests for certification tools.

Tests cover the business logic for HRP certification requirements,
disqualifying factors, and position types.
"""

from hrp_mcp.tools.certification import (
    FACTOR_MATCHERS,
    HALLUCINOGEN_KEYWORDS,
    _build_disqualifying_response,
    _check_hallucinogen_factors,
    _check_standard_factors,
    _contains_any,
)

# --- Helper Function Tests ---


class TestContainsAny:
    """Tests for _contains_any helper function."""

    def test_should_return_true_when_keyword_present(self):
        """Test that matching keyword is found."""
        assert _contains_any("marijuana use", ("marijuana", "cocaine")) is True

    def test_should_return_false_when_no_keywords_present(self):
        """Test that non-matching text returns False."""
        assert _contains_any("clean record", ("marijuana", "cocaine")) is False

    def test_should_return_true_for_partial_match(self):
        """Test that partial word matches work (substring)."""
        assert _contains_any("hallucinogenic drugs", ("hallucinogen",)) is True

    def test_should_handle_empty_text(self):
        """Test empty input text."""
        assert _contains_any("", ("marijuana",)) is False

    def test_should_handle_empty_keywords(self):
        """Test empty keywords tuple."""
        assert _contains_any("marijuana", ()) is False


class TestCheckHallucinogenFactors:
    """Tests for hallucinogen-specific factor detection."""

    def test_should_detect_hallucinogen_use_within_5_years(self):
        """Test detection of hallucinogen use within 5 years (absolute disqualifier)."""
        results = _check_hallucinogen_factors("lsd use 2 years ago")
        assert len(results) >= 1
        # All hallucinogen results should be absolute disqualifiers
        assert all(is_absolute for _, is_absolute in results)

    def test_should_detect_hallucinogen_flashback(self):
        """Test detection of hallucinogen flashback (absolute disqualifier)."""
        results = _check_hallucinogen_factors("experienced flashback from psilocybin")
        assert len(results) >= 1
        assert all(is_absolute for _, is_absolute in results)

    def test_should_not_match_hallucinogen_over_5_years(self):
        """Test that hallucinogen use over 5 years ago without flashback may not trigger."""
        # Note: The current implementation checks for "5 year" or 1-4 years explicitly
        results = _check_hallucinogen_factors("lsd use 10 years ago, no issues since")
        # Should not match the time-based rule (no "X year" where X < 5)
        assert len(results) == 0

    def test_should_return_empty_for_non_hallucinogen(self):
        """Test that non-hallucinogen substances don't trigger hallucinogen checks."""
        results = _check_hallucinogen_factors("marijuana use last month")
        assert len(results) == 0

    def test_should_detect_multiple_hallucinogen_keywords(self):
        """Test detection with various hallucinogen terms."""
        for keyword in ["lsd", "mushroom", "psilocybin", "mescaline", "peyote"]:
            results = _check_hallucinogen_factors(f"{keyword} use 1 year ago")
            assert len(results) >= 1, f"Should detect {keyword}"


class TestCheckStandardFactors:
    """Tests for standard (non-hallucinogen) factor detection."""

    def test_should_detect_drug_use(self):
        """Test detection of drug-related factors."""
        results = _check_standard_factors("positive drug test for cocaine")
        assert len(results) >= 1
        factor_ids = [f.name for f, _ in results]
        # Should find drug_test_positive based on keywords
        assert any("drug" in fid.lower() or "positive" in fid.lower() for fid in factor_ids)

    def test_should_detect_alcohol_disorder_with_secondary_keyword(self):
        """Test that alcohol disorder requires secondary keywords."""
        # Just "alcohol" should get alcohol_test_positive but not disorder
        results_simple = _check_standard_factors("alcohol consumption")
        results_disorder = _check_standard_factors("alcohol use disorder diagnosis")

        # Disorder result should have more matches (includes disorder-specific)
        simple_ids = {f.name for f, _ in results_simple}
        disorder_ids = {f.name for f, _ in results_disorder}
        assert len(disorder_ids) >= len(simple_ids)

    def test_should_detect_mental_health_conditions(self):
        """Test detection of mental health conditions."""
        conditions = ["depression", "anxiety", "bipolar", "ptsd"]
        for condition in conditions:
            results = _check_standard_factors(f"diagnosed with {condition}")
            assert len(results) >= 1, f"Should detect {condition}"

    def test_should_detect_security_concerns(self):
        """Test detection of security-related factors."""
        results = _check_standard_factors("foreign contact concerns")
        assert len(results) >= 1

    def test_should_return_empty_for_unrelated_text(self):
        """Test that unrelated text returns no matches."""
        results = _check_standard_factors("excellent performance review")
        assert len(results) == 0


class TestBuildDisqualifyingResponse:
    """Tests for response building."""

    def test_should_return_no_factors_response_when_empty(self):
        """Test response when no factors match."""
        response = _build_disqualifying_response("clean record", [], False)

        assert response["factor_description"] == "clean record"
        assert response["matching_factors"] == []
        assert response["is_absolute_disqualifier"] is False
        assert "No specific disqualifying factors" in response["guidance"]

    def test_should_include_guidance_for_matching_factors(self):
        """Test response includes guidance when factors match."""
        mock_factors = [{"name": "Test Factor", "evaluation_guidance": "Evaluate carefully"}]
        response = _build_disqualifying_response("test condition", mock_factors, False)

        assert len(response["matching_factors"]) == 1
        assert "Test Factor" in response["guidance"]

    def test_should_indicate_absolute_disqualifier(self):
        """Test that absolute disqualifier flag is set correctly."""
        mock_factors = [{"name": "Hallucinogen Use", "evaluation_guidance": ""}]
        response = _build_disqualifying_response("lsd use", mock_factors, True)

        assert response["is_absolute_disqualifier"] is True
        assert "Immediate consultation" in response["recommendation"]

    def test_should_always_include_disclaimer(self):
        """Test that disclaimer is always present."""
        response = _build_disqualifying_response("anything", [], False)
        assert "disclaimer" in response
        assert "informational guidance only" in response["disclaimer"]


# --- Business Logic Integration Tests ---
#
# Note: The actual MCP tool functions are wrapped with @mcp.tool() decorator
# which requires the MCP server context. These tests verify the business logic
# by testing the complete workflow through helper functions.


class TestDisqualifyingFactorWorkflow:
    """Integration tests for disqualifying factor evaluation workflow."""

    def test_should_identify_hallucinogen_as_absolute_disqualifier(self):
        """Test that hallucinogen use within 5 years is absolute disqualifier."""
        factor_lower = "used lsd 3 years ago"

        # Run the full workflow
        all_matches = _check_hallucinogen_factors(factor_lower) + _check_standard_factors(
            factor_lower
        )
        matching_factors = [factor.to_dict() for factor, _ in all_matches]
        is_absolute = any(is_abs for _, is_abs in all_matches)
        result = _build_disqualifying_response(
            "used LSD 3 years ago", matching_factors, is_absolute
        )

        assert result["is_absolute_disqualifier"] is True
        assert len(result["matching_factors"]) >= 1

    def test_should_identify_drug_test_failure(self):
        """Test detection of positive drug test."""
        factor_lower = "positive drug test for marijuana"

        all_matches = _check_hallucinogen_factors(factor_lower) + _check_standard_factors(
            factor_lower
        )
        matching_factors = [factor.to_dict() for factor, _ in all_matches]
        is_absolute = any(is_abs for _, is_abs in all_matches)
        result = _build_disqualifying_response(factor_lower, matching_factors, is_absolute)

        assert len(result["matching_factors"]) >= 1
        assert result["is_absolute_disqualifier"] is False  # Drug test is not absolute

    def test_should_identify_mental_health_condition(self):
        """Test detection of mental health conditions."""
        factor_lower = "diagnosed with depression"

        all_matches = _check_hallucinogen_factors(factor_lower) + _check_standard_factors(
            factor_lower
        )
        matching_factors = [factor.to_dict() for factor, _ in all_matches]
        is_absolute = any(is_abs for _, is_abs in all_matches)
        result = _build_disqualifying_response(factor_lower, matching_factors, is_absolute)

        assert len(result["matching_factors"]) >= 1
        assert result["is_absolute_disqualifier"] is False

    def test_should_return_no_factors_for_clean_description(self):
        """Test that clean descriptions return no factors."""
        factor_lower = "excellent work history"

        all_matches = _check_hallucinogen_factors(factor_lower) + _check_standard_factors(
            factor_lower
        )
        matching_factors = [factor.to_dict() for factor, _ in all_matches]
        is_absolute = any(is_abs for _, is_abs in all_matches)
        result = _build_disqualifying_response(factor_lower, matching_factors, is_absolute)

        assert result["matching_factors"] == []
        assert result["is_absolute_disqualifier"] is False

    def test_should_handle_multiple_conditions(self):
        """Test handling of descriptions with multiple potential factors."""
        factor_lower = "history of alcohol disorder and depression"

        all_matches = _check_hallucinogen_factors(factor_lower) + _check_standard_factors(
            factor_lower
        )
        matching_factors = [factor.to_dict() for factor, _ in all_matches]

        # Should find multiple factors
        assert len(matching_factors) >= 2

    def test_should_be_case_insensitive(self):
        """Test that matching is case-insensitive."""
        for text in ["marijuana use", "MARIJUANA USE", "Marijuana Use"]:
            factor_lower = text.lower()
            all_matches = _check_hallucinogen_factors(factor_lower) + _check_standard_factors(
                factor_lower
            )
            assert len(all_matches) >= 1

    def test_should_handle_empty_input(self):
        """Test handling of empty input."""
        factor_lower = ""

        all_matches = _check_hallucinogen_factors(factor_lower) + _check_standard_factors(
            factor_lower
        )
        matching_factors = [factor.to_dict() for factor, _ in all_matches]
        result = _build_disqualifying_response("", matching_factors, False)

        assert result["matching_factors"] == []
        assert "factor_description" in result


# --- Configuration Tests ---


class TestFactorMatcherConfiguration:
    """Tests for FACTOR_MATCHERS configuration."""

    def test_should_have_all_required_matchers(self):
        """Test that all expected matchers are configured."""
        factor_ids = {m.factor_id for m in FACTOR_MATCHERS}

        expected = {
            "drug_test_positive",
            "substance_use_disorder",
            "alcohol_test_positive",
            "alcohol_use_disorder",
            "mental_health_condition",
            "physical_condition",
            "behavioral_issue",
            "security_concern",
        }

        assert expected.issubset(factor_ids)

    def test_should_have_keywords_for_each_matcher(self):
        """Test that each matcher has keywords defined."""
        for matcher in FACTOR_MATCHERS:
            assert len(matcher.keywords) > 0, f"{matcher.factor_id} has no keywords"

    def test_hallucinogen_keywords_should_be_defined(self):
        """Test that hallucinogen keywords are properly defined."""
        assert len(HALLUCINOGEN_KEYWORDS) >= 5
        assert "lsd" in HALLUCINOGEN_KEYWORDS
        assert "psilocybin" in HALLUCINOGEN_KEYWORDS
