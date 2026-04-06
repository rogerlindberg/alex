import os
import re
import pytest
import alex


@pytest.fixture
def make_alex():
    def _make_alex(operators=None, regexps=None):
        regs = regexps or (
            (
                ("NUM", '^["0123456789"]*'),
                ("ID", f"^[a-zA-Z_0-9]*"),
            )
        )
        ops = operators or ((("ADD", "+"), ("SUB", "-")))
        return alex.Alex(operators=ops, regexps=regs)
    return _make_alex


def merge_lexemes(lexer):
    return ''.join([t.lexeme for t in lexer.tokens])


def merge_gen_lexemes(gen):
    return ''.join([t.lexeme for t in gen])


def create_test_file(text):
    filename = 'tmp.txt'
    with open(filename, "w") as f:
        f.write(text)
        return filename


def remove_test_file(filename):
    os.remove(filename)


def test_scan(make_alex):
    # Given
    lexer = make_alex()
    # When
    lexer.scan("17 + 5 - 12")
    # Then
    assert merge_lexemes(lexer) == "17+5-12"


def test_scan_file(make_alex):
    # Given
    lexer = make_alex()
    filename = create_test_file('17 + 5 - 12')
    # When
    lexer.scan_file(filename)
    # Then
    assert merge_lexemes(lexer) == "17+5-12"
    # Clean Up
    remove_test_file(filename)


def test_generate(make_alex):
    # Given
    lexer = make_alex()
    # When
    gen = lexer.generate("17 + 5 - 12")
    # Then
    assert merge_gen_lexemes(gen) == "17+5-12"


def test_generate_file(make_alex):
    # Given
    lexer = make_alex()
    filename = create_test_file('17 + 5 - 12')
    # When
    gen = lexer.generate_file(filename)
    # Then
    assert merge_gen_lexemes(gen) == "17+5-12"
    # Clean Up
    remove_test_file(filename)


def test_validate_operators_accepts_unique_names_and_lexemes():
    # Given
    lexer = alex.Alex()
    # When
    lexer._validate_operators([("ADD", "+"), ("SUB", "-")])
    # Then
    assert "+" in lexer.used_token_lexemes
    assert "-" in lexer.used_token_lexemes
    assert "ADD" in lexer.used_token_keys
    assert "SUB" in lexer.used_token_keys


def test_msg_prefix_helpers():
    # Given
    lexer = alex.Alex()
    # Then
    assert lexer._msg_prefix("obj", "y", "z") == "obj (y, 'z'):"
    assert lexer._re_msg_prefix("y", "z") == "Regexp (y, 'z'):"
    assert lexer._op_msg_prefix("y", "z") == "Operator (y, 'z'):"


def test_validate_operators_rejects_duplicate_name():
    # Given
    lexer = alex.Alex()
    # Then
    with pytest.raises(alex.AlexDefinitionError, match=r"Key 'ADD' already in use"):
        # When
        lexer._validate_operators([("ADD", "+"), ("ADD", "-")])


def test_validate_operators_rejects_duplicate_lexeme():
    # Given
    lexer = alex.Alex()
    # Then
    with pytest.raises(alex.AlexDefinitionError, match=r"Value '\+' already in use"):
        # When
        lexer._validate_operators([("ADD", "+"), ("SUB", "+")])


def test_validate_operators_rejects_empty_lexeme():
    # Given
    lexer = alex.Alex()
    # Then
    with pytest.raises(alex.AlexDefinitionError, match=r"No value given"):
        # When
        lexer._validate_operators([("ADD", "+"), ("SUB", "")])


def test_validate_operators_rejects_none_lexeme():
    # Given
    lexer = alex.Alex()
    # Then
    with pytest.raises(alex.AlexDefinitionError, match=r"No value given"):
        # When
        lexer._validate_operators([("ADD", "+"), ("SUB", None)])


def test_scan_python_indents_handles_whitespace_only_input():
    # Given
    lexer = alex.Alex(scan_python_indents=True)
    # When
    lexer.scan("   ")
    # Then
    assert [(t.name, t.lexeme, t.line_nbr, t.col_nbr) for t in lexer.tokens] == [
        ("INDENT", "3", 1, 1),
    ]


def test_scan_python_indents_handles_whitespace_only_line_after_newline():
    # Given
    lexer = alex.Alex(scan_python_indents=True)
    # When
    lexer.scan("\n   ")
    # Then
    assert [(t.name, t.lexeme, t.line_nbr, t.col_nbr) for t in lexer.tokens] == [
        ("INDENT", "3", 2, 1),
    ]


def test_valid_regexp():
    # Given
    lexer = alex.Alex()
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)
    # When
    lexer._validate_regexps(regexps)
    # Then
    assert "ID" in lexer.used_token_keys


def test_regexp_missing_initial_char():
    # Given
    lexer = alex.Alex()
    regexps = (("ID", f"[a-zA-Z_0-9]*"),)
    # Then
    with pytest.raises(
        alex.AlexDefinitionError, match=r"^A regexp must start with the \^ character\.$"
    ):
        # When
        lexer._validate_regexps(regexps)


def test_key_already_in_use():
    # Given
    lexer = alex.Alex()
    operators = [("ID", "+"), ("SUB", "-")]
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)

    # When
    lexer._validate_operators(operators)

    # Then
    with pytest.raises(
        alex.AlexDefinitionError,
        match=re.escape("Regexp (ID, '^[a-zA-Z_0-9]*'): Key 'ID' already in use!"),
    ):
        # When
        lexer._validate_regexps(regexps)


def test_attributes(make_alex):
    # Given
    lexer = make_alex()
    lexer._skip_unrecognized_chars = True
    # When
    lexer.scan("17 + 5 =\n - 12")
    # Then
    assert lexer.nbr_of_bytes == 14
    assert lexer.nbr_of_lines == 2
    assert lexer.nbr_of_skipped_chars == 7


def test_keyword():
    # Given
    operators = (("EQ", "="), ("ADD", "+"))
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)
    keywords = ("foo", "bar")
    lexer = alex.Alex(
        operators=operators,
        regexps=regexps,
        keywords=keywords,
        skip_unrecognized_chars=True,
    )
    # When
    lexer.scan("x = foo + bar")
    # Then
    keywords = {token.lexeme for token in lexer.tokens if token.name == "KEYWORD"}
    assert keywords == {"foo", "bar"}


def test_treat_unrecognized_chars_as_oprators(make_alex):
    # Given
    lexer = make_alex()
    lexer._treat_unrecognized_chars_as_an_operator = True
    # When
    lexer.scan("x=")
    # Then
    lexemes = {token.lexeme for token in lexer.tokens}
    names = {token.name for token in lexer.tokens}
    assert lexemes == {"=", "x"}
    assert names == {"ID", "UNRECOGNIZED-CHAR"}


def test_unrecognized_first_char():
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)
    lexer = alex.Alex(regexps=regexps)
    with pytest.raises(
        alex.AlexScanError,
        match=re.escape(
            "Unrecognized char '=' ordinal 61\nFollowing 10 characters are: x\nNo tokens was scanned"
        ),
    ):
        lexer.scan("=x")


def test_unrecognized_chars(make_alex):
    # Given
    lexer = make_alex()
    # Then
    with pytest.raises(
        alex.AlexScanError,
        match=re.escape(
            "Unrecognized char '=' ordinal 61\nFollowing 10 characters are: \nLast scanned Token:     1:  1  ID"
        ),
    ):
        # When
        lexer.scan("x=")


def test_trim():
    # Given
    regexps = (("ID", f"^[a-zA-Z_0-9\r\n]*"),)
    lexer = alex.Alex(regexps=regexps, skip_unrecognized_chars="\t")
    # When
    lexer.scan("foobar\r\n")
    # Then
    assert lexer.tokens[0].lexeme == "foobar"
