import csv
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


def save_csv_file(path, records):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not records:
        with open(output_path, "w", encoding="utf-8", newline="") as file:
            file.write("")
        return

    fieldnames = list(records[0].keys())

    with open(output_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for record in records:
            csv_record = {}
            for key, value in record.items():
                if isinstance(value, list):
                    csv_record[key] = "|".join(str(item) for item in value)
                else:
                    csv_record[key] = value
            writer.writerow(csv_record)


def load_json_file(path):
    input_path = Path(path)
    if not input_path.exists():
        return None

    with open(input_path, "r", encoding="utf-8") as file:
        return json.load(file)


def print_run_summary(raw_records, grouped_records, no_domain_records, merged_records, enriched_records, scored_records):
    success_count = 0
    failed_count = 0
    skipped_count = 0
    failure_reasons = {}

    for record in enriched_records:
        status = record.get("enrichment_status")

        if status == "success":
            success_count += 1
        elif status == "skipped_no_domain":
            skipped_count += 1
        else:
            failed_count += 1
            failure_reasons[status] = failure_reasons.get(status, 0) + 1

    print("\nRun Summary")
    print("-----------")
    print("Raw records:", len(raw_records))
    print("Unique domain groups:", len(grouped_records))
    print("No-domain records:", len(no_domain_records))
    print("Merged records:", len(merged_records))
    print("Enriched success:", success_count)
    print("Enriched skipped:", skipped_count)
    print("Enriched failed:", failed_count)

    if failure_reasons:
        print("Failure reasons:")
        for reason, count in sorted(failure_reasons.items()):
            print(f"  {reason}: {count}")

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
    merged_state_path = "state/merged_records.json"
    enriched_state_path = "state/enriched_records.json"
    scored_state_path = "state/scored_records.json"

    print("Total records loaded:", len(records))
    print("First 5 cleaned records:")

    for record in records[:5]:
        print(record)

    grouped_records, no_domain_records = group_records_by_domain(records)

    print("Unique domains:", len(grouped_records))
    print("Records with no domain:", len(no_domain_records))

    merged_records = load_json_file(merged_state_path)
    if merged_records is None:
        merged_records = merge_grouped_records(grouped_records, no_domain_records)
        save_json_file(merged_state_path, merged_records)
        print("Merged records count:", len(merged_records))
    else:
        print("Loaded merged records from state/merged_records.json")
        print("Merged records count:", len(merged_records))

    enriched_records = load_json_file(enriched_state_path)
    if enriched_records is None:
        enriched_records = enrich_records(merged_records)
        save_json_file(enriched_state_path, enriched_records)
        print("Enriched records count:", len(enriched_records))
    else:
        print("Loaded enriched records from state/enriched_records.json")
        print("Enriched records count:", len(enriched_records))

    scored_records = load_json_file(scored_state_path)
    if scored_records is None:
        scored_records = score_records(enriched_records)
        save_json_file(scored_state_path, scored_records)
        print("Scored records count:", len(scored_records))
    else:
        print("Loaded scored records from state/scored_records.json")
        print("Scored records count:", len(scored_records))

    final_output = build_final_output(scored_records)

    save_json_file("output/final_ranked_prospects.json", final_output)
    save_csv_file("output/final_ranked_prospects.csv", final_output)

    print("Final ranked prospects saved to output/final_ranked_prospects.json")
    print("Final ranked prospects saved to output/final_ranked_prospects.csv")

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
