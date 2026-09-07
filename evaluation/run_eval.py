import json
from pathlib import Path

def main():
    cases=json.loads(Path(__file__).with_name("test_cases.json").read_text())
    results=[]
    for c in cases:
        results.append({"id":c["id"],"status":"NOT_RUN","note":"Execute the system and record observed behaviour; do not fabricate results."})
    out=Path(__file__).with_name("results")/"latest.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(results,indent=2))
    print(f"Created evaluation checklist for {len(results)} cases at {out}")
if __name__=="__main__": main()
