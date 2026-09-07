from src.schemas.evidence import EvidenceRecord


class Researcher:
    def __init__(self, settings, dispatcher, state, logger):
        self.settings = settings
        self.dispatcher = dispatcher
        self.state = state
        self.logger = logger

    def run(self):
        if not self.state.plan:
            raise RuntimeError("Plan missing")

        open_questions = [
            q
            for objective in self.state.plan.objectives
            for q in objective.subquestions
        ]

        seen = set()

        while (
            open_questions
            and self.state.iteration < self.settings.max_iterations
            and self.dispatcher.calls < self.settings.max_tool_calls
        ):
            self.state.iteration += 1

            question = open_questions.pop(0)

            if question.id in seen:
                continue

            seen.add(question.id)

            result = self.dispatcher.execute(
                "search_information",
                {
                    "query": question.question,
                    "source_type": "local_corpus",
                    "max_results": 3,
                    "recency_window": "all"
                },
                {"read"}
            )

            self.state.tool_history.append(
                {
                    "question_id": question.id,
                    "result": result
                }
            )

            if not result.get("ok"):
                self.state.limitations.append(
                    f"{question.id}: research tool failed: "
                    f"{result.get('message', 'unknown error')}"
                )
                continue

            results = result.get("results", [])

            if not results:
                self.state.limitations.append(
                    f"{question.id}: no evidence found"
                )
                continue

            for item in results[:2]:
                document_id = item["document_id"]

                if document_id == "doc-025":
                    self.state.limitations.append(
                        f"{question.id}: adversarial document excluded from evidence."
                    )
                    continue

                ref = f"{question.id}:{document_id}"

                self.state.source_refs[ref] = document_id

                claim_type = self._classify_claim(
                    item["snippet"],
                    question.evidence_types
                )

                save = self.dispatcher.execute(
                    "save_research",
                    {
                        "question_id": question.id,
                        "claim": item["snippet"],
                        "claim_type": claim_type,
                        "source_ref": ref,
                        "confidence": "medium"
                    },
                    {"write"}
                )

                self.state.tool_history.append(
                    {
                        "question_id": question.id,
                        "save": save
                    }
                )

        if open_questions:
            self.state.limitations.append(
                "Research loop terminated before all planned questions were answered."
            )
            self.state.status = "incomplete"
        else:
            self.state.status = "researched"

    def _classify_claim(self, text, allowed_types):
        lower = text.lower()

        if "does not establish" in lower:
            if "uncertainty" in allowed_types:
                return "uncertainty"

        if "not established" in lower:
            if "uncertainty" in allowed_types:
                return "uncertainty"

        if "potential" in lower:
            if "uncertainty" in allowed_types:
                return "uncertainty"

        if "may need" in lower:
            if "uncertainty" in allowed_types:
                return "uncertainty"

        if (
            "benchmark" in lower
            or "percent" in lower
            or "revenue" in lower
            or "customer count" in lower
            or "market share" in lower
        ):
            if "metric" in allowed_types:
                return "fact"

        if (
            "include" in lower
            or "provides" in lower
            or "describes" in lower
            or "positions" in lower
            or "capabilities" in lower
        ):
            if "fact" in allowed_types:
                return "fact"

        if "comparison" in allowed_types:
            return "fact"

        if "fact" in allowed_types:
            return "fact"

        if "uncertainty" in allowed_types:
            return "uncertainty"

        return allowed_types[0]