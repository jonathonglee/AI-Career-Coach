# 2026–2027 University of Arizona Eller subject-code catalog

The active RAG corpus is **`eller_courses_2026_2027.json`**, rebuilt from the
University of Arizona course catalog CSV provided on **November 5, 2026**.
`eller_courses_2026_2027.csv` is the filtered export with the original fields.
The previous `ua_courses_2026_2027.json` is retained as an **inactive legacy
sample** and is no longer read by the course finder.

## Why filter by subject code?

The official [Eller undergraduate courses directory](https://eller.arizona.edu/programs/undergraduate/academics/courses)
lists **ACCT, BCOM, BNAD, BNAN, ECON, ENTR, FIN, MGMT, MIS, MKTG**.
Eller also identifies **OSCM** as Operations & Supply Chain Management in its
[program offerings](https://eller.arizona.edu/programs/undergraduate/admissions/bsba).
These eleven subject codes form the **only** prefixes in this app's search index.
There is no unreliable search for the word “Eller” in course descriptions.

- The full source CSV contains **18,085 rows**.
- Subject-code filtering yields **863 rows** in the exported CSV.
- The RAG JSON contains **862 unique subject+course-number codes**, because
  the source export repeats **ECON 410** under two course IDs.
- **815 unique codes** are from the nine recognized Eller offering units.
  The other **47** have an Eller subject prefix but an outside offering unit,
  frequently because of cross-listings. These are included by default and
  excluded if **Strict Eller ownership** is checked in the UI.

The University of Arizona Registrar explains that a course's **academic
organization identifies its owning department** and that cross-listed courses
can have multiple subject prefixes:
https://registrar.arizona.edu/faculty-staff-resources/courses-catalog/catalog/course-forms-section-requirement-groups/resources

## Rebuild with a fresh catalog CSV

From the repository root:

```bash
python course_catalog/build_eller_catalog.py path/to/courses-report.csv
```

This regenerates the filtered CSV and JSON without external dependencies.
Do not commit the full 18,085-row university export if you only intend to
recommend Eller courses. For a more restrictive catalog, choose the optional
strict-ownership toggle or filter `Offering Unit` as well.

## Retrieval and source caveats

Each record preserves the official code, title, description, minimum units,
offering unit, requisites and Course ID from the export. Catalog-page links
follow the official course ID URL pattern (for example, MIS 556 appears at
https://catalog.arizona.edu/courses/0436081). For cross-listed entries a URL
may open the primary rather than the selected subject listing.

There are **no live enrollment, available-section, eligibility, prerequisite
satisfaction, or degree-plan checks**. The 2026–2027 export should not be
represented as an up-to-date schedule. Always check the official catalog and
a student's advisor. The application uses **local TF-IDF RAG**; no embeddings
or vector database are required.
