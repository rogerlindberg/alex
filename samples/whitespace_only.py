from alex import Alex


REGEXPS = (("WORD", f"^[a-zA-Z_][a-zA-Z_0-9-’]*"),)
TEXT = "  \n   "


class AlexTest:
    """
    Input:
        This test examines only spaces input.

    Output:
        ----(Tokens)--------
            1:  1  INDENT       2
            2:  1  INDENT       3
    """

    def scan(self):
        self.lexer = Alex(
            regexps=REGEXPS, skip_unrecognized_chars=True, scan_python_indents=True
        )
        self.lexer.scan(TEXT)
        self.print_report()

    def print_report(self):
        print("----(Tokens)--------")
        for token in self.lexer.tokens:
            print(token)


AlexTest().scan()
