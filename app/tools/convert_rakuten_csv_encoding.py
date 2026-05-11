import argparse
import csv
from pathlib import Path


DEFAULT_ENCODINGS = ("cp932", "utf-8-sig", "shift_jis", "utf-8")


def main() -> None:
    args = _parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    raw_content = input_path.read_bytes()
    decoded_text, source_encoding = decode_csv_bytes(raw_content)

    if args.normalize_newlines:
        decoded_text = decoded_text.replace("\r\n", "\n").replace("\r", "\n")

    if args.validate_csv:
        validate_csv(decoded_text)

    output_encoding = "utf-8-sig" if args.excel_friendly else "utf-8"
    output_path.write_text(decoded_text, encoding=output_encoding, newline="")

    print(f"Input: {input_path}")
    print(f"Detected encoding: {source_encoding}")
    print(f"Output: {output_path}")
    print(f"Output encoding: {output_encoding}")


def decode_csv_bytes(content: bytes) -> tuple[str, str]:
    for encoding in DEFAULT_ENCODINGS:
        try:
            return content.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise ValueError(f"CSV encoding is not supported. Tried: {', '.join(DEFAULT_ENCODINGS)}")


def validate_csv(text: str) -> None:
    sample = text[:8192]
    dialect = csv.Sniffer().sniff(sample)
    reader = csv.reader(text.splitlines(), dialect)
    first_row = next(reader, None)
    if first_row is None:
        raise ValueError("CSV appears to be empty.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Rakuten RMS CSV from CP932/Shift_JIS/UTF-8 to UTF-8."
    )
    parser.add_argument("input", help="Input CSV path downloaded from Rakuten RMS.")
    parser.add_argument("output", help="Output UTF-8 CSV path.")
    parser.add_argument(
        "--excel-friendly",
        action="store_true",
        help="Write UTF-8 with BOM so Excel opens Japanese text correctly.",
    )
    parser.add_argument(
        "--no-normalize-newlines",
        action="store_false",
        dest="normalize_newlines",
        help="Keep original newline style.",
    )
    parser.add_argument(
        "--no-validate-csv",
        action="store_false",
        dest="validate_csv",
        help="Skip csv.Sniffer validation.",
    )
    parser.set_defaults(normalize_newlines=True, validate_csv=True)
    return parser.parse_args()


if __name__ == "__main__":
    main()
