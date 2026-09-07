class EvidenceAnalyst:
    def run(self,state):
        for e in state.evidence:
            if not e.source_ref or e.source_ref not in state.source_refs:
                e.confidence="low"
                e.analyst_notes="Rejected or downgraded because provenance does not resolve."
