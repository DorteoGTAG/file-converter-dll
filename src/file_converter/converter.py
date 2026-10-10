import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import pefile
except Exception:  # pragma: no cover - dependency may not be installed in some environments
    pefile = None


def sha256_of_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_file_type(path: str) -> str:
    with open(path, "rb") as handle:
        header = handle.read(64)
    if len(header) >= 2 and header[:2] == b"MZ":
        return "windows_pe"
    if len(header) >= 4 and header[:4] == b"\x7fELF":
        return "elf"
    if len(header) >= 8 and header[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if len(header) >= 3 and header[:3] == b"PK\x03\x04":
        return "zip"
    if len(header) >= 2 and header[:2] == b"%!":
        return "postscript"
    if len(header) >= 4 and header[:4] in {b"\x00\x00\x00\x00", b"\xFF\xFE\x00\x00"}:
        return "raw_binary"
    return "generic_binary"


def read_pe_metadata(path: str) -> Dict[str, Any]:
    if pefile is None:
        raise RuntimeError("pefile is required for PE metadata inspection. Install the project dependencies first.")

    pe = pefile.PE(path)
    exports = []
    imports = []

    try:
        for entry in pe.DIRECTORY_ENTRY_EXPORT.symbols or []:
            exports.append({
                "name": entry.name.decode("utf-8", errors="replace") if entry.name else "",
                "ordinal": entry.ordinal,
                "address": hex(entry.address),
            })
    except Exception:
        exports = []

    try:
        for entry in pe.DIRECTORY_ENTRY_IMPORT or []:
            module_name = entry.dll.decode("utf-8", errors="replace") if entry.dll else ""
            imports.append({
                "module": module_name,
                "functions": [
                    imp.name.decode("utf-8", errors="replace") if getattr(imp, "name", None) else ""
                    for imp in entry.imports
                ],
            })
    except Exception:
        imports = []

    machine = pe.FILE_HEADER.Machine
    machine_map = {
        0x14c: "x86",
        0x8664: "AMD64",
        0x200: "ARM",
        0x1c0: "ARM64",
        0xaa64: "ARM64EC",
        0x9041: "MIPS",
        0x266: "MIPS16",
        0x5032: "RISC-V",
    }

    result = {
        "type": "windows_pe",
        "file_name": Path(path).name,
        "file_size": Path(path).stat().st_size,
        "sha256": sha256_of_file(path),
        "machine": machine_map.get(machine, f"0x{machine:04x}"),
        "bits": 64 if machine in {0x8664, 0xaa64, 0x1c0} else 32 if machine == 0x14c else None,
        "timestamp": getattr(pe.FILE_HEADER, "TimeDateStamp", None),
        "section_count": getattr(pe.FILE_HEADER, "NumberOfSections", None),
        "characteristics": getattr(pe.FILE_HEADER, "Characteristics", None),
        "optional_header_magic": getattr(getattr(pe, "OPTIONAL_HEADER", None), "Magic", None),
        "entry_point": hex(getattr(getattr(pe, "OPTIONAL_HEADER", None), "AddressOfEntryPoint", 0)),
        "export_count": len(exports),
        "import_count": len(imports),
        "exports": exports,
        "imports": imports,
    }
    return result


def inspect_file(path: str) -> Dict[str, Any]:
    kind = detect_file_type(path)
    if kind == "windows_pe":
        return read_pe_metadata(path)
    return {
        "type": kind,
        "file_name": Path(path).name,
        "file_size": Path(path).stat().st_size,
        "sha256": sha256_of_file(path),
        "detected_by": "magic_bytes",
    }
