# Five-minute presentation plan (November 5, 2026)

**0:00–0:40 — Problem.** Students struggle to tailor resumes and understand job requirements. Show the app homepage.

**0:40–1:20 — Solution.** Three features: resume review, job comparison, and career chat. Explain input via PDF/TXT or paste.

**1:20–2:45 — Live demo.** Upload `samples/sample_resume.txt`, paste `samples/sample_job_description.txt`, run comparison, then ask a STAR interview question. Open the RAG sources expander.

**2:45–3:45 — AI architecture.** Streamlit UI → PDF/text extraction → TF-IDF similarity search over curated Markdown guidance → relevant passages + student inputs to OpenAI → personalized response. Explain that the passages shown in the expander are actually retrieved, not invented citations.

**3:45–4:30 — Practical value.** Identify demonstrated qualifications, unproven requirements, and actionable improvements. Stress that the tool does not invent qualifications or pretend to predict hiring.

**4:30–5:00 — Limitations and next steps.** API cost, model errors, privacy, lexical retrieval. Future work: authenticated profiles, embedding retrieval, additional career-center resources.

## Suggested team division
- Team member A: Streamlit UI and demo.
- Team member B: resume parsing and comparison prompts.
- Team member C: retrieval and knowledge-base content.
- Team member D: deployment, testing, and presentation.

## Before presenting
- Confirm the public app URL works in a private/incognito window.
- Verify API credits, key, and selected model.
- Use fictional resume/job data to protect privacy.
- Test the full flow once immediately before the presentation.
- Have screenshots as a backup if the API or hosting service is unavailable.
