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


def drop_empty_columns(rows):
    if not rows:
        return []
    width = max(len(row) for row in rows)
    keep = [
        index
        for index in range(width)
        if any(index < len(row) and str(row[index]).strip() for row in rows)
    ]
    return [
        [row[index] if index < len(row) else "" for index in keep]
        for row in rows
    ]


def fill_missing(rows, value=""):
    if not rows:
        return []
    width = max(len(row) for row in rows)
    return [
        list(row) + [value] * (width - len(row))
        for row in rows
    ]


def select_columns(rows, columns):
    if not rows:
        return []
    header = list(rows[0])
    indices = []
    for name in columns:
        if name not in header:
            raise ValueError(f"unknown column: {name}")
        indices.append(header.index(name))
    return [
        [row[index] if index < len(row) else "" for index in indices]
        for row in rows
    ]


def sort_rows(rows, column, reverse=False):
    if not rows:
        return []
    header = list(rows[0])
    if column not in header:
        raise ValueError(f"unknown column: {column}")
    index = header.index(column)
    body = [list(row) for row in rows[1:]]
    body.sort(
        key=lambda row: row[index] if index < len(row) else "",
        reverse=reverse,
    )
    return [header] + body


def load_rows(path, delimiter=","):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle, delimiter=delimiter))


def write_rows(path, rows, delimiter=","):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        csv.writer(handle, delimiter=delimiter).writerows(rows)


def clean_file(source, destination, delimiter=",", out_delimiter=None):
    """Clean a CSV file and return a small statistics dictionary."""
    if out_delimiter is None:
        out_delimiter = delimiter
    rows = load_rows(source, delimiter=delimiter)
    if not rows:
        write_rows(destination, [], delimiter=out_delimiter)
        return {
            "headers": [],
            "rows_before": 0,
            "rows_after": 0,
            "duplicates_removed": 0,
        }
    headers = normalize_headers(rows[0])
    body = clean_rows(rows[1:])
    unique = dedupe(body)
    write_rows(destination, [headers] + unique, delimiter=out_delimiter)
    return {
        "headers": headers,
        "rows_before": len(rows) - 1,
        "rows_after": len(unique),
        "duplicates_removed": len(body) - len(unique),
    }


def rename_columns(rows, mapping):
    """Rename header cells using a mapping, leaving unknown columns intact."""
    if not rows:
        return []
    header = [mapping.get(name, name) for name in rows[0]]
    return [header] + [list(row) for row in rows[1:]]
