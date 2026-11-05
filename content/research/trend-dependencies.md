---
title: 'Discovering trend dependencies in time-series data'
description: 'An accessible guide to trend dependencies, approximate constraints over evolving time series, with an explicitly synthetic experiment.'
year: '2023 / 2026 EXPLAINER'
number: 1
category: 'MSc RESEARCH / TIME SERIES'
ownership: 'Original MSc research'
status: 'Public thesis; synthetic interactive explainer'
format: 'Research article + interactive experiment'
public: true
exhibit: 'trend'
---
## Why time-series relationships are difficult

Many data constraints are written as if the world stays still: a key identifies one record, or an attribute determines another. Time-series data is less cooperative. Measurements fluctuate, trends shift, and relationships may only hold over particular windows or under particular conditions.

My MSc thesis, *Discovery of Trend Dependencies Over Time-Series*, explored a family of **approximate and conditional functional constraints** for evolving, noisy time series. Instead of insisting that every observation agrees with one exact expression, the approach asks which relationships can describe meaningful trends within suitable segments.

[Read the original thesis (Ontario Tech repository) ↗](https://ontariotechu.scholaris.ca/server/api/core/bitstreams/af2acd24-e895-43e3-8781-b04aca070e66/content)

## Global and segmented constraints

Suppose a measured variable `y` depends on time `t`. A simple global relationship might be written as `y ≈ f(t)`, with some allowance for observation noise. But a single `f` may become misleading after a change in process, measurement conditions, or underlying behavior.

A segmented alternative asks whether different functions better describe different intervals. The relevant questions are not merely *how low is the regression loss?* but also *where does the relationship hold?* and *what kind of deviation is meaningful?*

The original research considered segmentation, candidate filtering and sampling, transformer-based symbolic regression, and policy-gradient learning as ways to discover such structure. It explored potential uses in anomaly detection and missing-value estimation and evaluated approaches on synthetic and real-world time series.

## An example with a known breakpoint

The interactive exhibit below generates a **synthetic trend** using a fixed pseudo-random sequence. Move the controls to change the magnitude of noise, an abrupt level shift, or the residual tolerance used in a deliberately simple accept/reject rule. Toggle segmented fitting to see how fitting two lines can behave differently from a single global line.

This is **not a reimplementation of the thesis algorithm**. The browser performs ordinary least-squares line fitting and reports the fraction of invented data points within the selected residual threshold. It is meant to build intuition, not to reproduce published results or define the thesis's formal TD validity test.

## Three issues that matter when fitting a relationship

### 1. Choosing a function does not settle validity

A more flexible model may reduce error without producing a relationship that is understandable or stable. Research into symbolic forms asks whether useful structure can be expressed rather than merely predicted.

### 2. Segmentation changes the hypothesis

A single function for an entire sequence and a pair of functions over separate windows are different kinds of claims. A changepoint is not automatically an anomaly; it can be evidence that the data-generating process has changed.

### 3. Approximation requires explicit criteria

If a constraint admits some noise, what counts as sufficiently close? Any threshold changes what the system considers a violation. A rigorous implementation must state how candidates are scored, how segments are selected, and how evaluation avoids overfitting.

## Primary source

**Bode, Nicholas.** *Discovery of Trend Dependencies Over Time-Series.* MSc thesis, Ontario Tech University, November 2023. The public thesis is the source for the actual algorithms, definitions, experimental design, and results.

The interactive chart on this page is a new educational simplification based on the general idea; all displayed values are synthetic and should be interpreted only in that context.
