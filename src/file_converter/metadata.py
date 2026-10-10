import base64
import binascii
import os
from typing import Dict, Iterable, Optional

VALID_FORMATS = {
    "bin": "binary",
    "raw": "binary",
    "hex": "hex",
    "base64": "base64",
    "b64": "base64",
    "txt": "text",
    "text": "text",
    "json": "json",
}

def normalize_format(format_name: Optional[str]) -> str:
    if format_name is None:
        return "bin"
    key = str(format_name).strip().lower()
    if key in ("", "."):
        return "bin"
    key = key.lstrip(".")
    if key in VALID_FORMATS:
        return key
    raise ValueError(f"Unsupported format '{format_name}'. Supported formats: {', '.join(sorted(VALID_FORMATS))}")


def infer_format_from_path(path: str) -> str:
    _, ext = os.path.splitext(path)
    ext = ext.lower().lstrip(".")
    if not ext:
        return "bin"
    return normalize_format(ext)


def bytes_to_hex(data: bytes, *, separator: str = "") -> str:
    return data.hex(separator)


def hex_to_bytes(value: str) -> bytes:
    clean = value.strip()
    if not clean:
        return b""
    clean = "".join(ch for ch in clean if ch not in {" ", "\t", "\n", "\r", ":", "-"})
    if len(clean) % 2 != 0:
        raise ValueError("HEX string length must be even")
    return bytes.fromhex(clean)


def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def base64_to_bytes(value: str) -> bytes:
    clean = value.strip()
    if not clean:
        return b""
    try:
        return base64.b64decode(clean, validate=True)
    except Exception:
        padding = "=" * ((4 - len(clean) % 4) % 4)
        return base64.b64decode(clean + padding, validate=False)


def bytes_to_text(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.hex()


def parse_binary_input(data: bytes, source_format: str) -> bytes:
    fmt = normalize_format(source_format)
    if fmt in {"bin", "raw"}:
        return data
    if fmt == "hex":
        return hex_to_bytes(data.decode("utf-8", errors="ignore"))
    if fmt == "base64" or fmt == "b64":
        return base64_to_bytes(data.decode("utf-8", errors="ignore"))
    if fmt in {"txt", "text"}:
        return data
    raise ValueError(f"Unsupported source format for binary input: {source_format}")


def render_output(data: bytes, target_format: str) -> str:
    fmt = normalize_format(target_format)
    if fmt in {"bin", "raw"}:
        return data.decode("latin1")
    if fmt == "hex":
        return bytes_to_hex(data)
    if fmt == "base64" or fmt == "b64":
        return bytes_to_base64(data)
    if fmt in {"txt", "text"}:
        return bytes_to_text(data)
    if fmt == "json":
        return repr(data)
    raise ValueError(f"Unsupported target format: {target_format}")
