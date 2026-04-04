"""
Count the number of occurrences of the most common words in the given
input text.

Print a sorted top list to stdout.

In this example, the input is this file and the expected output is:

    ----(Counting 5 most common occurrences of identifier names)----------
      3 lexer
      3 token
      2 Counter
      2 alex
      2 REGEXPS
"""

from collections import Counter
import alex


REGEXPS = (
    ("ID", f"^[a-zåäöA-ZÅÄÖ_0-9-]*"),
)


def main(top=10):
    lexer = alex.Alex(regexps=REGEXPS, skip_unrecognized_chars=True)
    scan(lexer)
    print_report(lexer, top)


def scan(lexer):
    lexer.scan_file("text.txt")


def print_report(lexer, top):
    print(
        f"----(Counting {top} most common word occurrences)----------"
    )
    names = [token.lexeme for token in lexer.tokens if token.name == "ID"]
    counter = Counter(names).most_common(top)
    for name, length in counter:
        print(f"{length:3} {name}")


if __name__ == "__main__":
    main(12)
