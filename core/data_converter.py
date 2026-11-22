"""Lightweight structured data conversions between CSV, XLSX, and JSON without pandas."""

import csv
import json
from pathlib import Path
from typing import Any
import openpyxl


def _read_csv(src: Path) -> list[list[str]]:
    """Read CSV file with dialect sniffing and utf-8 / fallback encoding."""
    encodings = ["utf-8-sig", "utf-8", "latin-1"]
    content = None
    for enc in encodings:
        try:
            content = src.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    if content is None:
        raise ValueError(f"Unable to decode CSV file with supported encodings: {src.name}")

    if not content.strip():
        return []

    # Attempt delimiter detection
    try:
        sample = content[:4096]
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except Exception:
        dialect = csv.excel

    rows = []
    reader = csv.reader(content.splitlines(), dialect=dialect)
    for row in reader:
        rows.append(row)
    return rows


def _read_xlsx(src: Path) -> list[list[Any]]:
    """Read active sheet of Excel workbook."""
    wb = openpyxl.load_workbook(src, data_only=True, read_only=True)
    sheet = wb.active
    rows: list[list[Any]] = []
    if sheet is None:
        wb.close()
        return rows

    for row in sheet.iter_rows(values_only=True):
        rows.append(list(row))
    wb.close()
    return rows


def _read_json(src: Path) -> list[list[Any]]:
    """Read JSON array or list of objects into tabular 2D row structure."""
    data = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        if isinstance(data, dict):
            data = [data]
        else:
            raise ValueError("JSON file must contain an array or object of records.")

    if not data:
        return []

    # Case 1: List of dicts
    if isinstance(data[0], dict):
        # Collect all unique keys in order
        headers = []
        for item in data:
            if isinstance(item, dict):
                for k in item.keys():
                    if k not in headers:
                        headers.append(k)
        rows: list[list[Any]] = [headers]
        for item in data:
            if isinstance(item, dict):
                rows.append([item.get(h, "") for h in headers])
        return rows

    # Case 2: List of lists
    if isinstance(data[0], (list, tuple)):
        return [list(r) for r in data]

    # Case 3: Primitive list
    return [["Value"]] + [[str(x)] for x in data]


def _write_csv(rows: list[list[Any]], dst: Path) -> None:
    with open(dst, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        for r in rows:
            writer.writerow(["" if c is None else str(c) for c in r])


def _write_xlsx(rows: list[list[Any]], dst: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    if ws is not None:
        ws.title = "Data"
        for r in rows:
            ws.append(["" if c is None else c for c in r])
    wb.save(dst)
    wb.close()


def _write_json(rows: list[list[Any]], dst: Path) -> None:
    if not rows:
        dst.write_text("[]", encoding="utf-8")
        return

    # Check if first row can serve as headers
    headers = [str(c) if c is not None else f"col_{idx}" for idx, c in enumerate(rows[0])]
    records = []
    for r in rows[1:]:
        rec = {}
        for idx, h in enumerate(headers):
            val = r[idx] if idx < len(r) else None
            rec[h] = val
        records.append(rec)

    dst.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def convert_data(input_path: Path | str, output_path: Path | str) -> Path:
    """Convert structured data between CSV, XLSX, and JSON."""
    src = Path(input_path).resolve()
    dst = Path(output_path).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    src_ext = src.suffix.lower()
    dst_ext = dst.suffix.lower()

    # Load source into rows
    if src_ext == ".csv":
        rows = _read_csv(src)
    elif src_ext == ".xlsx":
        rows = _read_xlsx(src)
    elif src_ext == ".json":
        rows = _read_json(src)
    else:
        raise ValueError(f"Unsupported data source extension: {src_ext}")

    # Write target
    if dst_ext == ".csv":
        _write_csv(rows, dst)
    elif dst_ext == ".xlsx":
        _write_xlsx(rows, dst)
    elif dst_ext == ".json":
        _write_json(rows, dst)
    else:
        raise ValueError(f"Unsupported data target extension: {dst_ext}")

    return dst
