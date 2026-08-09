"""
Sandboxed execution of LLM-generated verifier programs (SPEC.md §6.3 step
1-3): "execute that program in a sandboxed subprocess with a timeout" and
"accept only if the program's output equals the claimed answer."

Not a full seccomp jail — this runs on the project owner's own machine
against code generated for a narrow, known task (compute a numeric/string
answer from arithmetic), not arbitrary untrusted internet input. The
controls here (subprocess isolation, CPU/memory rlimits, timeout, import
allowlist) match what SPEC.md asks for without overbuilding a jail this
threat model doesn't need.
"""

from __future__ import annotations

import json
import re
import resource
import subprocess
import sys
import tempfile
from pathlib import Path

ALLOWED_IMPORTS = {"math", "sympy", "fractions", "itertools", "decimal", "statistics", "cmath"}
FORBIDDEN_PATTERNS = [
    r"\bimport\s+os\b",
    r"\bimport\s+sys\b",
    r"\bimport\s+subprocess\b",
    r"\bimport\s+socket\b",
    r"\b__import__\b",
    r"\bopen\s*\(",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bcompile\s*\(",
    r"\bglobals\s*\(",
    r"\bgetattr\s*\(",
]

RUNNER_TEMPLATE = """
import json as _json

{code}

_result = compute()
# sympy numeric types (Float, Integer, Rational, ...) aren't natively JSON-serializable —
# coerce to a plain Python type first rather than letting a correct answer fail to report
# just because it came out of a symbolic computation.
try:
    _json.dumps(_result)
except TypeError:
    try:
        _result = float(_result)
    except (TypeError, ValueError):
        _result = str(_result)
print(_json.dumps({{"ok": True, "result": _result}}))
"""


class SandboxRejected(Exception):
    pass


def _static_check(code: str) -> None:
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            module = stripped.split()[1].split(".")[0]
            if module not in ALLOWED_IMPORTS:
                raise SandboxRejected(f"disallowed import: {module}")
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, code):
            raise SandboxRejected(f"forbidden pattern matched: {pattern}")
    if "def compute(" not in code:
        raise SandboxRejected("verifier code must define a `compute()` function")


def _limit_resources() -> None:
    # 5s CPU time, 512MB address space — a runaway/hostile program dies
    # fast instead of eating the box.
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))


def run_verifier(code: str, timeout: float = 8.0) -> tuple[bool, object | None, str]:
    """Returns (ok, result, error_message). ok=False on any failure —
    static-check rejection, non-zero exit, timeout, or bad output shape."""
    try:
        _static_check(code)
    except SandboxRejected as e:
        return False, None, str(e)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "verifier.py"
        script_path.write_text(RUNNER_TEMPLATE.format(code=code))
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=_limit_resources,
            )
        except subprocess.TimeoutExpired:
            return False, None, "verifier timed out"

        if proc.returncode != 0:
            return False, None, f"verifier exited {proc.returncode}: {proc.stderr[-500:]}"

        try:
            payload = json.loads(proc.stdout.strip().splitlines()[-1])
        except (json.JSONDecodeError, IndexError):
            return False, None, f"verifier produced non-JSON output: {proc.stdout[:500]!r}"

        if not payload.get("ok"):
            return False, None, "verifier reported failure"
        return True, payload.get("result"), ""
