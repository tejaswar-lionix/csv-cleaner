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
