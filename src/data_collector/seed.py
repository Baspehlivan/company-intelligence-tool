#!/usr/bin/env python3
"""Seed data/{key}.json from curated reference snapshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .reference import list_reference_keys, reference_as_collector


def seed_all(data_dir: Path | None = None, keys: list[str] | None = None) -> list[Path]:
    root = Path(__file__).resolve().parents[2]
    out = data_dir or root / "data"
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for key in keys or list_reference_keys():
        ref = reference_as_collector(key)
        if not ref:
            continue
        path = out / f"{key}.json"
        path.write_text(json.dumps(ref, indent=2, default=str), encoding="utf-8")
        written.append(path)
    return written


def main():
    parser = argparse.ArgumentParser(description="Seed collector JSON from reference data")
    parser.add_argument("keys", nargs="*", help="Company keys (default: all)")
    parser.add_argument("--data-dir", default="data")
    args = parser.parse_args()

    paths = seed_all(Path(args.data_dir), args.keys or None)
    for p in paths:
        print(f"Wrote {p}")


if __name__ == "__main__":
    main()
