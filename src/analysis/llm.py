"""
LLM client for CIT analysis — OpenClaude, litellm, or template fallback.

Environment:
  CIT_LLM_BACKEND=openclaude|litellm|auto   (default: auto)
  CIT_LLM_MODEL=...                         (litellm only)
  LITELLM_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY
"""

from __future__ import annotations

import json
import os
import re
from typing import Optional, Protocol


class LLMBackend(Protocol):
    @property
    def available(self) -> bool: ...
    def complete(self, system: str, user: str, temperature: float = 0.4) -> Optional[str]: ...
    def complete_json(self, system: str, user: str, temperature: float = 0.3) -> Optional[dict]: ...


class LiteLLMClient:
    def __init__(self, model: Optional[str] = None):
        self.model = model or os.environ.get("CIT_LLM_MODEL", "gpt-4o-mini")
        self._available: Optional[bool] = None

    @property
    def available(self) -> bool:
        if self._available is None:
            has_key = bool(
                os.environ.get("LITELLM_API_KEY")
                or os.environ.get("OPENAI_API_KEY")
                or os.environ.get("ANTHROPIC_API_KEY")
            )
            if not has_key:
                self._available = False
            else:
                try:
                    import litellm  # noqa: F401
                    self._available = True
                except ImportError:
                    self._available = False
        return self._available

    def complete(self, system: str, user: str, temperature: float = 0.4) -> Optional[str]:
        if not self.available:
            return None
        try:
            from litellm import completion

            resp = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=2048,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception:
            return None

    def complete_json(self, system: str, user: str, temperature: float = 0.3) -> Optional[dict]:
        text = self.complete(
            system + "\n\nRespond with valid JSON only — no markdown fences.",
            user,
            temperature,
        )
        return parse_json(text) if text else None


class OpenClaudeLLMClient:
    """Uses `openclaude -p` with project .openclaude-profile.json."""

    def __init__(self):
        self._runner = None
        self._available: Optional[bool] = None

    def _get_runner(self):
        if self._runner is None:
            from src.integration.openclaude_runner import OpenClaudeRunner
            self._runner = OpenClaudeRunner()
        return self._runner

    @property
    def available(self) -> bool:
        if self._available is None:
            if os.environ.get("CIT_LLM_BACKEND", "").lower() == "litellm":
                self._available = False
            else:
                self._available = self._get_runner().available
        return self._available

    def complete(self, system: str, user: str, temperature: float = 0.4) -> Optional[str]:
        return self._get_runner().complete(system, user)

    def complete_json(self, system: str, user: str, temperature: float = 0.3) -> Optional[dict]:
        return self._get_runner().complete_json(system, user)


def parse_json(text: str) -> Optional[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    return None


# Back-compat alias
_parse_json = parse_json


class LLMClient:
    """Facade: picks backend by CIT_LLM_BACKEND."""

    def __init__(self):
        self._backend: LLMBackend | None = None

    def _resolve(self) -> LLMBackend | None:
        if self._backend is not None:
            return self._backend

        pref = os.environ.get("CIT_LLM_BACKEND", "auto").lower()
        oc = OpenClaudeLLMClient()
        ll = LiteLLMClient()

        if pref == "openclaude":
            self._backend = oc if oc.available else None
        elif pref == "litellm":
            self._backend = ll if ll.available else None
        else:  # auto
            if oc.available:
                self._backend = oc
            elif ll.available:
                self._backend = ll
            else:
                self._backend = None
        return self._backend

    @property
    def available(self) -> bool:
        b = self._resolve()
        return b is not None and b.available

    @property
    def backend_name(self) -> str:
        b = self._resolve()
        if b is None:
            return "none"
        if isinstance(b, OpenClaudeLLMClient):
            return "openclaude"
        if isinstance(b, LiteLLMClient):
            return "litellm"
        return "unknown"

    def complete(self, system: str, user: str, temperature: float = 0.4) -> Optional[str]:
        b = self._resolve()
        return b.complete(system, user, temperature) if b else None

    def complete_json(self, system: str, user: str, temperature: float = 0.3) -> Optional[dict]:
        b = self._resolve()
        return b.complete_json(system, user, temperature) if b else None


_default_client: Optional[LLMClient] = None


def get_client() -> LLMClient:
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client
