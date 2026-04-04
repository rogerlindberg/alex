"""
Find all function definitions in a Python file.
Also nested functions should be detected.

Input:
    def a():
        def aa():
            pass
        def ab():
            pass
        pass

    def b():
        def ba():
            pass
        def bb():
            pass
            def bba():
                pass
        def bc():
            pass
        pass

Generates the output:
        ----(Function definitions)--------
        Name:a NbrOfTokens: 6 NbrOfFuncs: 2
            Name:aa NbrOfTokens: 6 NbrOfFuncs: 0
            Name:ab NbrOfTokens: 6 NbrOfFuncs: 0
        Name:b NbrOfTokens: 6 NbrOfFuncs: 3
            Name:ba NbrOfTokens: 6 NbrOfFuncs: 0
            Name:bb NbrOfTokens: 6 NbrOfFuncs: 1
                Name:bba NbrOfTokens: 6 NbrOfFuncs: 0
            Name:bc NbrOfTokens: 6 NbrOfFuncs: 0

"""

import alex
from alex.tools import create_python_function_tree

OPERATORS = (
    ("PLUS", "+"),
    ("MINUS", "-"),
    ("MUL", "*"),
    ("DIV", "/"),
    ("DOT", "."),
    ("COMMA", ","),
    ("COLON", ":"),
    ("SEMI", ";"),
    ("AT", "@"),
    ("MOD", "%"),
    ("EQ", "="),
    ("GT", ">"),
    ("LT", "<"),
    ("LP", "("),
    ("RP", ")"),
    ("LBR", "["),
    ("RBR", "]"),
    ("LCBR", "{"),
    ("RCBR", "}"),
    ("OR", "|"),
    ("XOR", "^"),
    ("NOT", "~"),
    ("AND", "&"),
    ("ADDEQ", "+="),
    ("SUBEQ", "-="),
    ("MULEQ", "*="),
    ("DIVEQ", "/="),
    ("IDIVEQ", "//="),
    ("MODEQ", "%="),
    ("LSHIFT", "<<"),
    ("RSHIFT", ">>"),
    ("IDIV", "//"),
    ("EXP", "**"),
    ("GE", ">="),
    ("LE", "<="),
    ("TYPE", "->"),
    ("NEQ", "!="),
    ("EQEQ", "=="),
    ("OREQ", "|="),
    ("XOREQ", "^="),
    ("ANDEQ", "&="),
    ("WALRUS", ":="),
    ("EXPEQ", "**="),
    ("LSHIFTEQ", "<<="),
    ("RSHIFTEQ", ">>="),
)
REGEXPS = (
    ("TSTR", r'^f?"""(?:\\.|(?!""").)*?"""|^f?\'\'\'(?:\\.|(?!\'\'\').)*?\'\'\''),
    ("STR", r'^f?"(?:\\.|[^"\\])*"|^f?\'(?:\\.|[^\'\\])*\''),
    ("NUM", '^["0123456789"]*'),
    ("REM", "^#[^\n]*"),
    ("ID", f"^[a-zA-Z_0-9]*"),
)
KEYWORDS = [
    "False",
    "None",
    "True",
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
]


TEXT = """\
def a():
    def aa():
        pass
    def ab():
        pass
    pass

def b():
    def ba():
        pass
    def bb():
        pass
        def bba():
            pass
    def bc():
        pass
    pass"""


def main():
    lexer = scan()


def scan():
    lexer = alex.Alex(
        operators=OPERATORS,
        regexps=REGEXPS,
        keywords=KEYWORDS,
    )
    gen = lexer.generate(TEXT)
    print("----(Function definitions)--------")
    for func in create_python_function_tree(gen):
        print_function(func)
    return lexer


def print_function(func, indent=0):
    print(f'{" " * indent}{func}')
    for f in func.funcs:
        print_function(f, indent + 4)


if __name__ == "__main__":
    main()
