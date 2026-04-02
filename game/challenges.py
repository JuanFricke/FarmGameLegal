"""
Challenge definitions for each crop type.

Each Challenge has:
  - crop_type      : which crop this challenge unlocks
  - title          : short display name
  - description    : multi-line task description shown in the code panel
  - starter_code   : the text pre-filled in the editor
  - test_cases     : list of (args_tuple, expected_result)
  - hints          : list of hint strings shown progressively on failure
  - score_base     : base score awarded on passing
  - score_fn       : optional callable(code_str) -> bonus_score (corn only)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
from .crop import CropType


@dataclass
class Challenge:
    crop_type: CropType
    title: str
    description: list[str]
    starter_code: str
    test_cases: list[tuple[tuple, Any]]
    hints: list[str]
    score_base: int
    function_name: str
    score_fn: Callable[[str], int] | None = None


# ---------------------------------------------------------------------------
# Helpers (defined first so they can be used in challenge definitions)
# ---------------------------------------------------------------------------

def _enc(text: str, key: str) -> str:
    """Simple additive Caesar cipher used to build pumpkin test cases."""
    if not key:
        return text
    return "".join(
        chr(ord(c) + ord(key[i % len(key)]))
        for i, c in enumerate(text)
    )


def _corn_score(code: str) -> int:
    """Return bonus points based on the sorting algorithm detected."""
    code_lower = code.lower()
    if "merge" in code_lower:
        return 200
    if "quick" in code_lower:
        return 180
    if "sorted(" in code_lower or ".sort(" in code_lower:
        return 50
    # Likely insertion / selection / bubble
    return 100


# ---------------------------------------------------------------------------
# 1. Potato — is_prime(n)
# ---------------------------------------------------------------------------

POTATO_CHALLENGE = Challenge(
    crop_type=CropType.POTATO,
    title="[Batata] Numeros Primos",
    description=[
        "Implemente a funcao is_prime(n).",
        "Retorne True se n for primo, False caso contrario.",
        "",
        "Exemplos:",
        "  is_prime(2)  -> True",
        "  is_prime(9)  -> False",
        "  is_prime(13) -> True",
    ],
    starter_code=(
        "def is_prime(n):\n"
        "    # seu código aqui\n"
        "    pass\n"
    ),
    function_name="is_prime",
    test_cases=[
        ((2,),  True),
        ((3,),  True),
        ((4,),  False),
        ((7,),  True),
        ((9,),  False),
        ((13,), True),
        ((1,),  False),
        ((0,),  False),
        ((17,), True),
        ((25,), False),
    ],
    hints=[
        "Dica: Números menores que 2 não são primos.",
        "Dica: Verifique se n é divisível por algum número de 2 até n-1.",
        "Dica: Basta checar divisores ate sqrt(n).",
        "Solução: return n >= 2 and all(n % i != 0 for i in range(2, int(n**0.5)+1))",
    ],
    score_base=100,
)


# ---------------------------------------------------------------------------
# 2. Carrot — is_multiple(n, m)
# ---------------------------------------------------------------------------

CARROT_CHALLENGE = Challenge(
    crop_type=CropType.CARROT,
    title="[Cenoura] Multiplos",
    description=[
        "Implemente a funcao is_multiple(n, m).",
        "Retorne True se n for multiplo de m.",
        "",
        "Exemplos:",
        "  is_multiple(9, 3)  -> True",
        "  is_multiple(7, 2)  -> False",
        "  is_multiple(0, 5)  -> True",
    ],
    starter_code=(
        "def is_multiple(n, m):\n"
        "    # seu código aqui\n"
        "    pass\n"
    ),
    function_name="is_multiple",
    test_cases=[
        ((9, 3),    True),
        ((7, 2),    False),
        ((0, 5),    True),
        ((12, 4),   True),
        ((11, 3),   False),
        ((100, 10), True),
        ((15, 7),   False),
        ((6, 6),    True),
    ],
    hints=[
        "Dica: Use o operador % (módulo).",
        "Dica: n é múltiplo de m se n % m == 0.",
        "Atenção: Verifique o caso m == 0 (divisão por zero).",
        "Solução: return m != 0 and n % m == 0",
    ],
    score_base=80,
)


# ---------------------------------------------------------------------------
# 3. Pumpkin — decode_hash(text, key)
# ---------------------------------------------------------------------------

PUMPKIN_CHALLENGE = Challenge(
    crop_type=CropType.PUMPKIN,
    title="[Abobora] Decodificacao",
    description=[
        "Implemente decode_hash(text, key).",
        "Cada char de text foi cifrado somando o",
        "valor ASCII da chave (ciclicamente).",
        "Reverta a cifra para recuperar o original.",
        "",
        "Exemplo (chave 'ab'):",
        "  cifrado = chr(ord('h')+ord('a')) + ...",
        "  decode_hash(cifrado, 'ab') -> 'hi'",
    ],
    starter_code=(
        "def decode_hash(text, key):\n"
        "    result = []\n"
        "    # seu código aqui\n"
        "    return ''.join(result)\n"
    ),
    function_name="decode_hash",
    test_cases=[
        ((_enc("hello", "abc"), "abc"), "hello"),
        ((_enc("Farm",  "xy"),  "xy"),  "Farm"),
        ((_enc("Python3", "k"), "k"),   "Python3"),
        ((_enc("abcdef", "z"),  "z"),   "abcdef"),
        ((_enc("",      "key"), "key"), ""),
    ],
    hints=[
        "Dica: Itere sobre os índices de text.",
        "Dica: Use key[i % len(key)] para obter a chave cíclica.",
        "Dica: Subtraia o valor ASCII da chave de cada char.",
        "Solução: chr(ord(c) - ord(key[i%len(key)])) for i,c in enumerate(text)",
    ],
    score_base=150,
)


# ---------------------------------------------------------------------------
# 4. Corn — sort_list(lst)   (bonus scoring by algorithm)
# ---------------------------------------------------------------------------

CORN_CHALLENGE = Challenge(
    crop_type=CropType.CORN,
    title="[Milho] Ordenacao (Bonus)",
    description=[
        "Implemente sort_list(lst).",
        "Retorne uma nova lista em ordem crescente.",
        "",
        "BONUS por algoritmo:",
        "  sorted() / .sort()  ->  +50 pts",
        "  Insertion / Bubble  -> +100 pts",
        "  Merge / Quick sort  -> +180-200 pts",
        "",
        "Exemplo:",
        "  sort_list([3,1,2]) -> [1,2,3]",
    ],
    starter_code=(
        "def sort_list(lst):\n"
        "    # seu código aqui\n"
        "    pass\n"
    ),
    function_name="sort_list",
    test_cases=[
        (([3, 1, 2],),       [1, 2, 3]),
        (([],),              []),
        (([5],),             [5]),
        (([2, 2, 1],),       [1, 2, 2]),
        (([9, 7, 5, 3, 1],), [1, 3, 5, 7, 9]),
        (([1, 2, 3, 4, 5],), [1, 2, 3, 4, 5]),
        (([-3, 0, -1, 2],),  [-3, -1, 0, 2]),
    ],
    hints=[
        "Dica: Você pode usar sorted(lst) para uma solução simples.",
        "Dica: Para bônus máximo, implemente merge sort ou quick sort.",
        "Dica: Merge sort divide a lista ao meio recursivamente.",
        "Certifique-se de retornar uma nova lista (não modificar a original).",
    ],
    score_base=120,
    score_fn=_corn_score,
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ALL_CHALLENGES: list[Challenge] = [
    POTATO_CHALLENGE,
    CARROT_CHALLENGE,
    PUMPKIN_CHALLENGE,
    CORN_CHALLENGE,
]
