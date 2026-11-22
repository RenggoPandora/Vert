import json
from pathlib import Path
import openpyxl
from core.data_converter import convert_data


def test_csv_to_xlsx(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("name,score,active\nAlice,95,True\nBob,80,False\n", encoding="utf-8")

    xlsx_file = tmp_path / "sample.xlsx"
    out = convert_data(csv_file, xlsx_file)

    assert out.exists()
    wb = openpyxl.load_workbook(out)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    assert rows[0] == ("name", "score", "active")
    assert rows[1] == ("Alice", "95", "True")
    wb.close()


def test_xlsx_to_csv(tmp_path):
    xlsx_file = tmp_path / "test.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["id", "product", "price"])
    ws.append([1, "Widget", 19.99])
    wb.save(xlsx_file)
    wb.close()

    csv_file = tmp_path / "test.csv"
    out = convert_data(xlsx_file, csv_file)

    assert out.exists()
    content = out.read_text(encoding="utf-8-sig")
    assert "Widget" in content
    assert "19.99" in content


def test_csv_to_json(tmp_path):
    csv_file = tmp_path / "items.csv"
    csv_file.write_text("title,count\nBook,5\nPen,20\n", encoding="utf-8")

    json_file = tmp_path / "items.json"
    out = convert_data(csv_file, json_file)

    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert data[0]["title"] == "Book"
    assert data[0]["count"] == "5"


def test_json_to_csv(tmp_path):
    json_file = tmp_path / "records.json"
    json_file.write_text(
        json.dumps([{"user": "carol", "role": "admin"}, {"user": "dave", "role": "editor"}]),
        encoding="utf-8",
    )

    csv_file = tmp_path / "records.csv"
    out = convert_data(json_file, csv_file)

    assert out.exists()
    content = out.read_text(encoding="utf-8-sig")
    assert "user,role" in content
    assert "carol,admin" in content


def test_json_to_xlsx(tmp_path):
    json_file = tmp_path / "records.json"
    json_file.write_text(
        json.dumps([{"city": "Tokyo", "pop": 37000000}, {"city": "Paris", "pop": 2100000}]),
        encoding="utf-8",
    )

    xlsx_file = tmp_path / "records.xlsx"
    out = convert_data(json_file, xlsx_file)

    assert out.exists()
    wb = openpyxl.load_workbook(out)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    assert rows[0] == ("city", "pop")
    assert rows[1] == ("Tokyo", 37000000)
    wb.close()
