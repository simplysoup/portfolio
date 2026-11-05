---
title: 'Testing incremental models with dbt and DuckDB'
description: 'A local DuckDB + dbt analytics pipeline that makes incremental correctness and data-quality failures visible.'
year: '2026'
number: 2
category: 'PUBLIC DEMO / DATA ENGINEERING'
ownership: 'Independently developed'
status: 'Public repository; locally verified synthetic-data demo'
format: 'Engineering case study'
public: true
---
## The problem

An incremental warehouse model looks simple until an old order changes, a duplicate arrives, a null value appears, or a source row disappears. I built a small local test to verify those cases without paid infrastructure or confidential data.

This independently built demonstration uses **synthetic orders and customers**, Python ingestion, DuckDB, dbt transformations and tests, and CI. The repository contains setup instructions, integration tests, lineage and documented design tradeoffs.

[Explore the public project, tests, and design notes ↗](https://github.com/simplysoup/analytics-pipeline-dbt)

## Data flow and ownership boundaries

1. **Generate data:** deterministic synthetic records, with duplicates, null quantities, late-arriving orders, and a small customer dimension.
2. **Ingest:** Python loads the complete CSV snapshots into DuckDB using `CREATE OR REPLACE`. This stage is *idempotent snapshot loading*, not incremental ingestion.
3. **Stage and normalize:** dbt views deduplicate source records, preserve intentionally null quantities, and standardize types.
4. **Transform:** an intermediate view calculates amounts and flags null quantities. The customer dimension is kept separate rather than copying mutable attributes onto order facts.
5. **Incremental fact:** `fct_orders` merges over the full staging set on `order_id`, updating changed historical orders and inserting new ones.
6. **Test and report:** tests gate the build; JSON run logging and integration checks expose behavior after a changed source.

## Testing the update semantics

The project documents a local integration test that modifies a historical record, inserts a late order and a duplicate, introduces null cases, reruns the pipeline, and checks the resulting warehouse state. A second unchanged run is checked for duplicate-free idempotency.

| Contract | Why it matters |
| --- | --- |
| `order_id` merge key | A changed historical order replaces its former fact state |
| Source-relative freshness | Staleness is evaluated against actual input, not an arbitrary calendar offset |
| Customer dimension | Avoids duplicating mutable customer attributes inside the fact table |
| Null-quantity warning | Known sample problems remain inspectable rather than silently disappearing |
| Failing tests gate CI | Schema or data errors can stop a build instead of becoming green dashboards |
| Idempotency integration test | Repeat runs should not generate additional facts |

The README documents **18 dbt tests** and a verified run with **PASS=22, WARN=1** across models and test nodes. Its integration check reports a restored baseline of 1,010 fact rows and a mutated run of 1,012; the repeated mutated run remained at 1,012. These numbers describe only the repository's small, generated fixtures.

## Tradeoffs and known limitations

The full-staging merge prioritizes correctness and simple reasoning over optimized large-scale warehouse throughput. It **does not delete** target facts whose source records vanish. Snapshot ingestion also reloads the entire raw dataset each time; it does not track an ingestion watermark.

DuckDB is the **tested** target. The README discusses Snowflake compatibility as a possible adaptation, but does not claim that this project has actually run there. Airflow is represented by a demo DAG, not a continuously operated scheduler.

## What the tests establish

The tests check what happens when an existing order changes, when a duplicate is inserted, and when the same input runs twice. Those are the cases that would make this pipeline fail silently without explicit checks.

**Source:** [Repository, README and architectural tradeoff notes](https://github.com/simplysoup/analytics-pipeline-dbt). This is a local demonstration and not an employer or production pipeline.
