#!/usr/bin/env python3
"""Clean and deduplicate CSV files."""
import csv


def clean_rows(rows):
    cleaned = []
    for row in rows:
        cells = [str(cell).strip() for cell in row]
        if any(cells):
            cleaned.append(cells)
    return cleaned


def normalize_headers(headers):
    normalized = []
    for header in headers:
        slug = header.strip().lower().replace(" ", "_")
        slug = "".join(char for char in slug if char.isalnum() or char == "_")
        normalized.append(slug or "column")
    return normalized


def dedupe(rows, key=None):
    seen = set()
    result = []
    for row in rows:
        marker = tuple(row) if key is None else row[key]
        if marker in seen:
            continue
        seen.add(marker)
        result.append(row)
    return result


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)


def clean_file(source, destination):
    """Clean a CSV file and return a small statistics dictionary."""
    rows = load_rows(source)
    if not rows:
        write_rows(destination, [])
        return {
            "headers": [],
            "rows_before": 0,
            "rows_after": 0,
            "duplicates_removed": 0,
        }
    headers = normalize_headers(rows[0])
    body = clean_rows(rows[1:])
    unique = dedupe(body)
    write_rows(destination, [headers] + unique)
    return {
        "headers": headers,
        "rows_before": len(rows) - 1,
        "rows_after": len(unique),
        "duplicates_removed": len(body) - len(unique),
    }
