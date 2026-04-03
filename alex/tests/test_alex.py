import re
import pytest
import alex


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
    assert 'ID' in lexer.used_token_keys


def test_regexp_missing_initial_char():
    lexer = alex.Alex()
    regexps = (("ID", f"[a-zA-Z_0-9]*"),)
    with pytest.raises(alex.AlexDefinitionError, match=r"^A regexp must start with the \^ character\.$"):
        lexer._validate_regexps(regexps)


def test_key_already_in_use():
    lexer = alex.Alex()
    operators = [('ID', '+'), ('SUB', '-')]
    lexer._validate_operators(operators)
    regexps = (("ID", f"^[a-zA-Z_0-9]*"),)

    with pytest.raises(
            alex.AlexDefinitionError,
            match=re.escape("Regexp (ID, '^[a-zA-Z_0-9]*'): Key 'ID' already in use!")
    ):
        lexer._validate_regexps(regexps)
