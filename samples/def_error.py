"""
This sample demonstrates what happens when there exists
duplicate keywords in the definitions.

"""

import alex


OPERATORS = (
    ("ADD", "+"),
    ("ADD", "-"),
)

REGEXPS = (("NUM", '^["0123456789"]*'),)


def demonstrate():
    try:
        lexer = alex.Alex(operators=OPERATORS, regexps=REGEXPS)
    except alex.AlexDefinitionError as ex:
        print("----(Error report)----------")
        print(ex)


if __name__ == "__main__":
    demonstrate()
