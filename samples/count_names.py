from collections import Counter
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


def count_names(count=10, verbose=False):
    path = os.path.join("..", "alex", "__init__.py")
    lexer = alex.Alex(operators=OPERATORS, regexps=REGEXPS)
    lexer.scan_file(path)
    print_report(lexer, count, verbose)


def print_report(lexer, count, verbose):
    if verbose:
        print("----(Tokens found)----------")
        for token in lexer.tokens:
            print(token)
    print(
        f"----(Counting {count} most common occurrences of identifier names)----------"
    )
    names = [token.lexeme for token in lexer.tokens if token.name == "ID"]
    counter = Counter(names).most_common(count)
    for name, length in counter:
        print(f"{length:3} {name}")


if __name__ == "__main__":
    count_names(verbose=False)
