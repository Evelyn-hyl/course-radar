import re

from ftfy import fix_text


PICTURE_MARKER_PATTERN = re.compile(
    r"<!--\s*(?:start|end)\s+of\s+picture\s+text\s*-->",
    flags=re.IGNORECASE,
)
HTML_BREAK_PATTERN = re.compile(r"<br\s*/?>", flags=re.IGNORECASE)


def clean_extracted_text(text: str) -> str:
    """Normalize extracted Markdown without discarding meaningful content."""

    cleaned = fix_text(text, uncurl_quotes=False)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = cleaned.replace("\u00ad", "").replace("\u200b", "")
    cleaned = PICTURE_MARKER_PATTERN.sub("", cleaned)
    cleaned = HTML_BREAK_PATTERN.sub("\n", cleaned)
    cleaned = "\n".join(line.rstrip() for line in cleaned.splitlines())
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
