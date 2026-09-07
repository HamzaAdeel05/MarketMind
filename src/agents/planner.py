import json
from src.schemas.plan import ResearchPlan


class Planner:
    def __init__(self, llm):
        self.llm = llm

    def run(self, run_id, normalized):

        if not self.llm.settings.use_openai:
            return ResearchPlan(
                entity_type=normalized["entity_type"],
                segment=normalized["segment"],
                geography=normalized["geography"],
                time_horizon=normalized["time_horizon"],
                deliverable_type=normalized["deliverable_type"],
                assumptions=normalized["assumptions"],
                ambiguities=normalized["ambiguities"],
                objectives=[
                    {
                        "id": "O1",
                        "objective": "Understand category evaluation criteria",
                        "subquestions": [
                            {
                                "id": "O1_Q1",
                                "question": "What criteria should enterprise buyers evaluate?",
                                "evidence_types": ["fact"],
                                "candidate_tools": [
                                    "search_information",
                                    "retrieve_document",
                                ],
                            },
                            {
                                "id": "O1_Q2",
                                "question": "What governance and security areas are relevant?",
                                "evidence_types": ["fact"],
                                "candidate_tools": [
                                    "search_information",
                                    "retrieve_document",
                                ],
                            },
                        ],
                    },
                    {
                        "id": "O2",
                        "objective": "Assess adoption and productivity evidence",
                        "subquestions": [
                            {
                                "id": "O2_Q1",
                                "question": "What does the corpus establish about productivity measurement?",
                                "evidence_types": ["fact", "uncertainty"],
                                "candidate_tools": [
                                    "search_information",
                                    "retrieve_document",
                                ],
                            },
                            {
                                "id": "O2_Q2",
                                "question": "What adoption controls are recommended?",
                                "evidence_types": ["fact"],
                                "candidate_tools": [
                                    "search_information",
                                    "retrieve_document",
                                ],
                            },
                        ],
                    },
                    {
                        "id": "O3",
                        "objective": "Identify gaps and comparison opportunities",
                        "subquestions": [
                            {
                                "id": "O3_Q1",
                                "question": "Which vendor attributes are not established by available evidence?",
                                "evidence_types": ["uncertainty", "comparison"],
                                "candidate_tools": [
                                    "search_information",
                                    "compare_companies",
                                ],
                            },
                            {
                                "id": "O3_Q2",
                                "question": "What limitations should a decision maker see?",
                                "evidence_types": ["uncertainty"],
                                "candidate_tools": [
                                    "search_information",
                                ],
                            },
                        ],
                    },
                ],
            )

        system_prompt = """
You are the planning agent for a research system.

Create a research plan for the user's request.

IMPORTANT:
Return ONLY valid JSON.

The JSON MUST have exactly this top-level structure:

{
  "entity_type": "string",
  "segment": "string",
  "geography": "string",
  "time_horizon": "string",
  "deliverable_type": "string",
  "assumptions": [],
  "ambiguities": [],
  "objectives": [
    {
      "id": "O1",
      "objective": "string",
      "subquestions": [
        {
          "id": "Q1",
          "question": "string",
          "evidence_types": ["fact"],
          "candidate_tools": ["search_information"]
        }
      ]
    }
  ]
}

Rules:

1. Create 3-6 objectives.
2. Each objective must have 2-5 subquestions.
3. Every objective MUST have an id such as O1, O2, O3.
4. Every subquestion MUST be an object.
5. Every subquestion MUST have:
   - id
   - question
   - evidence_types
   - candidate_tools
6. evidence_types MUST contain ONLY these values:
   - fact
   - comparison
   - metric
   - uncertainty
7. Do NOT use values such as:
   - forecast
   - trend analysis
   - time series
   - market analysis
   - ranking
   - expert opinion
   - risk assessment
8. Do NOT return a "research_plan" wrapper.
9. Do NOT return "research_question" as a replacement for the required fields.
10. Return JSON only. No markdown. No explanation.

The required fields must always be present, even if their value is an empty string or empty array.
"""

        text = self.llm.text(
            run_id=run_id,
            stage="planner",
            system=system_prompt,
            user=json.dumps(normalized),
        )

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Planner returned invalid JSON:\n{text}"
            ) from e

        if "research_plan" in data:
            data = data["research_plan"]

        if "entity_type" not in data:
            data["entity_type"] = "AI trends"

        if "segment" not in data:
            data["segment"] = "General"

        if "geography" not in data:
            data["geography"] = "Global"

        if "time_horizon" not in data:
            data["time_horizon"] = "2026"

        if "deliverable_type" not in data:
            data["deliverable_type"] = "Research report"

        if "assumptions" not in data:
            data["assumptions"] = []

        if "ambiguities" not in data:
            data["ambiguities"] = []

        objectives = data.get("objectives", [])

        for objective_index, objective in enumerate(objectives):

            if not isinstance(objective, dict):
                objective = {
                    "id": f"O{objective_index + 1}",
                    "objective": str(objective),
                    "subquestions": [],
                }
                objectives[objective_index] = objective

            objective["id"] = f"O{objective_index + 1}"

            if "objective" not in objective:
                objective["objective"] = (
                    f"Research objective {objective_index + 1}"
                )

            subquestions = objective.get("subquestions", [])

            if not isinstance(subquestions, list):
                subquestions = [subquestions]

            objective["subquestions"] = subquestions

            for question_index, question in enumerate(subquestions):

                unique_id = (
                    f"O{objective_index + 1}_Q{question_index + 1}"
                )

                if isinstance(question, str):

                    objective["subquestions"][question_index] = {
                        "id": unique_id,
                        "question": question,
                        "evidence_types": ["fact"],
                        "candidate_tools": [
                            "search_information"
                        ],
                    }

                elif isinstance(question, dict):

                    question["id"] = unique_id

                    if "question" not in question:
                        question["question"] = str(
                            question.get("text", "")
                        )

                    if "evidence_types" not in question:
                        question["evidence_types"] = ["fact"]

                    if "candidate_tools" not in question:
                        question["candidate_tools"] = [
                            "search_information"
                        ]

                else:

                    objective["subquestions"][question_index] = {
                        "id": unique_id,
                        "question": str(question),
                        "evidence_types": ["fact"],
                        "candidate_tools": [
                            "search_information"
                        ],
                    }

        data["objectives"] = objectives

        allowed_evidence_types = {
            "fact",
            "comparison",
            "metric",
            "uncertainty",
        }

        evidence_type_mapping = {
            "forecast": "uncertainty",
            "trend analysis": "comparison",
            "time series": "metric",
            "market analysis": "comparison",
            "comparative assessment": "comparison",
            "impact estimate": "metric",
            "expert analysis": "fact",
            "adoption metric": "metric",
            "company evidence": "fact",
            "risk assessment": "uncertainty",
            "expert opinion": "uncertainty",
            "methodology": "fact",
            "score": "metric",
            "comparative analysis": "comparison",
            "ranking": "comparison",
            "sensitivity analysis": "uncertainty",
            "uncertainty assessment": "uncertainty",
            "synthesis": "fact",
            "source credibility": "fact",
            "citation": "fact",
            "scenario analysis": "uncertainty",
            "regional comparison": "comparison",
        }

        for objective in data.get("objectives", []):

            for question in objective.get("subquestions", []):

                evidence_types = question.get(
                    "evidence_types",
                    ["fact"]
                )

                normalized_types = []

                for evidence_type in evidence_types:

                    if not isinstance(evidence_type, str):
                        evidence_type = "fact"

                    evidence_type = evidence_type.lower().strip()

                    if evidence_type in allowed_evidence_types:
                        normalized_types.append(evidence_type)

                    elif evidence_type in evidence_type_mapping:
                        normalized_types.append(
                            evidence_type_mapping[evidence_type]
                        )

                    else:
                        normalized_types.append("fact")

                question["evidence_types"] = list(
                    dict.fromkeys(normalized_types)
                )

                if not question["evidence_types"]:
                    question["evidence_types"] = ["fact"]

        try:
            return ResearchPlan.model_validate(data)

        except Exception:
            print("\n--- PLANNER JSON ---")
            print(json.dumps(data, indent=2))
            print("--- END PLANNER JSON ---\n")
            raise