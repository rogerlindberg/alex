"""
Alex is a lexical analyzer tool.

It reads an input string and converts it into a list of `Token` objects.
Each `Token` contains:

- a name (token type)
- the lexeme (the exact matched text)
- the position in the input where it was found

A lexeme is a sequence of input characters that together form a single token.
"""

import re
import codecs

__version__ = '0.1.1'


class AlexScanError(Exception):
    """Raised when the lexer encounters invalid input during scanning."""
    pass


class AlexDefinitionError(Exception):
    """Raised when definitions or lexer configuration are invalid."""
    pass


class Token:
    """Represents a lexical token produced by the Alex lexer.

    A token consists of:
    - a name (token type)
    - the lexeme (the exact matched text)
    - the line number where it was found
    - the column number where it was found

    Attributes:
        name: The token type.
        lexeme: The matched text.
        line_nbr: Line number in the input (0-based or 1-based depending on lexer).
        col_nbr: Column number in the input.
    """

    def __init__(self, name: str, lexeme: str, line_nbr: int = 0, col_nbr: int = 0):
        self._name = name
        self._lexeme = lexeme
        self._line_nbr = line_nbr
        self._col_nbr = col_nbr

    @property
    def name(self) -> str:
        """The token type."""
        return self._name

    @property
    def lexeme(self) -> str:
        """The exact matched text."""
        return self._lexeme

    @property
    def line_nbr(self) -> int:
        """The line number where the token was found."""
        return self._line_nbr

    @property
    def col_nbr(self) -> int:
        """The column number where the token was found."""
        return self._col_nbr

    def __repr__(self):
        return "%5d:%3d  %-12s %-12s" % (
            self._line_nbr,
            self._col_nbr,
            self._name,
            self._lexeme,
        )


class Alex:
    """
        Alex is a lexical analyzer that scans input text and produces a sequence
        of `Token` objects.

        The scanner attempts to match the input in the following order:

            1. newline string
            2. characters to skip
            3. operator words
            4. regular expression words (checked against keywords)
            5. keywords

        When a match is found, a `Token` is created and the input pointer is
        advanced by the length of the matched lexeme.

        If no match is found, an exception is raised unless
        `skip_unrecognized_chars` is set to True. In that case, the character is
        ignored and printed to stdout.

        Definitions for keywords, regular expression words, and operators are
        provided when creating the `Alex` instance or via its properties.

        Example:
            ```python
            alex = Alex(keywords=KEYWORDS, regexps=REGEXPS, operators=OPERATORS)
            alex.scan_file(path)
            for token in alex.tokens:
                print(token)
            ```
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
        scan_python_indents=False
    ):
        """
        Initialize the Alex lexer.

        Args:
            skip_chars:
                A string containing characters that should be skipped during
                scanning (typically whitespace).

            newline:
                A string representing a line break in the input. Used for
                line counting. Set to None to disable line counting.

            keywords:
                A list or tuple of keyword strings. All keywords produce
                tokens with the name "KEYWORD".

            regexps:
                A list or tuple of `(token_name, regexp)` pairs. Each regexp
                must begin with `^`. If a regexp matches and the matched
                lexeme is also a keyword, it is treated as a keyword.

            operators:
                A list or tuple of `(token_name, lexeme)` pairs. All token
                names must be unique.

            skip_unrecognized_chars:
                If True, unrecognized characters are ignored instead of
                raising an exception.

            treat_unrecognized_chars_as_an_operator:
                If True, unrecognized characters are returned as tokens.

            scan_python_indents:
                If True, indentation tokens are generated similar to Python's
                indentation rules.
        """

        self.used_token_keys = {'KEYWORD', 'INDENT'}
        self.used_token_lexemes = set()
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
        self._scan_python_indents = scan_python_indents

    @property
    def nbr_of_bytes(self) -> int:
        return self._nbr_of_bytes

    @property
    def nbr_of_lines(self) -> int:
        return self._nbr_of_lines

    @property
    def nbr_of_skipped_chars(self) -> int:
        return self._nbr_of_skipped_chars

    @property
    def tokens(self) -> list[Token]:
        return self._tokens

    def scan_file(self, path: str) -> None:
        """
        This function returns a list of Token objects representing the
        tokens found in the text of the input file.
        """
        text = self._read_file(path)
        self.scan(text)

    def generate_file(self, path: str):
        """
        This function returns a list of Token objects representing the
        tokens found in the text of the input file.
        """
        text = self._read_file(path)
        for token in self.generate(text):
            yield token

    def scan(self, text: str) -> None:
        """
        This function returns a list of Token objects representing the
        tokens found in the given input text.
        """
        self._init_scan(text)
        while text:
            text = self._eat(text)

    def generate(self, text: str):
        """
        This function returns a list of Token objects representing the
        tokens found in the given input text.
        """
        self._init_scan(text)
        size = 0
        while text:
            text = self._eat(text)
            current_size = len(self._tokens)
            if current_size > size:
                size = current_size
                yield self._tokens[-1]

    #
    # Private methods
    #

    def _read_file(self, path):
        with codecs.open(path, encoding="utf-8") as f:
            text = f.read()
        return text

    def _init_scan(self, text):
        self._tokens = []
        self._line_nbr = 1
        self._col_nbr = 1
        self._nbr_of_bytes = len(text)
        self._nbr_of_lines = len(text.split(self._newline))

    def _eat(self, text):
        if self._is_newline(text):
            return self._eat_newline(text)
        if self._scan_python_indents:
            if self._is_indent(text):
                return self._eat_indent(text)
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

    def _is_indent(self, text):
        return self._col_nbr == 1 and text and text[0] == ' '

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
                if lexeme.endswith("\r"):
                    lexeme = lexeme[:-1]
                if lexeme in self._keywords:
                    self._add_token("KEYWORD", lexeme)
                else:
                    self._add_token(name, lexeme)
                return True

    def _eat_newline(self, text):
        self._col_nbr = 1
        self._nbr_of_skipped_chars += len(self._newline)
        return self._eat_text(text, len(self._newline))

    def _eat_indent(self, text):
        count = 0
        try:
            while text and text[count] == ' ':
                count += 1
        except IndexError:
            pass
        self._add_token('INDENT', str(count))
        return self._eat_text(text, count)

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
        return self._compile_regexps(regexps)

    @staticmethod
    def _compile_regexps(regexps):
        return [(name, re.compile(reg, re.DOTALL)) for name, reg in regexps]

    def _set_operators(self, operators):
        """
        operators is a tuple of tuple items. A tuple item has two values,
        a token name and a lexeme description.
        Example:
        (
            ('DOT', '.'),
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
        invalid_regexps = [t for t in regexps if t[1][0] != "^"]
        if invalid_regexps:
            print("A regexp must start with the ^ characters.")
            print("The following items are not following that rule!")
            for regexp in invalid_regexps:
                print("%-6s '%s'" % regexp)
                raise AlexDefinitionError("Invalid regexps!")
        for key, value in regexps:
            if key in self.used_token_keys:
                msg = f"{self._re_msg_prefix(key, value)} Key '{key}' already in use!"
                raise AlexDefinitionError(msg)
            self.used_token_keys.add(key)

    def _validate_operators(self, operators):
        for name, lexeme in operators:
            if name in self.used_token_keys:
                msg = (
                    f"{self._op_msg_prefix(name, lexeme)} Key '{name}' already in use!"
                )
                raise AlexDefinitionError(msg)
            if lexeme is None or len(lexeme) == 0:
                msg = f"{self._op_msg_prefix(name, lexeme)} No value given!"
                raise AlexDefinitionError(msg)
            if lexeme in self.used_token_lexemes:
                msg = f"{self._op_msg_prefix(name, lexeme)} Value '{lexeme}' already in use!"
                raise AlexDefinitionError(msg)
            self.used_token_lexemes.add(lexeme)
            self.used_token_keys.add(name)

    def _op_msg_prefix(self, name, value):
        return self._msg_prefix("Operator", name, value)

    def _re_msg_prefix(self, name, value):
        return self._msg_prefix("Regexp", name, value)

    def _msg_prefix(self, obj, name, value):
        return f"{obj} ({name}, '{value}'):"
