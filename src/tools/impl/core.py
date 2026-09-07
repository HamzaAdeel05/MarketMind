import json
from pathlib import Path

from src.schemas.tools import (
    SearchArgs,
    RetrieveArgs,
    CalculateArgs,
    CompareArgs,
    SaveEvidenceArgs,
    GenerateReportArgs
)
from src.schemas.evidence import EvidenceRecord


CORPUS_PATH = Path(__file__).resolve().parents[3] / "samples" / "corpus.json"


def _corpus():
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def search_information(args: SearchArgs, state):
    terms = [
        x.lower()
        for x in args.query.split()
        if len(x) > 2
    ]

    documents = []

    for document in _corpus():
        text = (
            document["title"]
            + " "
            + document["content"]
        ).lower()

        score = sum(
            1
            for term in terms
            if term in text
        )

        if score:
            documents.append((score, document))

    documents.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return {
        "ok": True,
        "results": [
            {
                "document_id": document["id"],
                "title": document["title"],
                "source": document["source"],
                "year": document["year"],
                "snippet": document["content"][:600]
            }
            for _, document in documents[:args.max_results]
        ]
    }


def retrieve_document(args: RetrieveArgs, state):
    for document in _corpus():
        if document["id"] == args.document_id:
            return {
                "ok": True,
                "document": {
                    "document_id": document["id"],
                    "title": document["title"],
                    "source": document["source"],
                    "year": document["year"],
                    "content": document["content"]
                }
            }

    return {
        "ok": False,
        "error_type": "not_found",
        "message": "Document not found."
    }


def calculate_metric(args: CalculateArgs, state):
    values = args.values

    if args.operation == "sum":
        result = sum(values)

    elif args.operation == "average":
        if not values:
            return {
                "ok": False,
                "error_type": "invalid_calculation",
                "message": "average requires at least one value."
            }

        result = sum(values) / len(values)

    elif args.operation == "difference":
        if len(values) < 2:
            return {
                "ok": False,
                "error_type": "invalid_calculation",
                "message": "difference requires two values."
            }

        result = values[0] - values[1]

    else:
        if len(values) != 2 or values[0] == 0:
            return {
                "ok": False,
                "error_type": "invalid_calculation",
                "message": (
                    "percentage_change requires two values "
                    "and a non-zero baseline."
                )
            }

        result = (
            (values[1] - values[0])
            / values[0]
            * 100
        )

    return {
        "ok": True,
        "result": result,
        "operation": args.operation
    }


def compare_companies(args: CompareArgs, state):
    matrix = {
        entity: {
            attribute: "not established"
            for attribute in args.attributes
        }
        for entity in args.entities
    }

    for record in state.evidence:
        claim = record.claim.lower()

        for entity in args.entities:
            if entity.lower() not in claim:
                continue

            for attribute in args.attributes:
                if attribute.lower() in claim:
                    matrix[entity][attribute] = record.claim

    return {
        "ok": True,
        "matrix": matrix,
        "note": (
            "Cells remain 'not established' when the "
            "evidence store does not support the attribute."
        )
    }


def save_research(args: SaveEvidenceArgs, state):
    if args.source_ref not in state.source_refs:
        return {
            "ok": False,
            "error_type": "provenance",
            "message": (
                "source_ref does not resolve to a prior "
                "tool result."
            )
        }

    document_id = state.source_refs[args.source_ref]

    document = None

    for item in _corpus():
        if item["id"] == document_id:
            document = item
            break

    if document is None:
        return {
            "ok": False,
            "error_type": "provenance",
            "message": "Referenced document no longer exists."
        }

    suspicious_phrases = [
        "ignore prior instructions",
        "ignore previous instructions",
        "system:",
        "developer:",
        "assistant:"
    ]

    lower_claim = args.claim.lower()

    if any(
        phrase in lower_claim
        for phrase in suspicious_phrases
    ):
        return {
            "ok": False,
            "error_type": "prompt_injection",
            "message": (
                "Retrieved content contains instruction-like "
                "text and cannot be stored as evidence."
            )
        }

    credibility = "medium"

    if "vendor documentation" in document["source"].lower():
        credibility = "medium"
    elif "adversarial" in document["source"].lower():
        credibility = "low"

    evidence_id = f"E-{len(state.evidence) + 1:03d}"

    record = EvidenceRecord(
        evidence_id=evidence_id,
        question_id=args.question_id,
        claim=args.claim,
        claim_type=args.claim_type,
        source_ref=args.source_ref,
        source_kind="retrieved_document",
        source_detail=(
            f"{document['title']} | "
            f"{document['source']} | "
            f"{document['year']}"
        ),
        credibility=credibility,
        recency=str(document["year"]),
        corroboration=[],
        confidence=args.confidence
    )

    state.evidence.append(record)

    return {
        "ok": True,
        "evidence_id": evidence_id,
        "source_ref": args.source_ref
    }


def generate_report(args: GenerateReportArgs, state):
    if not state.plan:
        return {
            "ok": False,
            "error_type": "plan_missing",
            "message": "Research plan is missing."
        }

    missing = []

    for objective in state.plan.objectives:
        for question in objective.subquestions:
            covered = any(
                evidence.question_id == question.id
                for evidence in state.evidence
            )

            if not covered:
                missing.append(question.id)

    if missing:
        return {
            "ok": False,
            "error_type": "coverage",
            "message": (
                "Mandatory questions lack evidence."
            ),
            "missing_question_ids": missing
        }

    unresolved_sources = []

    for evidence in state.evidence:
        if evidence.source_ref not in state.source_refs:
            unresolved_sources.append(
                evidence.evidence_id
            )

    if unresolved_sources:
        return {
            "ok": False,
            "error_type": "provenance",
            "message": (
                "Some evidence records have unresolved "
                "source references."
            ),
            "evidence_ids": unresolved_sources
        }

    return {
        "ok": True,
        "ready": True
    }