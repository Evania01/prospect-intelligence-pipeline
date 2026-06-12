def group_records_by_domain(records):
    grouped = {}
    no_domain_records = []

    for record in records:
        domain = record.get("domain")

        if domain:
            if domain not in grouped:
                grouped[domain] = []
            grouped[domain].append(record)
        else:
            no_domain_records.append(record)

    return grouped, no_domain_records


def choose_best_value(values):
    cleaned_values = [value for value in values if value not in (None, "")]
    if not cleaned_values:
        return None
    return cleaned_values[0]


def merge_record_group(records):
    return {
        "record_ids": [record["record_id"] for record in records if record.get("record_id")],
        "company_name": choose_best_value([record.get("company_name") for record in records]),
        "domain": choose_best_value([record.get("domain") for record in records]),
        "industry": choose_best_value([record.get("industry") for record in records]),
        "employee_count_min": choose_best_value([record.get("employee_count_min") for record in records]),
        "employee_count_max": choose_best_value([record.get("employee_count_max") for record in records]),
        "country": choose_best_value([record.get("country") for record in records]),
        "contact_email": choose_best_value([record.get("contact_email") for record in records]),
        "source_captured_at_clean": choose_best_value(
            [record.get("source_captured_at_clean") for record in records]
        ),
        "merged_record_count": len(records),
    }


def merge_grouped_records(grouped_records, no_domain_records):
    merged_records = []

    for domain, records in grouped_records.items():
        merged_records.append(merge_record_group(records))

    for record in no_domain_records:
        merged_records.append(
            {
                "record_ids": [record.get("record_id")] if record.get("record_id") else [],
                "company_name": record.get("company_name"),
                "domain": record.get("domain"),
                "industry": record.get("industry"),
                "employee_count_min": record.get("employee_count_min"),
                "employee_count_max": record.get("employee_count_max"),
                "country": record.get("country"),
                "contact_email": record.get("contact_email"),
                "source_captured_at_clean": record.get("source_captured_at_clean"),
                "merged_record_count": 1,
            }
        )

    return merged_records