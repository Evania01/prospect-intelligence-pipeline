import json
import time
from urllib import error, request

API_URL = "http://localhost:8900/enrich"
MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 1


def enrich_one_record(record):
    enriched_record = dict(record)
    domain = enriched_record.get("domain")

    if not domain:
        enriched_record["enrichment_status"] = "skipped_no_domain"
        enriched_record["enrichment"] = None
        return enriched_record

    payload = json.dumps({"domain": domain}).encode("utf-8")

    api_request = request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with request.urlopen(api_request) as response:
                response_data = response.read().decode("utf-8")
                enrichment_data = json.loads(response_data)

            enriched_record["enrichment_status"] = "success"
            enriched_record["enrichment"] = enrichment_data
            enriched_record["retry_count"] = attempt - 1
            return enriched_record

        except error.HTTPError as exc:
            if exc.code in (429, 500) and attempt < MAX_RETRIES:
                time.sleep(RETRY_WAIT_SECONDS)
                continue

            enriched_record["enrichment_status"] = f"http_error_{exc.code}"
            enriched_record["enrichment"] = None
            enriched_record["retry_count"] = attempt - 1
            return enriched_record

        except error.URLError:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_WAIT_SECONDS)
                continue

            enriched_record["enrichment_status"] = "connection_error"
            enriched_record["enrichment"] = None
            enriched_record["retry_count"] = attempt - 1
            return enriched_record

    enriched_record["enrichment_status"] = "failed_after_retries"
    enriched_record["enrichment"] = None
    enriched_record["retry_count"] = MAX_RETRIES
    return enriched_record


def enrich_records(records):
    enriched_records = []

    for record in records:
        enriched_record = enrich_one_record(record)
        enriched_records.append(enriched_record)

    return enriched_records