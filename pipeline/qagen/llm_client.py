"""
Thin client for a local OpenAI-compatible LLM server (SPEC.md §6.3 —
"serve a local model ... on the A5000"). No API key: this hits
http://localhost, never a hosted provider, so CLAUDE.md's "no API keys in
client code" is moot here (and this is pipeline code, not client code,
regardless).

Defaults to Ollama (already running on this machine as a stable service
with qwen2.5:32b / qwen3:32b pre-pulled — SPEC.md named vLLM specifically,
but Ollama serves the identical OpenAI-compatible /v1/chat/completions
contract this module needs, with zero extra setup vs. vLLM's CUDA/torch
version-matching fight documented in PROGRESS.md). Point VLLM_BASE_URL at
a real vLLM server instead if you stand one up later — nothing else in
this file needs to change.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import requests

# Models routinely emit raw LaTeX inside JSON string values (e.g. `$20\%$`,
# `Rs.\;493`) — valid in a LaTeX source but not valid JSON, since `\%` and
# `\;` aren't recognised JSON escapes. Rather than reject every draft that
# contains math, double up any backslash that isn't already starting a
# real JSON escape sequence before parsing.
_INVALID_JSON_ESCAPE = re.compile(r'\\(?![\\"/bfnrtu])')


def _fix_invalid_json_escapes(text: str) -> str:
    return _INVALID_JSON_ESCAPE.sub(r"\\\\", text)

VLLM_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://localhost:11434/v1")
MODEL_NAME = os.environ.get("VLLM_MODEL_NAME", "qwen2.5:32b")


class LLMError(Exception):
    pass


def _chat(messages: list[dict[str, str]], temperature: float, max_tokens: int = 2048) -> str:
    # This shared, single-request-at-a-time Ollama instance occasionally
    # takes well over a minute on a long generation under real load — a
    # ReadTimeout here is routine, not exceptional, and previously escaped
    # as a raw requests exception (only HTTP-status failures were wrapped
    # in LLMError), which crashed an entire multi-hour batch run on one
    # slow call. Both network-level and HTTP-status failures now raise the
    # same LLMError so every caller's existing `except LLMError` handling
    # covers both.
    try:
        resp = requests.post(
            f"{VLLM_BASE_URL}/chat/completions",
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=300,
        )
    except requests.RequestException as e:
        raise LLMError(f"request to {VLLM_BASE_URL} failed: {e}") from e
    if not resp.ok:
        raise LLMError(f"LLM request failed: {resp.status_code} {resp.text[:500]}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def chat_json(system: str, user: str, temperature: float = 0.7, max_tokens: int = 2048) -> dict[str, Any]:
    """Chat call that expects a single JSON object back. Strips markdown
    code fences if the model wraps its output in ```json ... ``` anyway."""
    text = _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(_fix_invalid_json_escapes(cleaned))
    except json.JSONDecodeError as e:
        raise LLMError(f"Model did not return valid JSON: {e}\nRaw: {text[:1000]}") from e


def chat_text(system: str, user: str, temperature: float = 0.8, max_tokens: int = 512) -> str:
    return _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
        max_tokens=max_tokens,
    ).strip()


def server_is_up() -> bool:
    try:
        r = requests.get(f"{VLLM_BASE_URL}/models", timeout=5)
        return r.ok
    except requests.RequestException:
        return False
