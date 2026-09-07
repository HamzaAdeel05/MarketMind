class QualityControl:
    def run(self,state,synthesis):
        defects=[]
        evidence_ids={e.evidence_id for e in state.evidence}
        for f in synthesis["findings"]:
            if f.claim_type=="fact" and not f.evidence_ids: defects.append({"severity":"high","type":"unsupported_claim","statement":f.statement})
            if any(eid not in evidence_ids for eid in f.evidence_ids): defects.append({"severity":"high","type":"missing_evidence","statement":f.statement})
        planned={q.id for o in state.plan.objectives for q in o.subquestions}
        answered={e.question_id for e in state.evidence}
        for q in sorted(planned-answered): defects.append({"severity":"medium","type":"coverage_gap","question_id":q})
        return {"pass":not any(d["severity"]=="high" for d in defects),"defects":defects}
