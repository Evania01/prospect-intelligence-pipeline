# Prospect Intelligence Pipeline

This project reads messy prospect company data from a CSV file, cleans and normalizes it, groups duplicate records, enriches companies using a mock API, scores the prospects, and produces a final ranked output.

## What the pipeline does

The pipeline runs in these stages:
1. Ingestion and normalization
2. Duplicate grouping and merging
3. Enrichment using the mock API
4. Scoring and ranking
5. Output generation and run summary

## Project structure

```text
prospect_pipeline/
├── main.py
├── README.md
├── AI_USAGE_LOG.md
├── data/
│   ├── raw_prospects.csv
│   └── raw_prospects_sample.json
├── mock_enrichment_api/
│   ├── app.py
│   └── requirements.txt
├── pipeline/
│   ├── ingest.py
│   ├── dedupe.py
│   ├── enrich.py
│   ├── score.py
│   └── utils.py
├── state/
│   ├── merged_records.json
│   ├── enriched_records.json
│   └── scored_records.json
└── output/
    ├── cleaned_records.json
    ├── enriched_records.json
    ├── scored_records.json
    └── final_ranked_prospects.json
```   
    
## Requirements

- Python 3.x
- pip

## How to run the mock enrichment API

Run this first:

cd mock_enrichment_api
pip install -r requirements.txt
uvicorn app:app --port 8900

The mock API runs at:
http://localhost:8900/enrich

## How to run the pipeline

After starting the mock API, open another terminal in the project root and run:

python main.py

## Output files

Final output:
- output/final_ranked_prospects.json

Intermediate state files:
- state/merged_records.json
- state/enriched_records.json
- state/scored_records.json

## Run summary

When the pipeline finishes, it prints:
- raw records count
- unique domain groups
- no-domain records
- merged records count
- enrichment success count
- enrichment skipped count
- enrichment failed count
- final scored records count

## Notes

- records with the same cleaned domain are grouped together
- records without domains are skipped for enrichment
- retry handling is included for temporary enrichment failures
- scoring is based on enrichment signals such as hiring status, employee count, funding recency, and tech signals