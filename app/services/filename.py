import re
import unicodedata
from typing import Literal

DocKind = Literal["Resume", "CoverLetter"]

_UNSAFE_CHARS = re.compile(r'[\\/:*?"<>|]')
_WHITESPACE = re.compile(r"\s+")
_MAX_COMPONENT_LENGTH = 60


def _sanitize_component(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    stripped = _UNSAFE_CHARS.sub(" ", ascii_only)
    collapsed = _WHITESPACE.sub(" ", stripped).strip()
    underscored = collapsed.replace(" ", "_")
    return underscored[:_MAX_COMPONENT_LENGTH]


def build_filename(
    first: str, last: str, doc_kind: DocKind, company: str, role_title: str
) -> str:
    parts = [
        _sanitize_component(first),
        _sanitize_component(last),
        doc_kind,
        _sanitize_component(company),
        _sanitize_component(role_title),
    ]
    return "_".join(parts) + ".pdf"
