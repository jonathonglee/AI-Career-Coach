# AI Career Coach - Group 11: Group Assignment 2

A deployable **Streamlit** web app for college students: upload a resume, compare it with a job description, and ask career questions. Uses **OpenAI** for generation and **local TF-IDF retrieval** for a real, lightweight RAG workflow.

## Features
- Upload a text-based **PDF** or **TXT** resume, or paste resume text.
- Get strengths, improvements, and truthful bullet rewrites.
- Compare resume evidence with job requirements (without misleading ATS scores).
- Ask follow-up career and interview questions in a session chat.
- Expand **RAG retrieved passages** to demonstrate grounding and source filenames.
- Download generated resume and job comparison feedback as Markdown.

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

## How RAG works
1. `knowledge_base/*.md` contains short, curated guidance passages separated by `---`.
2. `career_coach/retrieval.py` loads the passages and converts them to TF-IDF vectors.
3. It ranks passages by cosine similarity to the current task and job/question text.
4. Top passages are supplied as context in the OpenAI request.
5. The model is instructed to cite the source filenames. The UI also shows the actual retrieved passages.

**Important:** TF-IDF retrieval is a simple lexical RAG method, not embedding-based semantic retrieval. The knowledge base is project-authored general guidance, not independently verified official career-center policy. The model may still make mistakes; inspect all output.

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
app.py                         Streamlit user interface
career_coach/extract.py        PDF/TXT extraction
career_coach/retrieval.py      TF-IDF retrieval
career_coach/analysis.py       OpenAI generation + prompting
knowledge_base/*.md           RAG source documents
samples/*.txt                  Fictional demo input
.streamlit/config.toml         Streamlit styling/config
.env.example                   API configuration example
requirements.txt               Python dependencies
tests/test_core.py             Offline tests
PRESENTATION_GUIDE.md          Five-minute demo plan
```

## Limitations / future improvements
- No scanned-PDF OCR, DOCX support, persistent accounts, or user history.
- Text-based retrieval may miss synonyms; embedding search is a possible upgrade.
- AI feedback is advisory and may be wrong; always verify job requirements.
- Do not assume the system's evaluation is equivalent to a real employer's ATS.
- A production release should add consent, authentication, rate limiting, retention policies, secure file scanning, and monitoring.
