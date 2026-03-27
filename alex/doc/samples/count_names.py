from collections import Counter
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

    "self",
    "dict",
    "set",
    "string",
    "isinstance",
    "args",
    "kwargs",
]

lexer = alex.Alex(
    operators=OPERATORS, regexps=REGEXPS, keywords=KEYWORDS, scan_python_indents=True
)

lexer.scan_file("test.py")

print("----(Counting 20 most common occurrences of identifier names)----------")
names = [token.lexeme for token in lexer.tokens if token.name == 'ID']
counter = Counter(names).most_common(20)
for name, length in counter:
    print(f'{length:3} {name}')