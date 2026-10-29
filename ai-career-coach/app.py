"""Streamlit entrypoint: AI Career Coach."""
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from career_coach.extract import extract_resume
from career_coach.analysis import generate_response

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
st.caption("Resume feedback • Job description comparison • Career questions")
st.info("This is educational career guidance, not a hiring prediction. Avoid uploading highly sensitive information. Your resume and job description are sent to the AI provider when you run an analysis.")

with st.sidebar:
    st.header("Settings")
    stored_key = get_secret("OPENAI_API_KEY")
    custom_key = st.text_input("OpenAI API key (optional if configured by host)", type="password", help="Only enter a key you own. For a public deployment, configure it in Streamlit secrets instead.")
    api_key = custom_key or stored_key
    model = st.text_input("OpenAI model", value=get_secret("OPENAI_MODEL", "gpt-4o-mini"))
    st.caption("AI is configured" if api_key else "Add an API key to enable AI feedback")
    if st.button("Clear session", use_container_width=True):
        for key in ("resume_text", "job_text", "chat_history", "last_output", "last_sources", "last_upload_id"):
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

tab1, tab2, tab3 = st.tabs(["📝 Resume review", "🎯 Job match", "💬 Career assistant"])


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

st.divider()
st.caption("RAG uses TF-IDF retrieval from the local knowledge_base folder. Uploaded documents are processed in session memory; no application database is configured. Hosting and AI providers may retain data under their own policies.")
