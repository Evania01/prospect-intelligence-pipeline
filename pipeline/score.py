def score_one_record(record):
    scored_record = dict(record)
    enrichment = scored_record.get("enrichment") or {}

    score = 0

    if enrichment.get("hiring_now") is True:
        score += 20

    employee_count = enrichment.get("employee_count")
    if employee_count:
        if employee_count >= 1000:
            score += 20
        elif employee_count >= 200:
            score += 15
        elif employee_count >= 50:
            score += 10
        else:
            score += 5

    funding_months = enrichment.get("last_funding_months_ago")
    if funding_months is not None:
        if funding_months <= 6:
            score += 20
        elif funding_months <= 12:
            score += 15
        elif funding_months <= 24:
            score += 10
        else:
            score += 5

    tech_signals = enrichment.get("tech_signals") or []
    score += min(len(tech_signals) * 5, 20)

    scored_record["score"] = score
    return scored_record


def score_records(records):
    scored_records = []

    for record in records:
        scored_record = score_one_record(record)
        scored_records.append(scored_record)

    scored_records.sort(key=lambda record: record.get("score", 0), reverse=True)
    return scored_records