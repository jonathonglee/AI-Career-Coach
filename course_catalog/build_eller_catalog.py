"""Build the Eller-only local RAG corpus from UA's exported 2026–2027 course CSV.

Usage:
    python course_catalog/build_eller_catalog.py path/to/courses-report.csv

The primary filter is the university's official Eller subject prefixes, not the
appearance of the word 'Eller' in a course title or description. The Offering
Unit field is retained for an optional strict ownership filter in the app.
"""
import argparse
import csv
import json
import re
from pathlib import Path

ELLER_SUBJECT_CODES = (
    "ACCT", "BCOM", "BNAD", "BNAN", "ECON", "ENTR", "FIN",
    "MGMT", "MIS", "MKTG", "OSCM",
)

ELLER_OFFERING_UNITS = (
    "Accountancy, Sch of", "Business Analytics, Sch of", "Economics",
    "Eller Administration", "Finance", "Management & Organizations",
    "Management Information Systems", "Marketing", "McGuire Ctr: Entrepreneurship",
)

CATALOG_URL = "https://catalog.arizona.edu/"
COURSE_LINK_ROOT = "https://catalog.arizona.edu/courses/"
ROOT = Path(__file__).resolve().parent


def normalize_description(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def records_from_csv(csv_path: Path):
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        needed = {"Course ID", "Subject code", "Catalog Number", "Course Title",
                  "Course Description", "Min Units", "Offering Unit"}
        missing = needed - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required CSV columns: {', '.join(sorted(missing))}")
        rows = [row for row in reader if row["Subject code"].strip().upper() in ELLER_SUBJECT_CODES]
        fieldnames = reader.fieldnames
    # The export contains two records for ECON 410 with the same title. Keep
    # both source rows in the CSV but one canonical code in the search index.
    unique = {}
    for row in rows:
        subject = row["Subject code"].strip().upper()
        number = row["Catalog Number"].strip().upper()
        code = f"{subject}{number}"
        match = re.match(r"^(\d{3})", number)
        if not match:
            continue
        course_id = row["Course ID"].strip()
        if not re.fullmatch(r"\d{6}", course_id):
            raise ValueError(f"Unexpected Course ID for {code}: {course_id!r}")
        unit = row["Offering Unit"].strip()
        units = float(row["Min Units"])
        record = {
            "code": code,
            "title": normalize_description(row["Course Title"]),
            "level": "Graduate" if int(match.group(1)) >= 500 else "Undergraduate",
            "credits": int(units) if units.is_integer() else units,
            "description": normalize_description(row["Course Description"]),
            "index_terms": "",
            "url": f"{COURSE_LINK_ROOT}{course_id}1",
            "offering_unit": unit,
            "course_id": course_id,
            "requisites": normalize_description(row.get("Course Requisites", "")),
            "eller_owned": unit in ELLER_OFFERING_UNITS,
        }
        if code not in unique or len(record["description"]) > len(unique[code]["description"]):
            unique[code] = record
    return rows, [unique[code] for code in sorted(unique)], fieldnames


def build(input_csv: Path, output_dir: Path = ROOT) -> tuple[int, int]:
    rows, records, headers = records_from_csv(input_csv)
    output_dir.mkdir(parents=True, exist_ok=True)
    export_csv = output_dir / "eller_courses_2026_2027.csv"
    with export_csv.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "catalog_year": "2026–2027",
        "source": "University of Arizona catalog CSV export, supplied 2026-11-05",
        "catalog_url": CATALOG_URL,
        "filter": {"subject_codes": ELLER_SUBJECT_CODES,
                   "eller_offering_units_for_optional_strict_filter": ELLER_OFFERING_UNITS},
        "notes": "The catalog is not a live section schedule. Cross-listed links may point to the primary course listing.",
        "courses": records,
    }
    (output_dir / "eller_courses_2026_2027.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(rows), len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    row_count, unique_count = build(args.input_csv, args.output_dir)
    print(f"Saved {row_count} Eller-prefix rows, {unique_count} unique course codes to {args.output_dir}")
