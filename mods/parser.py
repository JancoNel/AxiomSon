"""Parser utilities for Sound codewar.

Provides `parse_expr(text)` which parses a user-supplied mathematical expression
using `sympy.sympify` and returns a callable that accepts numeric x,y,z inputs.

The function returns a tuple `(fn, meta)` where `fn` is a python-callable that
accepts floats or numpy arrays, and `meta` contains `symbols` and `expr`.
"""
from typing import Any, Callable, Dict, Tuple #  Python 3.14 types are not for the faint of heart

def parse_expr(expr_text: str) -> Tuple[Callable[..., Any], Dict[str, Any]]:
    """Parse `expr_text` into a numeric function f(x,y,z).

    Returns (fn, meta). `fn(x,y,z)` accepts floats or numpy arrays.
    """
    try:
        import sympy as sp
        import numpy as np
    except Exception as e:
        raise RuntimeError("sympy and numpy are required to parse expressions") from e

    # define allowed symbols and safe namespace
    x, y, z = sp.symbols('x y z')

    # Parse expression using sympy.sympify (raises on invalid input)
    expr = sp.sympify(expr_text, locals={})

    # ensure only allowed free symbols are used
    free = {str(s) for s in expr.free_symbols}
    allowed = {'x', 'y', 'z'}
    if not free.issubset(allowed):
        raise ValueError(f"Expression uses unsupported symbols: {free - allowed}")

    # lambdify to a numpy-aware function
    fn = sp.lambdify((x, y, z), expr, modules=['numpy'])

    # metadata dictionary 
    meta = {
        'expr': expr,
        'symbols': sorted(list(free)), # For some reason I only now realised I am allowed to run functions in inside lists
        'text': expr_text,
    }

    return fn, meta
