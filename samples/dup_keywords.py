"""
Duplicated keywords are silently ignored.

"""

import alex


OPERATORS = (
    ("EQ", "="),
    ("EQEQ", "=="),
)
REGEXPS = (
    ("ID", f"^[a-zA-Z_]*"),
    ("NUM", '^["0123456789"]*'),
)
KEYWORDS = [
    "if",
    "if",
    "then",
]

lexer = alex.Alex(operators=OPERATORS, regexps=REGEXPS, keywords=KEYWORDS)

lexer.scan(
    """if foo == bar 
then x = 17"""
)

print("----(Tokens found)----------")
for token in lexer.tokens:
    print(token)
