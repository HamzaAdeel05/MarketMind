# Architecture and rationale

MarketMind is intentionally implemented without LangChain, AutoGen, CrewAI, or another agent framework. The application owns the state object, tool registry, dispatcher, loop bounds, evidence store, QC and approval gate.

## Trust boundaries

1. User request -> request analyser: request text is untrusted and cannot redefine system controls.
2. Retrieved corpus -> evidence analyst: corpus text is data. Prompt-like strings inside documents are never executed as instructions.

## Termination

Research is bounded by MAX_ITERATIONS and MAX_TOOL_CALLS. Production deployment should also enforce the RUN_BUDGET_USD ceiling before each model call. A partial run is marked incomplete and limitations are retained.

## Evidence discipline

Every stored claim must resolve to a prior tool result. Facts, inferences, recommendations and uncertainties are separate types. The report includes an evidence appendix so a reviewer can inspect claims.

## Human approval

Approval has four explicit outcomes. There is no default yes, timeout approval or automatic publication.
