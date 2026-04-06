import os
import re
import pytest
import alex


def test_scan():
    operators = (("ADD", "+"), ("SUB", "-"))
    regexps = (("NUM", '^["0123456789"]*'),)
    lexer = alex.Alex(operators=operators, regexps=regexps)
    lexer.scan("17 + 5 - 12")
    lexemes = [t.lexeme for t in lexer.tokens]
    assert "".join(lexemes) == "17+5-12"


def test_scan_file():
    operators = (("ADD", "+"), ("SUB", "-"))
    regexps = (("NUM", '^["0123456789"]*'),)
    lexer = alex.Alex(operators=operators, regexps=regexps)
    with open("tmp.txt", "w") as f:
        f.write("17 + 5 - 12")
    lexer.scan_file("tmp.txt")
    lexemes = [t.lexeme for t in lexer.tokens]
    assert "".join(lexemes) == "17+5-12"
    os.remove("tmp.txt")


def test_generate():
    operators = (("ADD", "+"), ("SUB", "-"))
    regexps = (("NUM", '^["0123456789"]*'),)
    lexer = alex.Alex(operators=operators, regexps=regexps)
    gen = lexer.generate("17 + 5 - 12")
    lexemes = [t.lexeme for t in gen]
    assert "".join(lexemes) == "17+5-12"


def test_generate_file():
    operators = (("ADD", "+"), ("SUB", "-"))
    regexps = (("NUM", '^["0123456789"]*'),)
    lexer = alex.Alex(operators=operators, regexps=regexps)
    with open("tmp.txt", "w") as f:
        f.write("17 + 5 - 12")
    gen = lexer.generate_file("tmp.txt")
    lexemes = [t.lexeme for t in gen]
    assert "".join(lexemes) == "17+5-12"
    os.remove("tmp.txt")


def test_validate_operators_accepts_unique_names_and_lexemes():
    lexer = alex.Alex()
    lexer._validate_operators([("ADD", "+"), ("SUB", "-")])
    assert "+" in lexer.used_token_lexemes
    assert "-" in lexer.used_token_lexemes
    assert "ADD" in lexer.used_token_keys
    assert "SUB" in lexer.used_token_keys


def test_msg_prefix_helpers():
    lexer = alex.Alex()
    assert lexer._msg_prefix("obj", "y", "z") == "obj (y, 'z'):"
    assert lexer._re_msg_prefix("y", "z") == "Regexp (y, 'z'):"
    assert lexer._op_msg_prefix("y", "z") == "Operator (y, 'z'):"


def test_validate_operators_rejects_duplicate_name():
    lexer = alex.Alex()
    with pytest.raises(alex.AlexDefinitionError, match=r"Key 'ADD' already in use"):
        lexer._validate_operators([("ADD", "+"), ("ADD", "-")])


def test_validate_operators_rejects_duplicate_lexeme():
    lexer = alex.Alex()
    with pytest.raises(alex.AlexDefinitionError, match=r"Value '\+' already in use"):
        lexer._validate_operators([("ADD", "+"), ("SUB", "+")])


def test_validate_operators_rejects_empty_lexeme():
    lexer = alex.Alex()
    with pytest.raises(alex.AlexDefinitionError, match=r"No value given"):
        lexer._validate_operators([("ADD", "+"), ("SUB", "")])


def test_validate_operators_rejects_none_lexeme():
    lexer = alex.Alex()
    with pytest.raises(alex.AlexDefinitionError, match=r"No value given"):
        lexer._validate_operators([("ADD", "+"), ("SUB", None)])


def test_scan_python_indents_handles_whitespace_only_input():
    lexer = alex.Alex(scan_python_indents=True)
    lexer.scan("   ")
    assert [(t.name, t.lexeme, t.line_nbr, t.col_nbr) for t in lexer.tokens] == [
        ("INDENT", "3", 1, 1),
    ]


def test_scan_python_indents_handles_whitespace_only_line_after_newline():
    lexer = alex.Alex(scan_python_indents=True)
    lexer.scan("\n   ")
    assert [(t.name, t.lexeme, t.line_nbr, t.col_nbr) for t in lexer.tokens] == [
        ("INDENT", "3", 2, 1),
    ]


def test_valid_regexp():
    lexer = alex.Alex()
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)
    lexer._validate_regexps(regexps)
    assert "ID" in lexer.used_token_keys


def test_regexp_missing_initial_char():
    lexer = alex.Alex()
    regexps = (("ID", f"[a-zA-Z_0-9]*"),)
    with pytest.raises(
        alex.AlexDefinitionError, match=r"^A regexp must start with the \^ character\.$"
    ):
        lexer._validate_regexps(regexps)


def test_key_already_in_use():
    lexer = alex.Alex()
    operators = [("ID", "+"), ("SUB", "-")]
    lexer._validate_operators(operators)
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)

    with pytest.raises(
        alex.AlexDefinitionError,
        match=re.escape("Regexp (ID, '^[a-zA-Z_0-9]*'): Key 'ID' already in use!"),
    ):
        lexer._validate_regexps(regexps)


def test_attributes():
    operators = (("ADD", "+"), ("SUB", "-"))
    regexps = (("NUM", '^["0123456789"]*'),)
    lexer = alex.Alex(
        operators=operators, regexps=regexps, skip_unrecognized_chars=True
    )
    lexer.scan("17 + 5 =\n - 12")
    assert lexer.nbr_of_bytes == 14
    assert lexer.nbr_of_lines == 2
    assert lexer.nbr_of_skipped_chars == 7


def test_keyword():
    operators = (("EQ", "="), ("ADD", "+"))
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)
    keywords = ("foo", "bar")
    lexer = alex.Alex(
        operators=operators,
        regexps=regexps,
        keywords=keywords,
        skip_unrecognized_chars=True,
    )
    lexer.scan("x = foo + bar")
    keywords = {token.lexeme for token in lexer.tokens if token.name == "KEYWORD"}
    assert keywords == {"foo", "bar"}


def test_treat_unrecognized_chars_as_oprators():
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)
    lexer = alex.Alex(
        regexps=regexps,
        treat_unrecognized_chars_as_an_operator=True,
    )
    lexer.scan("x=")
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


def test_unrecognized_chars():
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)
    lexer = alex.Alex(regexps=regexps)
    with pytest.raises(
        alex.AlexScanError,
        match=re.escape(
            "Unrecognized char '=' ordinal 61\nFollowing 10 characters are: \nLast scanned Token:     1:  1  ID"
        ),
    ):
        lexer.scan("x=")


def test_trim():
    regexps = (("ID", f"^[a-zA-Z_0-9\r\n]*"),)
    lexer = alex.Alex(regexps=regexps, skip_unrecognized_chars="\t")
    lexer.scan("foobar\r\n")
    assert lexer.tokens[0].lexeme == "foobar"
