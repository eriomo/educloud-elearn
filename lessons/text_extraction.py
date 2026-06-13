"""
Extracts plain text from an uploaded lecture-note file (.txt, .pdf, .docx)
so it can be stored in Lesson.content_text (a Postgres/Supabase column),
rather than only existing as a file on Render's disk.

This is the core of "lecture notes stored in the Supabase databank": the
binary file itself still goes through Django's normal file storage (which,
on Render's free tier, is ephemeral local disk - unchanged, existing
behaviour), but the TEXT CONTENT is pulled out and saved into the
database, where it persists across redeploys, can be searched, and (in
future) can feed the topic-assignment keyword pipeline alongside the
scheme-of-work content in SCHEME_OF_WORK.

Usage (see lessons/models.py SAVE_OVERRIDE_SNIPPET.py for where to call
this):

    from .text_extraction import extract_text_from_file
    text = extract_text_from_file(self.content_file)
    if text:
        self.content_text = text

Supported formats: .txt (read directly), .pdf (via pypdf), .docx (via
python-docx). Any other format, or any extraction error, returns an empty
string and is logged - it never raises, so a lesson upload can never fail
because of this.
"""
import logging
import os

logger = logging.getLogger(__name__)


def extract_text_from_file(file_field, max_chars=50000):
    """
    file_field: a Django FieldFile (e.g. lesson.content_file).
    Returns extracted plain text, or '' if nothing could be extracted.
    """
    if not file_field:
        return ""

    name = file_field.name or ""
    ext = os.path.splitext(name)[1].lower()

    try:
        if ext == ".txt":
            return _extract_txt(file_field)
        if ext == ".pdf":
            return _extract_pdf(file_field, max_chars)
        if ext == ".docx":
            return _extract_docx(file_field, max_chars)
    except Exception as e:
        logger.warning("Lecture note text extraction failed for %s: %s", name, e)
        return ""

    # Unsupported format (e.g. .pptx, image, video) - nothing to extract
    return ""


def _extract_txt(file_field):
    file_field.seek(0)
    raw = file_field.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="ignore")
    return raw.strip()


def _extract_pdf(file_field, max_chars):
    from pypdf import PdfReader
    file_field.seek(0)
    reader = PdfReader(file_field)
    chunks = []
    total = 0
    for page in reader.pages:
        text = page.extract_text() or ""
        chunks.append(text)
        total += len(text)
        if total >= max_chars:
            break
    return "\n".join(chunks).strip()[:max_chars]


def _extract_docx(file_field, max_chars):
    import docx
    file_field.seek(0)
    document = docx.Document(file_field)
    chunks = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(chunks).strip()[:max_chars]
