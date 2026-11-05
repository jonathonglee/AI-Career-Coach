# AI Career Coach - Group 11: Group Assignment 2

A deployable **Streamlit** web app for college students: upload a resume, compare it with a job description, ask career questions, examine fictional resume examples, and discover relevant University of Arizona courses. Uses **OpenAI** for generation and **local TF-IDF retrieval** for a lightweight RAG workflow across three knowledge sources.

## Live Application

[Launch AI Career Coach](https://ai-career-coach-mis556.streamlit.app/)

## Features
- Upload a text-based **PDF** or **TXT** resume, or paste resume text.
- Get strengths, improvements, and truthful bullet rewrites.
- Compare resume evidence with job requirements (without misleading ATS scores).
- Ask follow-up career and interview questions in a session chat.
- Expand **RAG retrieved passages** to demonstrate grounding and source filenames.
- Download generated resume and job comparison feedback as Markdown.
- Explore **fictional sample candidate resumes** matched to the target role and optionally receive an evidence-based comparison with your resume. These are **not** actual job applicants.
- Find **Eller College courses** using RAG over a 2026–2027 University of Arizona catalog CSV export filtered by Eller subject codes. Filter by academic level, subject, completed courses, and optional strict department ownership; use AI to explain relevance to job requirements.
- Browse the retrieved example resumes and official catalog record links even without an AI API key.

## Quick start (Windows PowerShell)

Install Python 3.11 or 3.12, then open a terminal in this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and replace `replace_with_your_api_key` with your OpenAI API key. Then:

```powershell
streamlit run app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`). The OpenAI API is a paid service and requires available credits. The default model can be changed in the sidebar if your account supports a different model.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API key
streamlit run app.py
```

## Demo walkthrough
1. Upload `samples/sample_resume.txt` (fictional sample data).
2. Copy/paste `samples/sample_job_description.txt` into the target-job field.
3. Click **Analyze resume**, then expand the RAG passages.
4. Click **Compare resume to job** and review evidence vs. gaps.
5. Open **Career assistant** and ask: `How should I answer a teamwork interview question using STAR?`
6. Open **Example resumes**, enter `AI Engineer` or `Data Analyst`, and click **Find relevant example resumes**. Expand source documents and inspect the AI comparison (with a resume and key).
7. Open **Eller course finder**, enter `LLM RAG AI engineer`, select **Graduate**, and click **Recommend UA courses**. Check that **MIS 556** is retrieved and linked to the official UA catalog. Enter `MIS 556` in completed courses and rerun to see that it is excluded.

## How RAG works
There are now **three separate retrieval corpora**:

1. `knowledge_base/*.md`: curated career guidance, used by resume review, job match, and career assistant.
2. `benchmark_resumes/*.md`: six **project-authored fictional** role-specific resume examples, used by Example resumes.
3. `course_catalog/eller_courses_2026_2027.json`: **862 unique Eller-prefix courses** from the user-supplied November 5, 2026 UA catalog CSV (863 rows including a duplicate ECON 410). Records retain original course descriptions, units, offering units, requisites, and course-ID-based catalog links. The app excludes courses outside the official Eller subject-code list.

**Retrieve:** `career_coach/retrieval.py` uses TF-IDF and cosine similarity to select the top matching passages/course records; `career_coach/benchmarks.py` and `career_coach/courses.py` filter and format domain-specific results. Course selection filters degree level, selected Eller prefixes, optional Eller offering-unit ownership, and completed course codes **before** ranking.

**Augment:** Retrieved examples/course records and the student-provided role, job description, or resume are passed to an OpenAI chat completion in `career_coach/analysis.py`. The prompt explicitly forbids fabricating qualifications, real applicants, courses, or hiring predictions.

**Generate:** The model compares documented evidence or explains recommended courses and is told to cite filenames or official course URLs. The UI separately displays retrieved source records so users can inspect them. Without an API key the retrieval stage still works, but no new LLM explanation is generated.

**Important:** TF-IDF is lexical RAG, **not** embedding-based semantic search. The career guidance and example resumes are project-authored. The Eller-filtered UA course snapshot is **not** a live class schedule; verify eligibility, prerequisites, term offerings, and degree applicability with the official catalog and advisor. LLM output can still be wrong.

## Deploy to Streamlit Community Cloud
1. Create a **private** GitHub repository and upload these files, preserving the folder structure. Never commit `.env` or `secrets.toml`.
2. Visit https://share.streamlit.io/ and deploy the GitHub repository with **`app.py`** as the main file.
3. In the app's **Settings → Secrets**, add:

   ```toml
   OPENAI_API_KEY = "your-real-key"
   OPENAI_MODEL = "gpt-4o-mini"
   ```

4. Save secrets and reboot the app if needed. Test the deployed public URL from an incognito browser window.
5. Keep the app running and accessible for your November 5 presentation/submission. Hosting availability depends on Streamlit Cloud account and service limits.

**Security warning:** A shared server-side API key means every visitor may incur costs on your account. For a class demo, limit distribution, set provider usage limits, and disable/remove the key after grading. This educational prototype has no authentication, rate limiting, malware scanning, or production-grade privacy controls. Use fictional or redacted resumes for public demonstrations.

## Test

```bash
python -m pytest -q
```

Tests cover text extraction and retrieval without making billable OpenAI calls.

## Files

```text
app.py                                  Streamlit user interface (5 tabs)
career_coach/extract.py                 PDF/TXT extraction
career_coach/retrieval.py               Reusable TF-IDF retrieval
career_coach/analysis.py                OpenAI generation + grounded prompting
career_coach/benchmarks.py              Example resume retrieval
career_coach/courses.py                 UA course catalog retrieval/filtering
knowledge_base/*.md                     RAG guidance documents
benchmark_resumes/*.md                  Six clearly fictional resumes
course_catalog/eller_courses_2026_2027.json  Active Eller course RAG corpus
course_catalog/eller_courses_2026_2027.csv   Filtered original catalog data
course_catalog/build_eller_catalog.py     Rebuild script using subject codes
course_catalog/README.md                Dataset provenance and cautions
FEATURE_DEMO.md                         Presentation walkthrough
samples/*.txt                  Fictional demo input
.streamlit/config.toml         Streamlit styling/config
.env.example                   API configuration example
requirements.txt               Python dependencies
tests/test_core.py             Offline tests
```

## Limitations / future improvements
- No scanned-PDF OCR, DOCX support, persistent accounts, or user history.
- Text-based retrieval may miss synonyms; embedding search is a possible upgrade.
- AI feedback is advisory and may be wrong; always verify job requirements.
- Example resumes are fictional portfolio benchmarks, **not** actual competitors or population statistics.
- UA catalog data is a November 5, 2026 Eller-subject snapshot rather than live course availability or academic advising. Cross-listed courses may carry Eller prefixes but belong to other departments; toggle strict ownership if needed.
- Adding dynamic catalog synchronization or embedding retrieval would be a future improvement.
- Do not assume the system's evaluation is equivalent to a real employer's ATS.
- A production release should add consent, authentication, rate limiting, retention policies, secure file scanning, and monitoring.
