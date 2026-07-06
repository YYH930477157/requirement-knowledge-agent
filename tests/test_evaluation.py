from requirement_knowledge_agent.evaluation import evaluate_package


def test_evaluate_package_reports_accuracy_and_failures():
    package = {
        "items": [
            {
                "requirement_id": "REQ-1",
                "decision": "applied",
                "applied_solution_ids": ["SOL-1"],
                "matches": {
                    "standards": [{"clause_id": "STD-1"}],
                    "solutions": [{"solution": {"solution_id": "SOL-1"}}],
                },
            },
            {
                "requirement_id": "REQ-2",
                "decision": "needs_review",
                "applied_solution_ids": [],
                "matches": {
                    "standards": [],
                    "solutions": [],
                },
            },
        ],
        "input_errors": [],
    }
    expected = [
        {
            "requirement_id": "REQ-1",
            "expected_standard_clause_ids": ["STD-1"],
            "expected_solution_ids": ["SOL-1"],
            "expected_decision": "applied",
        },
        {
            "requirement_id": "REQ-2",
            "expected_standard_clause_ids": ["STD-2"],
            "expected_solution_ids": ["SOL-2"],
            "expected_decision": "suggested",
        },
    ]

    report = evaluate_package(package, expected)

    assert report["summary"] == {
        "total_expected": 2,
        "evaluated": 2,
        "standard_hit_rate": 0.5,
        "solution_hit_rate": 0.5,
        "decision_accuracy": 0.5,
    }
    assert report["failures"] == [
        {
            "requirement_id": "REQ-2",
            "standard_hit": False,
            "solution_hit": False,
            "decision_correct": False,
            "expected_standard_clause_ids": ["STD-2"],
            "actual_standard_clause_ids": [],
            "expected_solution_ids": ["SOL-2"],
            "actual_solution_ids": [],
            "expected_decision": "suggested",
            "actual_decision": "needs_review",
        }
    ]


def test_evaluate_package_counts_missing_analysis_as_failure():
    report = evaluate_package(
        {"items": [], "input_errors": []},
        [
            {
                "requirement_id": "REQ-1",
                "expected_standard_clause_ids": [],
                "expected_solution_ids": [],
                "expected_decision": "needs_review",
            }
        ],
    )

    assert report["summary"]["evaluated"] == 0
    assert report["summary"]["decision_accuracy"] == 0.0
    assert report["failures"][0]["actual_decision"] == ""
