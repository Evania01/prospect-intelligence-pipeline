import json
from pathlib import Path

from pipeline.dedupe import group_records_by_domain, merge_grouped_records
from pipeline.enrich import enrich_records
from pipeline.ingest import load_raw_records
from pipeline.score import score_records


def save_json_file(path, data):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

def print_run_summary(raw_records, grouped_records, no_domain_records, merged_records, enriched_records, scored_records):
    success_count = 0
    failed_count = 0
    skipped_count = 0

    for record in enriched_records:
        status = record.get("enrichment_status")

        if status == "success":
            success_count += 1
        elif status == "skipped_no_domain":
            skipped_count += 1
        else:
            failed_count += 1

    print("\nRun Summary")
    print("-----------")
    print("Raw records:", len(raw_records))
    print("Unique domain groups:", len(grouped_records))
    print("No-domain records:", len(no_domain_records))
    print("Merged records:", len(merged_records))
    print("Enriched success:", success_count)
    print("Enriched skipped:", skipped_count)
    print("Enriched failed:", failed_count)
    print("Final scored records:", len(scored_records))


def build_final_output(scored_records):
    final_records = []

    for record in scored_records:
        enrichment = record.get("enrichment") or {}

        final_records.append(
            {
                "record_ids": record.get("record_ids"),
                "company_name": record.get("company_name"),
                "domain": record.get("domain"),
                "country": record.get("country"),
                "industry": record.get("industry") or enrichment.get("industry"),
                "employee_count_min": record.get("employee_count_min"),
                "employee_count_max": record.get("employee_count_max"),
                "contact_email": record.get("contact_email"),
                "source_captured_at_clean": record.get("source_captured_at_clean"),
                "merged_record_count": record.get("merged_record_count"),
                "enrichment_status": record.get("enrichment_status"),
                "retry_count": record.get("retry_count"),
                "hiring_now": enrichment.get("hiring_now"),
                "founded_year": enrichment.get("founded_year"),
                "revenue_band": enrichment.get("revenue_band"),
                "tech_signals": enrichment.get("tech_signals"),
                "last_funding_months_ago": enrichment.get("last_funding_months_ago"),
                "score": record.get("score"),
            }
        )

    return final_records


def main():
    csv_path = "data/raw_prospects.csv"
    records = load_raw_records(csv_path)

    print("Total records loaded:", len(records))
    print("First 5 cleaned records:")

    for record in records[:5]:
        print(record)

    grouped_records, no_domain_records = group_records_by_domain(records)

    print("Unique domains:", len(grouped_records))
    print("Records with no domain:", len(no_domain_records))

    merged_records = merge_grouped_records(grouped_records, no_domain_records)

    print("Merged records count:", len(merged_records))
    save_json_file("state/merged_records.json", merged_records)

    enriched_records = enrich_records(merged_records)

    print("Enriched records count:", len(enriched_records))
    save_json_file("state/enriched_records.json", enriched_records)

    scored_records = score_records(enriched_records)

    print("Scored records count:", len(scored_records))
    save_json_file("state/scored_records.json", scored_records)

    final_output = build_final_output(scored_records)

    save_json_file("output/final_ranked_prospects.json", final_output)

    print("Final ranked prospects saved to output/final_ranked_prospects.json")

    print_run_summary(
        records,
        grouped_records,
        no_domain_records,
        merged_records,
        enriched_records,
        scored_records,
    )


if __name__ == "__main__":
    main()
