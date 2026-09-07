# MarketMind AI — Autonomous Business Research Agent

A from-scratch Python implementation of the MarketMind capstone. It implements request analysis, research planning, a bounded plan–act–observe loop, strict tool dispatch, evidence provenance, comparison, synthesis, automated QC, a bounded repair loop, human approval, run logging, and evaluation scaffolding.

> Academic note: this is an implementation scaffold for the assignment. You must run it yourself, inspect every generated report, execute the evaluation, take your own screenshots, and be able to explain the code in the viva.

## Architecture

```text
User Request
    |
    v
Request Analyser -> Research Plan -> Bounded Research Loop
                                      |
                              +-------+--------+
                              | Tool Dispatcher |
                              +---+---+---+----+
                                  |   |   |
                         Search/Retrieve/Calculate
                                  |
                           Evidence Store
                                  |
                     Comparison -> Synthesis -> QC
                                             |
                                     <= 2 repair rounds
                                             |
                                      Report Generator
                                             |
                                      HUMAN APPROVAL
                                             |
                                      approve/reject/
                                      expand/modify
```

## Quick start

1. Python 3.11+ is recommended.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it and install: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
5. For a deterministic no-API smoke run, set `USE_OPENAI=false`.
6. Run: `python -m src.main --request "Compare AI coding assistants for enterprise adoption in 2026."`
7. The system writes an auditable JSON artifact under `runs/<run_id>/` and asks for an explicit approval decision.

## Important design choices

- No agent framework is used.
- Model output is validated with Pydantic and cross-field invariants are checked in application code.
- Search/retrieval evidence comes from the local curated corpus in `samples/corpus.json`; the model is not allowed to invent retrieved evidence.
- Tool arguments are validated before execution and additional properties are rejected.
- Write tools require explicit stage permissions.
- Research loops stop on iteration, tool-call, cost, or stuck-loop limits.
- Tool errors are returned as structured observations instead of crashing the loop.
- Reports are not considered publishable until a human chooses `approve`.
- Credentials are read from environment variables and never written to run logs.

## Current API verification

The assignment explicitly requires checking current OpenAI documentation on implementation day. This project uses the official Python SDK and the Responses API. Before submission, re-check the exact SDK/model/structured-output patterns against the current official docs and update `docs/api_verification.md` with the date and versions you actually used.

## Evaluation

`evaluation/test_cases.json` contains the 18 required behavioural cases as inputs and expected outcomes. `python -m evaluation.run_eval` executes the local deterministic checks. Cases involving stochastic model behaviour should be repeated at least three times and reported with observed pass rates, not invented results.
