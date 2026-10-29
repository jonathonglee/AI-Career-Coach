"""Text extraction and basic input validation."""
import fitz

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARS = 18_000


def extract_resume(uploaded_file) -> str:
    data = uploaded_file.getvalue()
    if not data or len(data) > MAX_FILE_BYTES:
        raise ValueError("Upload a nonempty PDF or TXT file smaller than 5 MB.")
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        text = data.decode("utf-8-sig", errors="replace")
    elif name.endswith(".pdf"):
        try:
            with fitz.open(stream=data, filetype="pdf") as doc:
                if doc.page_count > 15:
                    raise ValueError("Please upload a resume with 15 pages or fewer.")
                text = "\n".join(page.get_text(sort=True) for page in doc)
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("Could not read this PDF. Try a text-based PDF or TXT file.") from exc
    else:
        raise ValueError("Only PDF and TXT resumes are supported.")
    text = text.strip()
    if not text:
        raise ValueError("No selectable text was found. Scanned PDFs are not supported; try TXT.")
    return text[:MAX_TEXT_CHARS]
