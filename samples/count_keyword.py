"""
Count the number of occurrences of a keyword, in this
sample the 'if'-keyword.

The goal is to not count words in comments, therefore we define the
regexps TSTR, STR och REM.

The regexp ID is used to identify a word.

The argument ('if',) is an iterable with the keyword we are looking for.
"""

import os
import alex

REGEXPS = (
    ("TSTR", r'^f?"""(?:\\.|(?!""").)*?"""|^f?\'\'\'(?:\\.|(?!\'\'\').)*?\'\'\''),
    ("STR", r'^f?"(?:\\.|[^"\\])*"|^f?\'(?:\\.|[^\'\\])*\''),
    ("REM", "^#[^\n]*"),
    ("ID", f"^[a-zA-Z_0-9]*"),
)


def count_if(verbose=False):
    path = os.path.join("..", "alex", "__init__.py")
    lexer = alex.Alex(regexps=REGEXPS, keywords=("if",), skip_unrecognized_chars=True)
    lexer.scan_file(path)
    print_report(lexer, verbose)


def print_report(lexer, verbose):
    if verbose:
        print("----(Tokens found:)----------")
        for token in lexer.tokens:
            print(token)
    print("----(Counting nbr of if-statements)----------")
    occurrences = len(
        [
            token
            for token in lexer.tokens
            if token.name == "KEYWORD" and token.lexeme == "if"
        ]
    )
    print(f'Number of occurrences of "if"-statements: {occurrences}')


if __name__ == "__main__":
    count_if(verbose=False)
