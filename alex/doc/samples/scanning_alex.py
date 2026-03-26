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
    ("REM", '^#[^\n]*'),
    ("ID", f"^[a-zA-Z_]*"),
)
KEYWORDS = [
    'if',
    'then',
]

lexer = alex.Alex(
    operators=OPERATORS,
    regexps=REGEXPS,
    keywords=KEYWORDS)

lexer.scan_file(os.path.join('..', '..', 'main.py'))
#lexer.scan('  #')

print('----(Tokens found)----------')
for token in lexer.tokens:
    print(token)
