import argparse
import json
from pathlib import Path

from .converter import convert_file, normalize_output_name
from .formats import VALID_FORMATS
from .metadata import inspect_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert raw binary, HEX, Base64, and inspect PE files like DLL/EXE.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert a file into another format")
    convert_parser.add_argument("input", help="Input file path")
    convert_parser.add_argument("--to", dest="target", required=True, help="Target format: bin, hex, base64, txt, json")
    convert_parser.add_argument("--output", help="Output path; defaults to a generated path next to the input file")
    convert_parser.add_argument("--source-format", help="Explicit source format for input file if detection is insufficient")
    convert_parser.add_argument("--metadata", action="store_true", help="Include file metadata in the result")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect the file type and metadata")
    inspect_parser.add_argument("input", help="File path to inspect")

    formats_parser = subparsers.add_parser("list-formats", help="List supported formats")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list-formats":
        print(json.dumps(sorted(VALID_FORMATS.keys()), indent=2))
        return

    if args.command == "inspect":
        result = inspect_file(args.input)
        print(json.dumps(result, indent=2, default=str))
        return

    if args.command == "convert":
        output_path = args.output or normalize_output_name(args.input, args.target)
        result = convert_file(
            args.input,
            output_format=args.target,
            output_path=output_path,
            source_format=args.source_format,
            include_metadata=args.metadata,
        )
        print(json.dumps(result, indent=2, default=str))
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()
