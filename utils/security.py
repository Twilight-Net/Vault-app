"""
utils/security.py — File-upload validation and miscellaneous security helpers.
"""

import os
import uuid
from werkzeug.utils import secure_filename

# Maximum upload size: 50 MB
MAX_FILE_SIZE = 50 * 1024 * 1024

# Allowed MIME type prefixes / exact types
ALLOWED_MIME_TYPES = {
    # Images
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
    # Videos
    "video/mp4", "video/webm", "video/ogg", "video/quicktime",
    # Documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain", "text/csv", "text/markdown",
    # Archives
    "application/zip", "application/x-tar", "application/gzip",
}

ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp", "svg",
    "mp4", "webm", "ogv", "mov",
    "pdf", "doc", "docx", "xls", "xlsx",
    "txt", "csv", "md",
    "zip", "tar", "gz",
}


def allowed_file(filename: str) -> bool:
    """Check extension whitelist."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS


def safe_filename(original: str) -> str:
    """Generate a UUID-based filename that preserves the extension."""
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else "bin"
    return f"{uuid.uuid4().hex}.{ext}"


def get_mime_type(filepath: str) -> str:
    """Return MIME type using python-magic if available, else a fallback."""
    try:
        import magic
        return magic.from_file(filepath, mime=True)
    except Exception:
        # Fallback: guess from extension
        import mimetypes
        mime, _ = mimetypes.guess_type(filepath)
        return mime or "application/octet-stream"
