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
