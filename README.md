import os
import tempfile

from file_converter.converter import convert_bytes, convert_file
from file_converter.formats import bytes_to_hex, hex_to_bytes
from file_converter.metadata import detect_file_type


def test_hex_round_trip() -> None:
    payload = b"hello world\x00\x01\x02"
    encoded = convert_bytes(payload, source_format="bin", target_format="hex")
    assert encoded == bytes_to_hex(payload).encode("utf-8")
    restored = convert_bytes(encoded, source_format="hex", target_format="bin")
    assert restored == payload


def test_base64_round_trip() -> None:
    payload = b"binary-data-123"
    encoded = convert_bytes(payload, source_format="bin", target_format="base64")
    restored = convert_bytes(encoded, source_format="base64", target_format="bin")
    assert restored == payload


def test_detect_file_type_for_dll_like_header() -> None:
    with tempfile.NamedTemporaryFile(delete=False) as handle:
        handle.write(b"MZ\x90\x00\x03\x00\x00\x00")
        path = handle.name
    try:
        assert detect_file_type(path) == "windows_pe"
    finally:
        os.unlink(path)


def test_convert_file_creates_output() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        source = os.path.join(tmpdir, "sample.bin")
        out = os.path.join(tmpdir, "sample.hex")
        with open(source, "wb") as handle:
            handle.write(b"\x00\x01\x02\x03")

        result = convert_file(source, output_format="hex", output_path=out)
        assert os.path.exists(out)
        with open(out, "rb") as handle:
            assert handle.read().decode("utf-8") == "00010203"
        assert result["output"] == out
