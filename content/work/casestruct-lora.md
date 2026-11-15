---
title: 'CaseStruct-LoRA: evaluating incident-text classification'
description: 'An exploratory LoRA study with paired bootstrap comparisons and explicit holdout limits.'
year: '2026'
number: 6
category: 'PUBLIC DEMO / MACHINE LEARNING'
ownership: 'Independently developed'
status: 'Public repository; exploratory study, not validated for deployment'
format: 'Engineering case study'
public: true
summary:
  problem: "Can a small LoRA-adapted model beat its strongest evaluated baseline on incident-text classification, and how certain is the difference?"
  built: "Qwen3-0.6B LoRA (rank 8, alpha 16) with a paired-bootstrap comparison (10,000 resamples, seed 71) against the strongest evaluated baseline per task."
  result: "ConstructCIE accident type +11.0 points (93.1% vs 82.1% macro-F1, 80 cases, 95% CI +1.7 to +21.1); OSHA injury nature +16.0 points (80.1% vs 64.0%, 333 cases, 95% CI +9.2 to +22.1)."
  limitation: "The test split was inspected during development, so it is not a pristine holdout; the source-only distribution does not independently reproduce the v2.1 outputs."
  evidence: "Public repository: methodology, aggregate results and code; per-example reports stay local."
---
## The engineering question

Can a small adapted language model classify incident narratives better than its strongest evaluated baseline, and how much uncertainty remains in that comparison? I built CaseStruct-LoRA to study the training and evaluation path rather than to claim that a model is ready to make safety decisions.

The external tasks are construction accident type and occupational injury nature. Neither external benchmark is a legal-document dataset. The project also retains an earlier synthetic legal-intake prototype as historical work; it should not be confused with the external task results. The reported outcomes are exploratory.

## What I built

I adapted Qwen3-0.6B with LoRA using PEFT and TRL. The adapter configuration used rank 8 and alpha 16. The prompt/completion training path used `completion_only_loss=True`, and the saved training run used offline Weights & Biases logging. The repository describes checks on the training mask; those checks cover the code path, not independent proof of the historical training run or checkpoint provenance.

I built preparation, evaluation and reporting workflows around the two tasks. The analysis compares the adapted model against evaluated alternatives rather than reporting a result in isolation. Constrained label scoring evaluates candidate labels, whereas a generated response has a different output contract. That distinction matters when comparing classification results with free-form model output.

The original code is MIT licensed. That license does not extend to the external datasets, base-model weights or other third-party materials. The repository does not distribute adapters or datasets, and per-example reports with source narratives remain local.

## How it was measured

I compared macro-F1 on each task against the strongest evaluated non-v2 baseline. Macro-F1 gives each class equal weight in the aggregate rather than letting the most common class alone dominate the result. I used paired bootstrap resampling over case IDs to estimate uncertainty in the difference, with 10,000 resamples and seed 71. The 95% intervals are paired comparisons for the reported cases, not assurances that future data will behave the same way.

The strongest-baseline selection was retrospective. The tasks should not be averaged: they involve different datasets, label meanings and sample sizes. In particular, injury codes may not always be inferable from a short narrative. That is a limit on the task itself, not necessarily a model error that more fluent output can resolve.

The README describes regeneration of evaluation results using saved adapters and prepared splits, without retraining. The source-only distribution does not independently reproduce the exploratory v2.1 outputs because the required adapters and prepared data are not included. A reader should follow the repository's prerequisites and provenance before treating an aggregate figure as a reproducible run.

## Results

For ConstructCIE accident type, the test set had 80 cases. The strongest non-v2 baseline was v1 zero-shot at 82.1% macro-F1; v2 constrained scoring reached 93.1%, a gain of 11.0 percentage points. Its paired 95% interval was [+1.7, +21.1] percentage points. With only 80 cases, that result is suggestive rather than conclusive.

For OSHA injury nature, the test set had 333 cases. The strongest baseline was base few-shot at 64.0% macro-F1; v2 constrained scoring reached 80.1%, a gain of 16.0 percentage points. Its paired 95% interval was [+9.2, +22.1] percentage points. The figures are task-specific and should not be combined into a single performance claim.

These comparisons help show why the baseline matters. Comparing only with an unmodified zero-shot model would not answer whether the adapter improves on the strongest tested alternative. The intervals add context to the point estimates, but they cannot repair leakage from inspecting the test set or establish generalization to a different population.

## Limits & what this does not show

The v2 test set was inspected during development and is not a pristine holdout. The v2.1 results are exploratory, and the source-only distribution does not independently reproduce them. ConstructCIE has only 80 test cases. Near-duplicates, label noise and information missing from narratives remain possible. The repository's audit is not proof that semantic leakage is absent.

The system is not validated for legal, clinical or safety-critical use. Public accident narratives can contain sensitive information; source terms and privacy matter when handling raw data, predictions and artifacts. Reporting aggregate metrics instead of publishing narratives reduces disclosure but does not replace a responsible data review.

A stronger next evaluation would freeze the model, label mapping and analysis plan before collecting a clean holdout. It would report each task separately and preserve the paired comparison, including uncertainty and failures, instead of promoting the exploratory score into a deployment claim.

## Source

[Public CaseStruct-LoRA README, methodology, aggregate results and code ↗](https://github.com/simplysoup/casestruct-lora)
