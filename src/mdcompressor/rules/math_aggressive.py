from __future__ import annotations

from ..models import RuleResult
from .base import BaseRule


class MathMacroToUnicodeRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="math-macro-to-unicode",
            description="Replace selected LaTeX macros with unicode symbols",
            risk="high",
            targets={"math_inline", "math_block"},
        )
        self.mapping = {
            r"\alpha": "α",
            r"\beta": "β",
            r"\gamma": "γ",
            r"\delta": "δ",
            r"\epsilon": "ε",
            r"\varepsilon": "ε",
            r"\theta": "θ",
            r"\vartheta": "ϑ",
            r"\lambda": "λ",
            r"\mu": "μ",
            r"\nu": "ν",
            r"\sigma": "σ",
            r"\Sigma": "Σ",
            r"\omega": "ω",
            r"\Omega": "Ω",
            r"\pi": "π",
            r"\phi": "φ",
            r"\varphi": "φ",
            r"\psi": "ψ",
            r"\times": "×",
            r"\cdot": "·",
            r"\pm": "±",
            r"\to": "→",
            r"\rightarrow": "→",
            r"\leftarrow": "←",
            r"\leftrightarrow": "↔",
            r"\infty": "∞",
            r"\approx": "≈",
            r"\leq": "≤",
            r"\geq": "≥",
            r"\neq": "≠",
        }

    def apply(self, text: str) -> tuple[str, RuleResult]:
        out = text
        for src, dst in self.mapping.items():
            out = out.replace(src, dst)
        return out, RuleResult(self.id, out != text, len(text) - len(out), "high-risk macro replacement")
