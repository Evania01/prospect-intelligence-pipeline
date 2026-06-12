# Architecture Note

## Overview

This project is a small backend prospect intelligence pipeline built in Python. It takes messy raw prospect data from a CSV file, cleans and normalizes the records, groups duplicate companies, enriches them using a mock external API, scores the results, and produces a final ranked output.

The pipeline is designed as a simple stage-by-stage process so that each part of the flow is easy to understand and inspect.

## Pipeline stages

### 1. Ingestion and normalization

The pipeline starts by reading `data/raw_prospects.csv`.

In this stage, the system:
- cleans text fields
- normalizes domains
- normalizes emails
- standardizes country values
- converts employee count values into min/max numeric fields
- converts different date formats into a single standard format

This stage is implemented in `pipeline/ingest.py`.

### 2. Duplicate grouping and merging

After records are cleaned, they are grouped by domain. Records with the same cleaned domain are treated as belonging to the same company group.

Each domain group is merged into one final record. For fields with multiple values, the current approach selects the first non-empty useful value.

Records without domains are kept separately and are not grouped by domain.

This stage is implemented in `pipeline/dedupe.py`.

### 3. Enrichment

Each merged record is enriched using the local mock API in `mock_enrichment_api/app.py`.

The pipeline sends the domain of each company to the API and stores the returned enrichment data. Records without domains are skipped.

The enrichment layer also handles temporary failures:
- retries for `429` rate-limit errors
- retries for `500` transient failures
- retry handling for connection problems

This stage is implemented in `pipeline/enrich.py`.

### 4. Scoring

After enrichment, each record is given a score based on enrichment signals. The current scoring logic uses:
- hiring status
- employee count
- funding recency
- number of tech signals

After scoring, records are sorted in descending order so the highest scoring prospects appear first.

This stage is implemented in `pipeline/score.py`.

### 5. Output and observability

The pipeline saves intermediate stage files in the `state/` folder:
- merged records
- enriched records
- scored records

It also creates a cleaner final output in:
- `output/final_ranked_prospects.json`

On reruns, the pipeline can reuse these saved `state/` files so completed stages do not need to be recalculated every time.

At the end of the run, it prints a summary showing:
- raw record count
- grouped domain count
- no-domain record count
- merged record count
- enrichment success, skipped, and failed counts
- failure reason breakdown
- final scored record count

This orchestration is handled in `main.py`.

## Key design decisions

### Domain-based duplicate grouping

I used cleaned domain values as the main duplicate grouping rule because domains are stronger identifiers than company names. Company names can vary a lot in casing, punctuation, and wording, but domains are usually more stable.

This approach is simple and reduces the chance of merging unrelated companies with similar names.

### Simple merge strategy

When merging grouped records, I selected the first non-empty useful value for each field. This is a simple strategy that keeps the implementation understandable and avoids overcomplicating conflict resolution.

### Retry-based enrichment handling

The enrichment API is intentionally unreliable, so I added retries for temporary errors. This makes the pipeline more robust and better aligned with the task’s backend reliability requirement.

### Stage-wise state saving

I saved intermediate results in the `state/` folder so each stage can be inspected separately. This also makes the pipeline easier to debug and allows reruns to reuse already completed stages.

## Trade-offs

The current implementation is intentionally simple and readable, but it has some trade-offs:

- duplicate detection is based mainly on domain, so records without domains are not merged intelligently
- merge conflict resolution is basic and may not always pick the best possible field value
- enrichment is sequential, not concurrent
- retry logic is simple and does not use exponential backoff
- the pipeline can reuse saved stage outputs on rerun, but it does not yet implement a full checkpoint system with validation or partial-stage recovery

These choices were made to keep the solution correct, understandable, and manageable within the task scope.

## What I would improve with more time

If I had more time, I would improve the project in these ways:

- add name-based fuzzy matching for no-domain duplicate records
- improve merge logic by selecting better values instead of only the first non-empty one
- add concurrent enrichment while respecting the rate limit
- add a dead-letter output for failed enrichment records
- add tests for ingestion, dedupe, and scoring logic
- add true resume/checkpoint behavior for interrupted runs
- expose the run summary as a structured report or endpoint
