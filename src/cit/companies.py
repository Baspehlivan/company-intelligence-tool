"""Load company registry from config/companies.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[2]

__all__ = ["ROOT", "load_companies", "load_compare_pairs", "get_company", "load_targets", "slug_for"]
COMPANIES_FILE = ROOT / "config" / "companies.yaml"
TARGETS_FILE = ROOT / "config" / "targets.yaml"


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise ImportError("PyYAML required: pip install pyyaml")
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def load_companies(config_path: Path | None = None) -> list[dict[str, Any]]:
    data = _load_yaml(config_path or COMPANIES_FILE)
    return list(data.get("companies", []))


def load_compare_pairs(config_path: Path | None = None) -> list[tuple[str, str]]:
    data = _load_yaml(config_path or COMPANIES_FILE)
    pairs = []
    for item in data.get("compare_pairs", []):
        if isinstance(item, list) and len(item) == 2:
            pairs.append((item[0], item[1]))
    return pairs


def get_company(key: str, config_path: Path | None = None) -> dict[str, Any] | None:
    key = key.lower().strip()
    for c in load_companies(config_path):
        if c.get("key", "").lower() == key or c.get("name", "").lower() == key:
            return c
    return None


def load_targets(config_path: Path | None = None) -> list[dict[str, Any]]:
    """Backward-compatible targets list for batch."""
    companies = load_companies(config_path)
    if companies:
        return [
            {
                "name": c["name"],
                "key": c.get("key"),
                "from_file": c.get("from_file"),
                "ticker": c.get("ticker"),
            }
            for c in companies
        ]
    # Fallback to legacy targets.yaml
    data = _load_yaml(TARGETS_FILE)
    return data.get("targets", [])


def slug_for(company: dict[str, Any]) -> str:
    return company.get("key") or company["name"].lower().replace(" ", "-")
