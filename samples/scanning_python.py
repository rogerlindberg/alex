import os
import alex


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

lexer = alex.Alex(
    operators=OPERATORS, regexps=REGEXPS, keywords=KEYWORDS, scan_python_indents=True
)

path = os.path.join('..', 'alex', '__init__.py')
lexer.scan_file(path)


print("----(Tokens found)----------")
for token in lexer.tokens:
    print(token)
