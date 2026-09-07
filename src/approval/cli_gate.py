from datetime import datetime, timezone

from src.schemas.report import Approval


def approval_gate(report):
    print("\n=== HUMAN APPROVAL GATE ===")
    print("1) approve")
    print("2) reject")
    print("3) request_additional_research")
    print("4) modify_scope")

    choice = input("Decision: ").strip()

    decisions = {
        "1": "approve",
        "2": "reject",
        "3": "request_additional_research",
        "4": "modify_scope",
    }

    if choice not in decisions:
        raise ValueError(
            "No default approval: choose one of the four explicit decisions."
        )

    decision = decisions[choice]

    approver = input("Approver name: ").strip()
    notes = input("Notes: ").strip()

    # Create a proper Approval Pydantic object
    report.approval = Approval(
        approver=approver,
        decision=decision,
        timestamp=datetime.now(timezone.utc).isoformat(),
        notes=notes,
    )

    return report