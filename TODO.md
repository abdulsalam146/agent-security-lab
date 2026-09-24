# TODO

This file tracks the path from the current offline policy simulator to a reproducible live-agent security evaluation. The existing 28 fixtures supply proposed actions directly; they do not measure what a model would choose to do.

## P0 — Live-agent evaluation

- [ ] Define an adapter interface that accepts a user request and untrusted document, invokes a tool-capable model, and captures its **actual proposed tool calls** and final answer. Include a model identifier, configuration and run timestamp in the result.
- [ ] Add a first adapter for a local model/runtime. Keep model access optional so the offline simulator and tests still work without a model or network.
- [ ] Introduce an independent authorization context assembled by the host application. Never trust a model-provided `source: "user"` or approval claim.
- [ ] Intercept every proposed tool call before execution. Use synthetic resources and mock `read`/`send` tools for evaluations; record denied calls without performing their side effects.
- [ ] Classify each run separately: unsafe action attempted, unsafe action blocked or allowed, legitimate task completed, and no tool call. Keep model behavior separate from policy behavior.
- [ ] Run the existing attack documents against the live adapter and retain raw proposed-call traces. Review each fixture's expected behavior: a document alone cannot prove that a model would propose its prefilled action.
- [ ] Add tests with a deterministic fake adapter for allowed actions, blocked actions, multiple proposed calls, missing calls and malformed arguments.

**Done when:** One command runs the attack documents through a real model with mock tools, produces a report of observed actions and policy decisions, and makes no external send or private-file read.

## P1 — Stronger evaluation and controls

- [ ] Define legitimate task success criteria for each fixture so that an agent cannot receive a good score merely by refusing everything.
- [ ] Add tests for both false positives and false negatives, including authorized public reads and requests that still require approval.
- [ ] Replace the illustrative `public/<filename>` string check with canonical resource IDs and a documented authorization policy. Add tests for path aliases, traversal and malformed targets.
- [ ] Make policy decisions and tool execution separate interfaces. Document how a host supplies verified user identity, tenant, permissions and human approval.
- [ ] Record per-case latency, model/provider version, token usage and cost where the adapter exposes them.
- [ ] Version fixture sets and report schemas so results can be compared across runs.

**Done when:** Reports distinguish security outcomes from task quality and include enough configuration to reproduce a run.

## P2 — Open source usability

- [ ] Add a minimal example agent and a walkthrough showing where to intercept tool calls.
- [ ] Provide a sample live-agent report using synthetic inputs and a clearly identified model/configuration.
- [ ] Add CI for unit tests and package installation across supported Python versions.
- [ ] Invite independently reviewed fixtures and document how contributors justify expected outcomes.
- [ ] Add a short demo and results table to the README, with an explicit distinction between fixture results and live-model results.

## Guardrails

- Never run the intentionally unsafe baseline with real tools or secrets.
- Do not treat the current 28/28 protected fixture result as a live-model security score.
- Keep real credentials, customer data, and active external destinations out of fixtures and published traces.
