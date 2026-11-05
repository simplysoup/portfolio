---
title: 'Evaluating a RAG system by the ways it can fail'
description: 'A reproducible document-QA experiment comparing a deterministic baseline with a bounded tool-using model.'
year: '2026'
number: 1
category: 'PUBLIC DEMO / APPLIED AI'
ownership: 'Independently developed'
status: 'Public repository; development benchmark, not production'
format: 'Engineering case study + educational trace'
public: true
exhibit: 'rag'
---
## The engineering question

When a language model gives a fluent answer, how do we know it was supported by the retrieved source? In a document-QA system, retrieval, citation validity, exact grounding, and abstention are different failure modes. Collapsing them into a single “accuracy” number can conceal which subsystem actually failed.

I built an **independent, synthetic-data document-QA demo** around those failure modes. I focused on the evaluation harness instead of building another chat interface. It contains eight fictional text documents, a fixed 30-question development set, a local TF-IDF retriever, an extractive baseline, an optional model-driven tool-user, six guardrail checks, and MLflow experiment tracking.

[Inspect the public source and evaluation protocol on GitHub ↗](https://github.com/simplysoup/evaluated-rag-agentic)

## Two configurations, one evaluation harness

**Deterministic baseline.** A fixed retrieve → extractive draft → check → answer/abstain workflow uses no LLM API. Source passages are chunked by sentence, indexed locally with TF-IDF, and returned with exact citations. It is inexpensive, reproducible, and intentionally limited.

**Tool-using configuration.** An optional model selects among three **read-only local tools** to search documents, fetch a document, or extract fields. After at most six tool calls, it must return an extractive, cited answer or abstain. The validator checks the proposed answer *against its cited chunk*, permits one corrective attempt after a grounding failure, and abstains if that attempt also fails. Tool errors and API failures are logged separately from ordinary abstentions.

The evaluation runs both configurations on the same synthetic questions and records whether added tool use changes correctness, latency, and cost.

## What the published development benchmark shows

The repository documents the following local runs. **The 30 questions were used during development**, not held out as a clean independent test; a one-question difference changes the percentage by 3.33 points. The second model run followed code changes, but is also a new nondeterministic run rather than a controlled A/B repeat.

| Configuration / run | Correct answers | Citation accuracy | Retrieval precision | Mean time / question |
| --- | ---: | ---: | ---: | ---: |
| Deterministic baseline | 28 / 30 | 100% | 0.689 | 0.003 s |
| Tool-using model, original run | 29 / 30 | 96.7% | 0.518 | 5.565 s |
| Tool-using model, revised run | 30 / 30 | 100% | 0.480 | 3.748 s |

The documented model-run estimated cost was approximately **US$0.0062 for each 30-question run** under the model prices recorded by the project. The baseline did not require an API key. These figures are narrow experimental observations, **not production reliability claims**.

## A grounding failure and a correction

The original model run included paraphrased answers that a strict source-grounding rule rejected, despite generally correct facts and citations. The follow-up implementation introduced a programmatic validator that verifies verbatim grounding, sends one corrective prompt if necessary, and abstains if the second attempt still cannot be justified.

The revised development run recorded two successful validator corrections. That is evidence about those particular traces, **not a general success-rate estimate**. It is equally notable that retrieval precision decreased even as answer correctness increased: collecting more candidate passages can improve the chance of finding support while making the retrieved set less precise.

The interactive explorer below uses **invented educational scenarios**, not copied execution logs. The repository remains the evidence source for actual tests, source code and measured runs.

## Design decisions

1. **Baseline first:** establish how much a constrained, non-LLM workflow can already do before introducing model flexibility.
2. **Guardrails in executable code:** make the answer contract testable rather than relying only on instructions inside a prompt.
3. **Distinct failure categories:** separate no-evidence abstention, incorrect citation, validator rejection, tool failure, and API error.
4. **Reproducible fixture:** choose a fictional document corpus so anyone can exercise the pipeline without disclosing private data.
5. **Measured tradeoffs:** compare correctness alongside retrieval precision, latency, cost, and intermediate steps.

## Limitations and next experiment

A small synthetic development set does not establish generalization to conflicting documents, adversarial prompts, long corpora, unseen organizations, or real users. Two model runs do not quantify nondeterministic variation. The next experiment should use held-out documents and repeated runs. I also want to replace the invented trace examples with records from a publicly releasable evaluation run.

**Source:** [Repository README, evaluation data, implementation and tests](https://github.com/simplysoup/evaluated-rag-agentic). No client work, private material, or deployment claims are part of this demo.
