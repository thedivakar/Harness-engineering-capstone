import json
from pathlib import Path

from claims_intake.session import ClaimSession
from claims_intake.tools import CLAIM_TYPES, SEVERITIES, TOOL_SCHEMAS, make_executor


def _session(tmp_path: Path) -> ClaimSession:
    return ClaimSession(
        claim_id="claim_test",
        policy_id="POL-1",
        run_dir=tmp_path,
        policies={
            "POL-1": {
                "policy_id": "POL-1",
                "policy_holder": "Alex Doe",
                "coverage": ["property_damage", "theft"],
                "deductible": 500,
                "status": "active",
            }
        },
        clarification_responses={"locked": "yes it was locked"},
    )


def test_seven_tools_registered_with_schemas() -> None:
    names = {t["name"] for t in TOOL_SCHEMAS}
    assert names == {
        "lookup_policy",
        "record_claim_fact",
        "classify_claim",
        "assess_severity",
        "request_clarification",
        "route_to_adjuster",
        "escalate_to_human",
    }
    for schema in TOOL_SCHEMAS:
        assert "input_schema" in schema
        assert schema["input_schema"]["type"] == "object"
        assert "required" in schema["input_schema"]


def test_categorical_fields_use_enums() -> None:
    by_name = {t["name"]: t for t in TOOL_SCHEMAS}
    assert by_name["classify_claim"]["input_schema"]["properties"]["claim_type"]["enum"] == CLAIM_TYPES
    assert by_name["assess_severity"]["input_schema"]["properties"]["severity"]["enum"] == SEVERITIES
    assert by_name["route_to_adjuster"]["input_schema"]["properties"]["queue"]["enum"] == CLAIM_TYPES


def test_lookup_policy_returns_record(tmp_path: Path) -> None:
    s = _session(tmp_path)
    out = make_executor(s)("lookup_policy", {"policy_id": "POL-1"})
    payload = json.loads(out)
    assert payload["policy_holder"] == "Alex Doe"


def test_lookup_policy_unknown_id_returns_graceful_error(tmp_path: Path) -> None:
    s = _session(tmp_path)
    out = make_executor(s)("lookup_policy", {"policy_id": "POL-MISSING"})
    err = json.loads(out)
    assert err["is_error"] is True
    assert err["error_category"] == "permanent"
    assert err["is_retryable"] is False
    assert "not found" in err["message"]


def test_unknown_tool_returns_graceful_error(tmp_path: Path) -> None:
    s = _session(tmp_path)
    out = make_executor(s)("definitely_not_a_tool", {})
    err = json.loads(out)
    assert err["is_error"] is True
    assert err["error_category"] == "permanent"


def test_request_clarification_returns_scripted_reply(tmp_path: Path) -> None:
    s = _session(tmp_path)
    out = make_executor(s)(
        "request_clarification",
        {
            "question": "Was the bike locked when it was taken?",
            "ambiguity_between": ["theft", "property_damage"],
        },
    )
    payload = json.loads(out)
    assert payload["claimant_reply"] == "yes it was locked"
    assert len(s.clarifications_asked) == 1


def test_request_clarification_no_response_when_unscripted(tmp_path: Path) -> None:
    s = _session(tmp_path)
    out = make_executor(s)(
        "request_clarification",
        {
            "question": "What was the weather like that day?",
            "ambiguity_between": ["property_damage", "auto"],
        },
    )
    payload = json.loads(out)
    assert payload["claimant_reply"] == "NO_RESPONSE"


def test_routing_requires_classification_and_severity(tmp_path: Path) -> None:
    s = _session(tmp_path)
    out = make_executor(s)(
        "route_to_adjuster",
        {"queue": "property_damage", "claim_summary": "fire damage"},
    )
    err = json.loads(out)
    assert err["is_error"] is True
    assert "classify_claim must be called" in err["message"]


def test_routing_writes_jsonl_and_marks_terminal(tmp_path: Path) -> None:
    s = _session(tmp_path)
    exec_ = make_executor(s)
    exec_("classify_claim", {"claim_type": "property_damage", "confidence": 0.9, "rationale": "fire"})
    exec_("assess_severity", {"severity": "high", "rationale": "kitchen destroyed"})
    out = exec_("route_to_adjuster", {"queue": "property_damage", "claim_summary": "kitchen fire"})
    payload = json.loads(out)
    assert payload["routed"] is True

    queue_file = tmp_path / "queues" / "property_damage.jsonl"
    assert queue_file.exists()
    record = json.loads(queue_file.read_text().strip())
    assert record["claim_type"] == "property_damage"
    assert record["severity"] == "high"
    assert record["confidence"] == 0.9
    assert s.terminal_called
    assert s.outcome == "routed"


def test_escalation_writes_jsonl_and_marks_terminal(tmp_path: Path) -> None:
    s = _session(tmp_path)
    exec_ = make_executor(s)
    out = exec_(
        "escalate_to_human",
        {
            "reason": "unresolved_ambiguity",
            "structured_summary": {
                "policy_id": "POL-1",
                "root_cause": "claimant cannot say whether water came from interior plumbing or neighbor's roof",
                "candidate_claim_types": ["property_damage", "liability"],
                "case_facts": {"location": "basement"},
                "recommended_action": "human adjuster site visit",
                "confidence": 0.4,
            },
        },
    )
    payload = json.loads(out)
    assert payload["escalated"] is True

    esc_file = tmp_path / "escalations.jsonl"
    assert esc_file.exists()
    record = json.loads(esc_file.read_text().strip())
    assert record["confidence"] == 0.4
    assert record["candidate_claim_types"] == ["property_damage", "liability"]
    assert s.outcome == "escalated"


def test_double_terminal_is_graceful_error(tmp_path: Path) -> None:
    s = _session(tmp_path)
    exec_ = make_executor(s)
    exec_("classify_claim", {"claim_type": "theft", "confidence": 0.95, "rationale": "stolen"})
    exec_("assess_severity", {"severity": "low", "rationale": "low value"})
    exec_("route_to_adjuster", {"queue": "theft", "claim_summary": "bike theft"})
    out = exec_(
        "escalate_to_human",
        {
            "reason": "other",
            "structured_summary": {
                "policy_id": "POL-1",
                "root_cause": "x",
                "candidate_claim_types": ["theft"],
                "case_facts": {},
                "recommended_action": "x",
                "confidence": 0.5,
            },
        },
    )
    err = json.loads(out)
    assert err["is_error"] is True
    assert "already called" in err["message"]


def test_handler_exception_is_caught_as_transient_error(tmp_path: Path) -> None:
    s = _session(tmp_path)
    # Force a TypeError inside a handler by passing wrong shape that bypasses validation.
    # The dispatcher should still return a JSON error, not raise.
    out = make_executor(s)("classify_claim", {"claim_type": "auto", "confidence": "not-a-number", "rationale": "x"})
    err = json.loads(out)
    assert err["is_error"] is True
