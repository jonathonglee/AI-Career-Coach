from pathlib import Path
from career_coach.retrieval import retrieve, load_passages
from career_coach.extract import extract_resume


class DummyUpload:
    name = "resume.txt"
    def getvalue(self):
        return b"Python SQL Tableau project"


def test_extract_txt():
    assert "Python" in extract_resume(DummyUpload())


def test_knowledge_base_loads():
    assert len(load_passages()) >= 3


def test_retrieval_returns_relevant_passage():
    results = retrieve("STAR behavioral interview situation task action result")
    assert results and any("interview" in p.source for p in results)


def test_no_query_returns_no_results():
    assert retrieve("") == []


def test_benchmark_corpus_is_explicitly_fictional():
    from career_coach.benchmarks import BENCHMARK_DIR, retrieve_benchmarks
    files = sorted(BENCHMARK_DIR.glob("*.md"))
    assert len(files) >= 5
    assert all("FICTIONAL SAMPLE PROFILE" in file.read_text() for file in files)
    top = retrieve_benchmarks("Python machine learning deep learning RAG LLM", "AI Engineer")
    assert top and "ai_ml_candidate.md" in [passage.source for passage in top[:2]]


def test_benchmark_no_target():
    from career_coach.benchmarks import retrieve_benchmarks
    assert retrieve_benchmarks("", "") == []


def test_ua_catalog_is_sourced():
    from career_coach.courses import load_courses
    courses = load_courses()
    assert len(courses) == 862
    assert len({c.code for c in courses}) == len(courses)
    assert all(c.url.startswith("https://catalog.arizona.edu/") or
               c.url.startswith("https://eller.arizona.edu/") for c in courses)
    assert any(c.code == "MIS556" for c in courses)


def test_eller_course_prefix_filter_and_ownership():
    from career_coach.courses import load_courses, retrieve_courses, ELLER_SUBJECT_CODES
    import re
    courses = load_courses()
    assert len(courses) == 862  # 863 CSV rows, including duplicate ECON 410
    assert all(re.match(r"^[A-Z]+", c.code).group(0) in ELLER_SUBJECT_CODES
               for c in courses)
    assert sum(c.eller_owned for c in courses) == 815
    assert any(not c.eller_owned for c in courses)  # cross-listings
    only_mis = retrieve_courses("business intelligence data mining", subjects=("MIS",), top_k=50)
    assert only_mis and all(c.code.startswith("MIS") for c, _ in only_mis)
    strict = retrieve_courses("business management ethics", strict_ownership=True, top_k=100)
    assert strict and all(c.eller_owned for c, _ in strict)
    assert retrieve_courses("business", subjects=()) == []


def test_course_retrieval_excludes_completed_and_filters_level():
    from career_coach.courses import retrieve_courses
    ranked = retrieve_courses("generative AI LLM prompt engineering RAG", level="Graduate",
                              completed="MIS 556, MIS545", top_k=20)
    assert ranked
    assert all(course.level == "Graduate" for course, _ in ranked)
    assert "MIS556" not in [course.code for course, _ in ranked]
    ranked_all = retrieve_courses("generative AI LLM prompt engineering RAG", level="Graduate")
    assert ranked_all[0][0].code == "MIS556"


def test_course_retrieval_includes_linked_sources():
    from career_coach.courses import format_course_context, retrieve_courses
    matches = retrieve_courses("business intelligence data warehouse ETL SQL analytics")
    text = format_course_context(matches)
    assert "https://" in text
    assert "MIS587" in text


def test_completed_course_parsing():
    from career_coach.courses import parse_completed_courses
    assert parse_completed_courses("mis 331, MIS545; MIS-556") == {"MIS331", "MIS545", "MIS556"}


def test_generative_tasks_refuse_missing_context():
    from career_coach.analysis import generate_benchmark_comparison, generate_course_recommendations
    import pytest
    with pytest.raises(ValueError):
        generate_benchmark_comparison("", "model", "resume", "job", "role", [])
    with pytest.raises(ValueError):
        generate_course_recommendations("", "model", "resume", "job", "role", "", [])


def test_streamlit_app_contains_five_tabs():
    app = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    assert '"👥 Example resumes"' in app
    assert '"🎓 Eller course finder"' in app
    assert "retrieve_benchmarks(" in app
    assert "retrieve_courses(" in app
    assert "strict_eller_courses" in app
