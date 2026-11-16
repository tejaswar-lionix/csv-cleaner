# csv-cleaner

Clean, normalize, and deduplicate CSV files.

## Usage

```bash
python3 -c "from cleaner import clean_file; print(clean_file('raw.csv', 'clean.csv'))"
python3 -c "from cleaner import clean_file; print(clean_file('raw.csv', 'clean.csv', delimiter=';', out_delimiter=','))"
```

## Features

- Trim cells and drop blank rows
- Normalize headers and deduplicate rows
- One-call cleanup with clean_file(source, destination)
- Custom input and output delimiters with load_rows, write_rows, and clean_file

## Tests

```bash
python3 -m unittest -q
```

## License

MIT
