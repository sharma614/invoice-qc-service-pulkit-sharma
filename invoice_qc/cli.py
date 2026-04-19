import argparse
import json
import sys
from pathlib import Path
from . import extractor, validator, models


def cmd_extract(args):
    invoices = extractor.extract_from_dir(args.pdf_dir)
    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump([i.model_dump() for i in invoices], fh, ensure_ascii=False, indent=2)
    print(f"Extracted {len(invoices)} invoices -> {outp}")


def cmd_validate(args):
    with open(args.input, "r", encoding="utf-8") as fh:
        raw_invoices = json.load(fh)
    invoices = [models.Invoice(**i) for i in raw_invoices]
    res = validator.validate_all(invoices)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)
    s = res.get("summary", {})
    print_summary(s)
    if s.get("invalid_invoices", 0) > 0:
        sys.exit(2)


def cmd_full_run(args):
    invoices = extractor.extract_from_dir(args.pdf_dir)
    res = validator.validate_all(invoices)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)
    print_summary(res.get("summary", {}))
    if res.get("summary", {}).get("invalid_invoices", 0) > 0:
        sys.exit(2)


def print_summary(summ: dict):
    total = summ.get("total_invoices", 0)
    valid = summ.get("valid_invoices", 0)
    invalid = summ.get("invalid_invoices", 0)
    ec = summ.get("error_counts", {})
    print(f"Total invoices: {total}")
    print(f"Valid: {valid}")
    print(f"Invalid: {invalid}")
    if ec:
        top = sorted(ec.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Top errors:")
        for k, v in top:
            print(f"  {k}: {v}")


def main():
    parser = argparse.ArgumentParser(prog="invoice-qc")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("extract")
    p1.add_argument("--pdf-dir", required=True)
    p1.add_argument("--output", required=True)
    p1.set_defaults(func=cmd_extract)

    p2 = sub.add_parser("validate")
    p2.add_argument("--input", required=True)
    p2.add_argument("--report", required=True)
    p2.set_defaults(func=cmd_validate)

    p3 = sub.add_parser("full-run")
    p3.add_argument("--pdf-dir", required=True)
    p3.add_argument("--report", required=True)
    p3.set_defaults(func=cmd_full_run)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
