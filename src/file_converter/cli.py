import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .formats import (
    base64_to_bytes,
    bytes_to_base64,
    bytes_to_hex,
    bytes_to_text,
    hex_to_bytes,
    infer_format_from_path,
    normalize_format,
    parse_binary_input,
)
from .metadata import inspect_file


def ensure_parent_directory(path: str) -> None:
    parent = Path(path).parent
    if parent and not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


def read_source_bytes(input_path: str, source_format: Optional[str] = None) -> bytes:
    with open(input_path, "rb") as handle:
        raw = handle.read()

    if source_format is None:
        source_format = infer_format_from_path(input_path)

    fmt = normalize_format(source_format)
    if fmt in {"bin", "raw"}:
        return raw
    if fmt == "hex":
        return hex_to_bytes(raw.decode("utf-8", errors="ignore"))
    if fmt in {"base64", "b64"}:
        return base64_to_bytes(raw.decode("utf-8", errors="ignore"))
    if fmt in {"txt", "text"}:
        return raw
    if fmt == "json":
        obj = json.loads(raw.decode("utf-8", errors="ignore"))
        return json.dumps(obj, indent=2).encode("utf-8")
    raise ValueError(f"Unsupported source format: {source_format}")


def write_output_bytes(path: str, data: bytes) -> str:
    ensure_parent_directory(path)
    with open(path, "wb") as handle:
        handle.write(data)
    return path


def convert_bytes(data: bytes, *, source_format: Optional[str] = None, target_format: str) -> bytes:
    source_fmt = normalize_format(source_format) if source_format else "bin"
    target_fmt = normalize_format(target_format)
    decoded = parse_binary_input(data, source_fmt)

    if target_fmt in {"bin", "raw"}:
        return decoded
    if target_fmt == "hex":
        return bytes_to_hex(decoded).encode("utf-8")
    if target_fmt in {"base64", "b64"}:
        return bytes_to_base64(decoded).encode("utf-8")
    if target_fmt in {"txt", "text"}:
        return bytes_to_text(decoded).encode("utf-8")
    if target_fmt == "json":
        payload = {
            "source_format": source_fmt,
            "target_format": target_fmt,
            "size_bytes": len(decoded),
            "hex_preview": bytes_to_hex(decoded[:64]),
            "base64_preview": bytes_to_base64(decoded[:64]),
        }
        return json.dumps(payload, indent=2).encode("utf-8")
    raise ValueError(f"Unsupported target format: {target_format}")


def convert_file(input_path: str, output_format: str, output_path: Optional[str] = None, source_format: Optional[str] = None, include_metadata: bool = False) -> Dict[str, Any]:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    source_fmt = source_format or infer_format_from_path(str(input_file))
    if source_fmt == "dll" or source_fmt == "exe":
        source_fmt = "bin"

    raw = read_source_bytes(str(input_file), source_format=source_fmt)
    converted = convert_bytes(raw, source_format=source_fmt, target_format=output_format)

    if output_path is None:
        base_name = input_file.stem
        target_ext = f".{normalize_format(output_format)}"
        output_path = str(input_file.with_name(f"{base_name}_converted{target_ext}"))

    write_output_bytes(output_path, converted)

    result = {
        "input": str(input_file),
        "source_format": source_fmt,
        "output_format": normalize_format(output_format),
        "output": output_path,
        "size_bytes": len(raw),
    }

    if include_metadata:
        result["metadata"] = inspect_file(str(input_file))

    return result


def normalize_output_name(input_path: str, output_format: str) -> str:
    input_file = Path(input_path)
    target_ext = f".{normalize_format(output_format)}"
    return str(input_file.with_name(f"{input_file.stem}_converted{target_ext}"))
