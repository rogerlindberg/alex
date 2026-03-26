"""
Alex is a lexical analyzer tool. It reads and converts the input to a
list of Token objects. A Token contains a name end the lexeme as well
as the position in the input where it was found. (A lexeme is a sequence
of input characters that comprise a single token)

"""

import re



class AlexScanError(Exception):
    pass


class AlexDefinitionError(Exception):
    pass


class Alex:
    """
    Alex scans the input and searches for tokens in the following order:
      1) a newline string
      2) a character to skip
      3) a regexp word
            checks if the regexp word is a keyword.
      4) a keyword
      5) an operator word

    If the beginning of the input matches one of these, a Token object is
    created and the input pointer is moved forward in the input with the same
    length as the found lexeme.

    If there is no match, the program ends with an exception, except if the
    property skip_unrecognized_chars is set to True. In this case the next
    character in the input is ignored. The non-matching character is printed
    to stdout.

    Definitions of keywords, regular expression words and operators are
    given as input to the tool when it is created or via it's properties.

    Usage:
        alex = Alex(keywords=KEYWORDS, regexps=REGEXPS, operators=OPERATORS)
        alex.scanfile(path)
        for token in alex.tokens:
            print(token)
    """

    def __init__(
        self,
        skip_chars=" \t\r",
        newline="\n",
        keywords=None,
        regexps=None,
        operators=None,
        skip_unrecognized_chars=False,
        treat_unrecognized_chars_as_an_operator=False,
    ):
        """
        skipchars:  A string containing all characters that are to be
                    skipped from the input.

        newline:    is a string representing a line-break in the input text.
                    This information is used four counting lines in the input.
                    If you don't need line-counting, newline can be set to None.
                    The default value is '\n'.

        kewords:    Is a list (or tuple) of strings that represents keywords
                    of the input language. The token name for all keywords is
                    KEYWORD. The default value for keywords is an empty list.

        regexps:    Is a list (or tuple) of tuples, where each tuple has a
                    token name and a regular expression specifying the lexeme.
                    The regular expression must start with the ^ character.
                    If a regular expression matches the input and if the matched
                    word also is a keyword it will be treated as a keyword.

        operators:  is a tuple of tuple items. A tuple item has two values,
                    a token name and a lexeme description.
                        Example:
                        (
                            ('DOT', '.'),
                        ...
                            ('LTOREQ', '<='),
                        )
                    All token names specified must be unique!

        skip_unrecognized_chars:
                    By default, the program stops if it encounters an
                    unrecognized character in the input. You can change
                    this behavior by setting this property = True.

        treat_unrecognized_chars_as_an_operator:
                    Return the unrecognized character as a lexical element.
        """
        self.used_token_keys = set()
        self.used_token_keys.add("KEYWORD")
        self._tokens = []
        self._line_nbr = 1
        self._col_nbr = 1
        self._nbr_of_bytes = 0
        self._nbr_of_lines = 0
        self._nbr_of_skipped_chars = 0
        self._skip_chars = skip_chars
        self._newline = newline
        self._keywords = set(keywords or [])
        self._regexps = self._set_regexps(regexps or [])
        self._operators = self._set_operators(operators or [])
        self._skip_unrecognized_chars = skip_unrecognized_chars
        self._treat_unrecognized_chars_as_an_operator = (
            treat_unrecognized_chars_as_an_operator
        )

    @property
    def nbr_of_bytes(self):
        return self._nbr_of_bytes

    @property
    def nbr_of_lines(self):
        return self._nbr_of_lines

    @property
    def nbr_of_skipped_chars(self):
        return self._nbr_of_skipped_chars

    @property
    def tokens(self):
        return self._tokens

    def scan_file(self, path):
        """
        This function returns a list of Token objects representing the
        tokens found in the text of the input file.
        """
        import codecs

        with codecs.open(path, encoding="utf-8") as f:
            text = f.read()
        return self.scan(text)

    def scan(self, text):
        """
        This function returns a list of Token objects representing the
        tokens found in the given input text.
        """
        self._tokens = []
        self._line_nbr = 1
        self._col_nbr = 1
        self._nbr_of_bytes = len(text)
        self._nbr_of_lines = len(text.split(self._newline))
        while text:
            text = self._eat(text)
        return self._tokens

    def _eat(self, text):
        if self._is_newline(text):
            return self.eat_newline(text)
        if self._is_skipchar(text):
            return self._eat_text(text, 1)
        if self._operator_token_created(text):
            return self._eat_last_token(text)
        if self._regexp_token_created(text):
            return self._eat_last_token(text)
        if self._keyword_token_created(text):
            return self._eat_last_token(text)
        # Last resort. Skip the char
        if self._skip_unrecognized_chars:
            self._nbr_of_skipped_chars += 1
            return text[1:]
        elif self._treat_unrecognized_chars_as_an_operator:
            self._add_token("UNRECOGNIZED-CHAR", text[0])
            return self._eat_last_token(text)
        else:
            if len(self.tokens) == 0:
                raise AlexScanError(
                    f"Unrecognized char '{text[0]}' ordinal {ord(text[0])}\nFollowing 10 characters are: {text[1:11]}\nNo tokens was scanned"
                )
            else:
                raise AlexScanError(
                    f"Unrecognized char '{text[0]}' ordinal {ord(text[0])}\nFollowing 10 characters are: {text[1:11]}\nLast scanned Token: {self.tokens[-1]}"
                )

    def _is_newline(self, text):
        return self._newline and text[: len(self._newline)] == self._newline

    def _is_skipchar(self, text):
        if text[0] in self._skip_chars:
            self._nbr_of_skipped_chars += 1
            return True

    def _operator_token_created(self, text):
        for name, lexeme in self._operators:
            if text[: len(lexeme)] == lexeme:
                self._add_token(name, lexeme)
                return True

    def _keyword_token_created(self, text):
        for keyword in self._keywords:
            size = len(keyword)
            if text[:size] == keyword:
                self._add_token("KEYWORD", text[:size])
                return True

    def _regexp_token_created(self, text):
        for name, reg in self._regexps:
            m = reg.match(text)
            if m and len(m.group()) > 0:
                lexeme = m.group()
                if lexeme.endswith("\n"):
                    lexeme = lexeme[:-1]
                if lexeme in self._keywords:
                    self._add_token("KEYWORD", lexeme)
                else:
                    self._add_token(name, lexeme)
                return True

    def eat_newline(self, text):
        self._col_nbr = 1
        self._nbr_of_skipped_chars += len(self._newline)
        return self._eat_text(text, len(self._newline))

    def _eat_last_token(self, text):
        return self._eat_text(text, len(self._tokens[-1]._lexeme))

    def _eat_text(self, text, n):
        """
        If newline is set, we count the number if newlines in the token
        text, before removing the token text from the input text.
        """
        lexeme = text[:n]
        nbr_of_nl = lexeme.count(self._newline)
        if self._newline:
            self._line_nbr += nbr_of_nl
        if nbr_of_nl > 0:
            tail = lexeme.rsplit(self._newline, 1)[1]
            self._col_nbr = max(1, len(tail))
        else:
            self._col_nbr += len(lexeme)
        return text[n:]

    def _add_token(self, name, lexeme):
        self._tokens.append(Token(name, lexeme, self._line_nbr, self._col_nbr))

    #
    # Input registration
    #
    # This code is important, but it is moved here so that the logic of the
    # Lexical Analysis will be more understandable.
    #

    def _set_regexps(self, regexps):
        """
        We compile all regular expressions to get better performance.
        """
        self._validate_regexps(regexps)
        return self._compile_rexeps(regexps)

    def _compile_rexeps(self, regexps):
        return [(name, re.compile(reg)) for name, reg in regexps]

    def _set_operators(self, operators):
        """
        operators is a tuple of tuple items. A tuple item has two values,
        a token name and a lexeme description.
        Example:
        (
            (DOT, '.'),
        ...
            ('LTOREQ', '<='),
        )
        """
        ops = self._sort_operators(operators)
        self._validate_operators(ops)
        return ops

    @staticmethod
    def _sort_operators(operators):
        """Sort operators by longest lexeme first."""
        return sorted(operators, key=lambda tup: len(tup[1]), reverse=True)

    #
    # Validation of inputs
    #

    def _validate_regexps(self, regexps):
        self._validate_regexps_syntax(regexps)
        self._validate_regexps_token_names(regexps)

    def _validate_regexps_syntax(self, regexps):
        invalid_regexps = [t for t in regexps if t[1][0] != "^"]
        if invalid_regexps:
            print("A regexp must start with the ^ characters.")
            print("The following items are not following that rule!")
            for regexp in invalid_regexps:
                print("%-6s '%s'" % regexp)
                raise SyntaxError("Invalid regexps!")

    def _validate_regexps_token_names(self, regexps):
        for key, _ in regexps:
            if key in self.used_token_keys:
                raise ValueError(
                    "Invalid regexp. The key '%s' has already been used!" % key
                )
            self.used_token_keys.add(key)

    def _validate_operators(self, operators):
        self._validate_operators_lexemes(operators)
        self._validate_operators_keys(operators)

    def _validate_operators_keys(self, operators):
        for name, _ in operators:
            if name in self.used_token_keys:
                raise AlexDefinitionError(
                    f'Invalid operator. The key {name} has already been used!'
                )
            self.used_token_keys.add(name)

    @staticmethod
    def _validate_operators_lexemes(operators):
        for name, lexeme in operators:
            if len(lexeme) == 0:
                raise AlexDefinitionError(f'Invalid operator. Value length is zero for {name}')


class Token:

    def __init__(self, name, lexeme, lineno=0, colno=0):
        self._name = name
        self._lexeme = lexeme
        self._lineno = lineno
        self._colno = colno

    @property
    def name(self):
        return self._name

    @property
    def lexeme(self):
        return self._lexeme

    @property
    def lineno(self):
        return self._lineno

    @property
    def colno(self):
        return self._colno

    def __repr__(self):
        return "%5d:%3d  %-12s %-12s" % (
            self._lineno,
            self._colno,
            self._name,
            self._lexeme,
        )
