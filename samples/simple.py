from alex import Alex

OPERATORS = (("ADD", "+"), ("SUB", "-"))
REGEXPS = (("NUM", '^["0123456789"]*'),)


def run_simple():
    lexer = Alex(operators=OPERATORS, regexps=REGEXPS)
    lexer.scan("1 + 2 - 123")
    print_report(lexer)


def print_report(lexer):
    print("----(Tokens found)----------")
    for token in lexer.tokens:
        print(token)


if __name__ == "__main__":
    run_simple()
