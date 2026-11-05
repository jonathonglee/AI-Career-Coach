"""Streamlit entrypoint: AI Career Coach."""
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from career_coach.extract import extract_resume
from career_coach.analysis import (generate_response, generate_benchmark_comparison,
                                   generate_course_recommendations)
from career_coach.benchmarks import retrieve_benchmarks
from career_coach.courses import retrieve_courses, load_courses, ELLER_SUBJECT_CODES

load_dotenv()
st.set_page_config(page_title="AI Career Coach", page_icon="🎓", layout="wide")


def get_secret(name, default=""):
    try:
        value = st.secrets.get(name, None)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)


st.title("🎓 AI Career Coach")
st.caption("Resume review • Job match • Career assistant • Example resumes • Eller course recommendations")
st.info("This is educational career guidance, not a hiring prediction. Avoid uploading highly sensitive information. Your resume and job description are sent to the AI provider when you run an analysis.")

with st.sidebar:
    st.header("Settings")
    stored_key = get_secret("OPENAI_API_KEY")
    custom_key = st.text_input("OpenAI API key (optional if configured by host)", type="password", help="Only enter a key you own. For a public deployment, configure it in Streamlit secrets instead.")
    api_key = custom_key or stored_key
    model = st.text_input("OpenAI model", value=get_secret("OPENAI_MODEL", "gpt-4o-mini"))
    st.caption("AI is configured" if api_key else "Add an API key to enable AI feedback")
    if st.button("Clear session", use_container_width=True):
        for key in ("resume_text", "job_text", "chat_history", "last_output", "last_sources",
                    "last_upload_id", "benchmark_result", "course_result"):
            st.session_state.pop(key, None)
        st.rerun()

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "job_text" not in st.session_state:
    st.session_state.job_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

left, right = st.columns(2)
with left:
    st.subheader("1. Your resume")
    upload = st.file_uploader("Upload PDF or TXT (up to 5 MB)", type=["pdf", "txt"])
    if upload is not None:
        upload_id = (upload.name, upload.size, getattr(upload, "file_id", None))
        if st.session_state.get("last_upload_id") != upload_id:
            try:
                st.session_state.resume_text = extract_resume(upload)
                st.session_state.last_upload_id = upload_id
                st.success("Resume text extracted successfully.")
            except ValueError as exc:
                st.error(str(exc))
    st.text_area("Or paste / edit your resume text", key="resume_text", height=250, max_chars=18000)
with right:
    st.subheader("2. Target job")
    st.text_area("Paste a job posting or description", key="job_text", height=330, max_chars=9000,
                 placeholder="Job title, responsibilities, required and preferred skills...")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Resume review", "🎯 Job match", "💬 Career assistant",
    "👥 Example resumes", "🎓 Eller course finder"
])


def run_analysis(task, question="", history=None):
    try:
        with st.spinner("Retrieving guidance and generating feedback..."):
            answer, passages = generate_response(
                api_key=api_key, model=model.strip(), task=task,
                resume=st.session_state.resume_text,
                job=st.session_state.job_text,
                question=question, history=history)
        return answer, passages
    except Exception as exc:
        st.error(f"Analysis could not complete: {type(exc).__name__}. Check your API key, model name, quota, and network connection.")
        return None, []


def show_sources(passages):
    with st.expander("RAG: retrieved knowledge-base passages"):
        if not passages:
            st.write("No passages matched this query.")
        for p in passages:
            st.markdown(f"**{p.source}** — relevance {p.score:.2f}")
            st.write(p.text)


with tab1:
    st.write("Get constructive, evidence-based feedback on your resume.")
    if st.button("Analyze resume", type="primary", disabled=not bool(st.session_state.resume_text.strip()), key="review"):
        answer, passages = run_analysis("resume")
        if answer:
            st.session_state.last_output = ("Resume review", answer)
            st.session_state.last_sources = passages
    if st.session_state.get("last_output", (None,))[0] == "Resume review":
        st.markdown(st.session_state.last_output[1])
        st.download_button("Download feedback", st.session_state.last_output[1], file_name="resume_feedback.md")
        show_sources(st.session_state.get("last_sources", []))

with tab2:
    st.write("Compare what your resume demonstrates against the job's requirements.")
    can_match = bool(st.session_state.resume_text.strip() and st.session_state.job_text.strip())
    if st.button("Compare resume to job", type="primary", disabled=not can_match, key="match"):
        answer, passages = run_analysis("match")
        if answer:
            st.session_state.last_output = ("Job match", answer)
            st.session_state.last_sources = passages
    if st.session_state.get("last_output", (None,))[0] == "Job match":
        st.markdown(st.session_state.last_output[1])
        st.download_button("Download comparison", st.session_state.last_output[1], file_name="job_match.md")
        show_sources(st.session_state.get("last_sources", []))

with tab3:
    st.write("Ask about interviews, skills, projects, or career paths. Resume/job text is optional.")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    question = st.chat_input("e.g., How should I prepare for a data analyst interview?")
    if question:
        previous = st.session_state.chat_history[:]
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        answer, passages = run_analysis("chat", question=question, history=previous)
        if answer:
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)
                show_sources(passages)

with tab4:
    st.subheader("Explore illustrative candidate resumes")
    st.write("Explore **fictional** resumes with skills and projects relevant to your target role, "
             "then compare them to the evidence in your own resume. These are **not** real "
             "applicants, scraped resumes, or a prediction of who you're competing against.")
    example_role = st.text_input("Target role", key="example_role", placeholder="e.g., Data Analyst or AI Engineer")
    available_target = bool(example_role.strip() or st.session_state.job_text.strip())
    if st.button("Find relevant example resumes", key="find_examples", type="primary",
                 disabled=not available_target):
        with st.spinner("Retrieving fictional resume examples..."):
            examples = retrieve_benchmarks(st.session_state.job_text, example_role)
        answer = None
        if examples and api_key and st.session_state.resume_text.strip():
            try:
                with st.spinner("Generating a grounded comparison..."):
                    answer = generate_benchmark_comparison(
                        api_key, model.strip(), st.session_state.resume_text,
                        st.session_state.job_text, example_role, examples)
            except Exception as exc:
                st.error(f"Comparison unavailable ({type(exc).__name__}). "
                         "Verify the model, API key, quota, and network.")
        st.session_state.benchmark_result = (answer, examples)

    if "benchmark_result" in st.session_state:
        comparison, examples = st.session_state.benchmark_result
        if comparison:
            st.markdown(comparison)
            st.download_button("Download example comparison", comparison,
                               file_name="illustrative_resume_comparison.md")
        elif examples and not st.session_state.resume_text.strip():
            st.info("Upload or paste your resume above for an AI comparison against these examples.")
        elif examples and not api_key:
            st.info("Add an OpenAI API key for an AI-generated comparison. "
                    "Retrieval of the examples works without a key.")
        st.markdown("#### Retrieved fictional resume examples")
        if not examples:
            st.write("No matching examples. Try a more specific job title.")
        for passage in examples:
            heading = passage.text.splitlines()[0].lstrip("# ")
            with st.expander(f"{heading} · {passage.source} · retrieval {passage.score:.2f}"):
                st.markdown(passage.text)
                st.caption(f"RAG source: benchmark_resumes/{passage.source} (fictional sample)")

with tab5:
    st.subheader("Eller College course recommender")
    st.write("Find business-school courses that may build skills for your next role. "
             "RAG searches a local **2026–2027 University of Arizona catalog export** "
             "filtered to official **Eller subject prefixes**. This is not a live class schedule.")
    st.caption(f"Catalog scope: {len(load_courses()):,} distinct Eller-prefix courses; "
               "source: University of Arizona catalog CSV export, November 5, 2026.")
    course_goal = st.text_input("Target career or skills to build", key="course_goal",
                                placeholder="e.g., data engineering, AI and LLM applications, cybersecurity")
    course_level = st.selectbox("Course level", ["All", "Undergraduate", "Graduate"],
                                key="course_level")
    selected_subjects = st.multiselect(
        "Eller subject codes (all selected by default)",
        options=sorted(ELLER_SUBJECT_CODES), default=sorted(ELLER_SUBJECT_CODES),
        key="eller_subject_codes")
    strict_eller = st.checkbox(
        "Strict Eller ownership only (exclude courses owned by other offering units)",
        value=False, key="strict_eller_courses",
        help="Some courses have an Eller subject code but are cross-listed and owned "
             "by another UA department. Leave unchecked to include those.")
    completed = st.text_input("Courses already taken (optional; comma-separated codes)",
                              key="completed_courses", placeholder="e.g., MIS 331, MIS 545")
    course_query = " ".join([course_goal.strip(), st.session_state.job_text.strip()[:3500]])
    if st.button("Recommend Eller courses", type="primary", key="find_courses",
                 disabled=not bool(course_query.strip()) or not bool(selected_subjects)):
        with st.spinner("Retrieving matching courses from the local catalog snapshot..."):
            course_matches = retrieve_courses(course_query, level=course_level,
                                              completed=completed, top_k=5,
                                              subjects=tuple(selected_subjects),
                                              strict_ownership=strict_eller)
        explanation = None
        if course_matches and api_key:
            try:
                with st.spinner("Explaining matches with cited course descriptions..."):
                    explanation = generate_course_recommendations(
                        api_key, model.strip(), st.session_state.resume_text,
                        st.session_state.job_text, course_goal, completed, course_matches)
            except Exception as exc:
                st.error(f"AI explanation unavailable ({type(exc).__name__}). "
                         "The source-linked course matches remain available below.")
        st.session_state.course_result = (explanation, course_matches)

    if "course_result" in st.session_state:
        explanation, course_matches = st.session_state.course_result
        if explanation:
            st.markdown(explanation)
            st.download_button("Download course plan", explanation,
                               file_name="ua_course_recommendations.md")
        elif course_matches and not api_key:
            st.info("Add an OpenAI API key for personalized AI explanations. "
                    "Catalog retrieval works without a key.")
        st.markdown("#### Retrieved catalog records")
        if not course_matches:
            st.warning("No matching courses with the selected subjects, level, "
                       "completion history, and ownership filter. Broaden your options.")
        for course, score in course_matches:
            with st.expander(f"{course.code} — {course.title} · {course.level} · {course.credits} units"):
                st.write(course.description)
                st.caption(f"RAG relevance: {score:.2f} · Catalog 2026–2027 "
                           f"· Offering unit: {course.offering_unit}")
                if course.requisites and course.requisites != "-":
                    st.write(f"**Course requisites:** {course.requisites}")
                st.link_button("Open university catalog record", course.url)
    st.caption("Always check prerequisites, term availability, program applicability, "
               "and registration with an academic advisor. "
               "Official catalog: https://catalog.arizona.edu/")

st.divider()
st.caption("RAG uses local TF-IDF retrieval over general guidance, fictional example "
           "resumes, and Eller-prefixed catalog records. Retrieved passages ground OpenAI "
           "responses when a key is provided. The app is not connected to live admissions, "
           "registration, hiring, or applicant data. Uploaded documents are held in session "
           "memory and sent to the AI provider only when an AI analysis is requested; "
           "hosting and AI providers may retain data under their own policies.")

