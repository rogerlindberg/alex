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
    ("AT", "@"),
    ("TYPE", "->"),
    ("PERCENT", "%"),
    ("EQ", "="),
    ("NEQ", "!="),
    ("GT", ">"),
    ("LT", "<"),
    ("EQEQ", "=="),
    ("LP", "("),
    ("RP", ")"),
    ("LBR", "["),
    ("RBR", "]"),
)
REGEXPS = (
    ("ID", f"^[a-zA-Z_]*"),
    ("STR", r'^"(?:\\.|[^"\\])*"|^\'(?:\\.|[^\'\\])*\''),
    ("NUM", '^["0123456789"]*'),
    ("REM", '^#[^\n]*'),
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
