import csv
import re
from datetime import datetime


def clean_text(value):
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    return value


def clean_domain(domain):
    domain = clean_text(domain)
    if not domain:
        return None

    domain = domain.lower()

    if domain.startswith("https://"):
        domain = domain[len("https://"):]
    elif domain.startswith("http://"):
        domain = domain[len("http://"):]

    if domain.startswith("www."):
        domain = domain[len("www."):]

    if domain.endswith("/"):
        domain = domain[:-1]

    return domain


def clean_email(email):
    email = clean_text(email)
    if not email:
        return None
    return email.lower()


def clean_country(country):
    country = clean_text(country)
    if not country:
        return None

    country = country.strip().lower()

    country_map = {
        "us": "United States",
        "usa": "United States",
        "u.s.a.": "United States",
        "united states": "United States",
        "uk": "United Kingdom",
        "united kingdom": "United Kingdom",
        "de": "Germany",
        "germany": "Germany",
        "ca": "Canada",
        "canada": "Canada",
        "in": "India",
        "india": "India",
        "australia": "Australia",
    }

    return country_map.get(country, country.title())


def clean_employee_count(value):
    value = clean_text(value)
    if not value:
        return None, None

    value = value.lower().strip()

    numbers = re.findall(r"\d+", value)
    if not numbers:
        return None, None

    numbers = [int(num) for num in numbers]

    if "+" in value:
        return numbers[0], None

    if "to" in value or "-" in value:
        if len(numbers) >= 2:
            return numbers[0], numbers[1]

    if len(numbers) == 1:
        return numbers[0], numbers[0]

    return None, None



def clean_date(value):
    value = clean_text(value)
    if not value:
        return None

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d %b %Y",
        "%d %B %Y",
        "%m/%d/%y",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None



def clean_record(row):
    employee_min, employee_max = clean_employee_count(row.get("employee_count"))
    return {
        "record_id": clean_text(row.get("record_id")),
        "company_name": clean_text(row.get("company_name")),
        "domain": clean_domain(row.get("domain")),
        "industry": clean_text(row.get("industry")),
        "employee_count_raw": clean_text(row.get("employee_count")),
        "employee_count_min": employee_min,
        "employee_count_max": employee_max,
        "country": clean_country(row.get("country")),
        "contact_email": clean_email(row.get("contact_email")),
        "source_captured_at_raw": clean_text(row.get("source_captured_at")),
        "source_captured_at_clean": clean_date(row.get("source_captured_at")),
    }


def load_raw_records(csv_path):
    records = []

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cleaned = clean_record(row)
            records.append(cleaned)

    return records