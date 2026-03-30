"""
Determine the nesting level of each function in the input text by analyzing
indentation.

Example:
    Given this file as input, the expected output is:

        Nesting levels for functions:
        Levels Function
        ------ -------------------------------------
           1   main
           2   scan
           4   measure_nesting
           2   print_report
"""

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

from alex.tools import create_python_function_tree, nodes


def main():
    gen = scan()
    result = []
    for node in create_python_function_tree(gen):
        calc_points(node, result)
    print_result(result)


def scan():
    lexer = alex.Alex(
        operators=OPERATORS,
        regexps=REGEXPS,
        keywords=KEYWORDS,
    )
    return lexer.generate_file("python_test.py")


def calc_points(func_node, result):
    func_node.points = 1
    for token in func_node.tokens:
        if token.lexeme in (
            "if",
            "elif",
            "for",
            "else",
            "while",
            "try",
            "except",
            "finally",
            "with",
            "and",
            "or",
        ):
            func_node.points += 1
    result.append((func_node.name, func_node.points))
    for func in func_node.func_nodes:
        calc_points(func, result)


def print_result(result):
    result = sorted(result, key=lambda item: item[1], reverse=True)
    for name, points in result[:10]:
        print(f"{points:3} {name}")



if __name__ == "__main__":
    main()
