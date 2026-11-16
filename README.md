# csv-cleaner

Clean, normalize, and deduplicate CSV files.

## Usage

```bash
python3 -c "from cleaner import clean_file; print(clean_file('raw.csv', 'clean.csv'))"
python3 -c "from cleaner import clean_file; print(clean_file('raw.csv', 'clean.csv', delimiter=';', out_delimiter=','))"
python3 -c "from cleaner import select_columns; print(select_columns([['name', 'score'], ['ada', '10']], ['score']))"
```

## Features

- Trim cells and drop blank rows
- Normalize headers and deduplicate rows
- Drop empty columns with drop_empty_columns(rows)
- Select and reorder columns with select_columns(rows, columns)
- One-call cleanup with clean_file(source, destination)
- Custom input and output delimiters with load_rows, write_rows, and clean_file

## Tests

```bash
python3 -m unittest -q
```

## License

MIT
