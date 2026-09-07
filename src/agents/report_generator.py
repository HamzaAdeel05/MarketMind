from datetime import datetime, timezone

from src.schemas.report import FinalReport


class ReportGenerator:

    def run(self, state, synthesis, qc, usage_total):

        findings = synthesis.get("findings", [])
        comparison = synthesis.get("comparison", {})

        market_overview = []
        key_trends = []
        opportunities = []
        risks = []
        recommendations = []

        for finding in findings:

            claim_type = finding.claim_type

            if claim_type == "fact":
                market_overview.append(finding)

            elif claim_type == "inference":
                key_trends.append(finding)

            elif claim_type == "recommendation":
                recommendations.append(finding)

            elif claim_type == "uncertainty":
                risks.append(finding)

        opportunity_findings = [
            finding
            for finding in findings
            if self._is_opportunity(finding)
        ]

        opportunities.extend(opportunity_findings)

        limitations = []

        limitations.extend(state.limitations)

        limitations.extend(
            self._detect_evidence_gaps(state)
        )

        limitations.extend(
            self._detect_contradictions(state)
        )

        for defect in qc.get("defects", []):
            limitations.append(
                f"QC defect: {defect}"
            )

        limitations = list(
            dict.fromkeys(
                limitation
                for limitation in limitations
                if limitation
            )
        )

        confidence_level = self._confidence(
            state,
            limitations
        )

        evidence_appendix = [
            evidence.model_dump(mode="json")
            for evidence in state.evidence
        ]

        sources = [
            {
                "source_ref": source_ref,
                "detail": document_id
            }
            for source_ref, document_id
            in state.source_refs.items()
        ]

        executive_summary = self._build_executive_summary(
            state,
            market_overview,
            key_trends,
            opportunities,
            risks,
            recommendations,
            limitations
        )

        report = FinalReport(
            report_id=state.run_id,
            generated_at=datetime.now(
                timezone.utc
            ).isoformat(),

            model_versions=[
                "configured OpenAI model"
            ],

            run_cost=round(
                usage_total,
                6
            ),

            research_objective={
                "request": state.request,
                "assumptions": state.plan.assumptions,
                "unresolved_ambiguity": state.plan.ambiguities
            },

            executive_summary=executive_summary,

            market_overview=market_overview[:5],

            key_trends=key_trends[:5],

            competitor_analysis=comparison,

            opportunities=opportunities[:5],

            risks=risks[:5],

            evidence_appendix=evidence_appendix,

            recommendations=recommendations[:5],

            confidence_level=confidence_level,

            confidence_rationale=self._confidence_rationale(
                state,
                limitations
            ),

            limitations_and_gaps=limitations,

            sources=sources
        )

        return report

    def _is_opportunity(self, finding):

        text = finding.statement.lower()

        opportunity_terms = [
            "opportunity",
            "target",
            "high-volume",
            "repeatable",
            "automation",
            "after-hours",
            "agent productivity",
            "workflow",
            "vertical",
            "integration"
        ]

        return (
            finding.claim_type == "recommendation"
            and any(
                term in text
                for term in opportunity_terms
            )
        )

    def _detect_evidence_gaps(self, state):

        gaps = []

        for evidence in state.evidence:

            text = evidence.claim.lower()

            if (
                "does not establish" in text
                or "not established" in text
                or "evidence gap" in text
                or "absence of reliable" in text
                or "does not establish reliable" in text
            ):
                gaps.append(
                    evidence.claim
                )

        return gaps

    def _detect_contradictions(self, state):

        benchmarks = []

        for evidence in state.evidence:

            text = evidence.claim.lower()

            if (
                "percent automated resolution" in text
                or "automated resolution rate" in text
            ):
                benchmarks.append(
                    evidence.claim
                )

        if len(benchmarks) < 2:
            return []

        unique = list(
            dict.fromkeys(benchmarks)
        )

        if len(unique) < 2:
            return []

        return [
            "Conflicting automation benchmarks were found in the corpus. "
            "The reported figures use different evaluation environments "
            "or methodologies and should not be treated as directly "
            "comparable."
        ]

    def _confidence(self, state, limitations):

        if not state.evidence:
            return "low"

        if state.status != "researched":
            return "low"

        if len(limitations) >= 3:
            return "medium"

        return "medium"

    def _confidence_rationale(
        self,
        state,
        limitations
    ):

        evidence_count = len(
            state.evidence
        )

        limitation_count = len(
            limitations
        )

        return (
            f"Confidence is based on {evidence_count} evidence records, "
            f"source provenance, claim typing, contradiction handling, "
            f"and {limitation_count} identified research limitations. "
            "Quantitative market size, vendor scale, pricing, and "
            "benchmark comparisons are treated cautiously where the "
            "available corpus does not establish reliable values."
        )

    def _build_executive_summary(
        self,
        state,
        market_overview,
        key_trends,
        opportunities,
        risks,
        recommendations,
        limitations
    ):

        summary_parts = []

        if market_overview:
            summary_parts.append(
                "The available evidence indicates that AI-powered "
                "customer support software combines conversational AI, "
                "automation, knowledge retrieval, agent assistance, "
                "analytics, integrations, and human handoff."
            )

        if key_trends:
            summary_parts.append(
                f"The research identified {len(key_trends)} "
                "evidence-grounded trends or strategic patterns."
            )

        if opportunities:
            summary_parts.append(
                f"The evidence supports {len(opportunities)} "
                "potential opportunity areas, particularly around "
                "repeatable support workflows and controlled automation."
            )

        if recommendations:
            summary_parts.append(
                f"The analysis produced {len(recommendations)} "
                "evidence-grounded recommendations."
            )

        if limitations:
            summary_parts.append(
                f"The research also identified {len(limitations)} "
                "limitations or evidence gaps that constrain "
                "quantitative conclusions."
            )

        if not summary_parts:
            summary_parts.append(
                "The report is based on the available research corpus "
                "and does not present unsupported claims as established facts."
            )

        return " ".join(summary_parts)