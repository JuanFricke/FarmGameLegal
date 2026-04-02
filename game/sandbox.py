"""
Sandboxed Python code execution for player-submitted solutions.

Returns a RunResult with:
  - passed     : bool — all tests passed
  - score      : int  — points earned
  - error      : str  — compile / runtime error message (if any)
  - cases      : list[CaseResult] — per-test-case details
"""
from __future__ import annotations
import threading
from dataclasses import dataclass, field
from typing import Any
from .challenges import Challenge

# ---------------------------------------------------------------------------
# Safe builtins whitelist
# ---------------------------------------------------------------------------

_BUILTINS_SOURCE = (
    __builtins__ if isinstance(__builtins__, dict) else vars(__builtins__)  # type: ignore
)

_SAFE_BUILTINS = {
    name: _BUILTINS_SOURCE[name]
    for name in (
        "abs", "all", "any", "bin", "bool", "chr", "dict", "divmod",
        "enumerate", "filter", "float", "format", "frozenset", "hash",
        "hex", "int", "isinstance", "issubclass", "iter", "len", "list",
        "map", "max", "min", "next", "oct", "ord", "pow", "print",
        "range", "repr", "reversed", "round", "set", "slice", "sorted",
        "str", "sum", "tuple", "type", "zip", "True", "False", "None",
    )
    if name in _BUILTINS_SOURCE
}


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class CaseResult:
    args: tuple
    expected: Any
    passed: bool
    got: Any = None
    error: str = ""

    def label(self, func_name: str) -> str:
        args_str = ", ".join(repr(a) for a in self.args)
        call = f"{func_name}({args_str})"
        if self.error:
            return f"[ERR]  {call}  =>  {self.error[:40]}"
        if self.passed:
            return f"[OK]   {call}  =>  {self.expected!r}"
        return f"[FAIL] {call}  =>  esperado {self.expected!r}, obtido {self.got!r}"


@dataclass
class RunResult:
    passed: bool
    score: int = 0
    error: str = ""
    cases: list[CaseResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

_TIMEOUT = 3.0


def _exec_thread(code: str, ns: dict, holder: list) -> None:
    try:
        exec(code, ns)  # noqa: S102
        holder.append(("ok", ns))
    except Exception as exc:  # noqa: BLE001
        holder.append(("error", str(exc)))


def run_challenge(challenge: Challenge, code: str) -> RunResult:
    """Execute *code* and evaluate all test cases for *challenge*."""
    ns: dict[str, Any] = {"__builtins__": _SAFE_BUILTINS}
    holder: list = []

    t = threading.Thread(target=_exec_thread, args=(code, ns, holder), daemon=True)
    t.start()
    t.join(timeout=_TIMEOUT)

    if t.is_alive():
        return RunResult(passed=False, error="Tempo limite excedido (loop infinito?).")

    if not holder:
        return RunResult(passed=False, error="Execucao falhou sem mensagem.")

    status, payload = holder[0]
    if status == "error":
        return RunResult(passed=False, error=f"Erro: {payload}")

    func = ns.get(challenge.function_name)
    if func is None or not callable(func):
        return RunResult(
            passed=False,
            error=f"Funcao '{challenge.function_name}' nao encontrada.",
        )

    cases: list[CaseResult] = []
    all_passed = True

    for args, expected in challenge.test_cases:
        try:
            got = func(*args)
            ok = got == expected
            cases.append(CaseResult(args=args, expected=expected, passed=ok, got=got))
            if not ok:
                all_passed = False
        except Exception as exc:  # noqa: BLE001
            cases.append(CaseResult(
                args=args, expected=expected, passed=False, error=str(exc)
            ))
            all_passed = False

    bonus = challenge.score_fn(code) if (all_passed and challenge.score_fn) else 0
    score = (challenge.score_base + bonus) if all_passed else 0
    return RunResult(passed=all_passed, score=score, cases=cases)
