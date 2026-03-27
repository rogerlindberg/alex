# Alex API Reference

This page contains the full API documentation for the `alex` module, including:

- `Token` — represents a lexical token
- `AlexScanError` and `AlexDefinitionError` — domain‑specific exceptions
- `Alex` — the main lexer class

All documentation is automatically generated from docstrings using `mkdocstrings`.

---

## Token

Represents a lexical token produced by the lexer.

::: yourpackage.token.Token

---

## Exceptions

### AlexScanError

Raised when the lexer encounters invalid or unrecognized input.

::: yourpackage.alex.AlexScanError

### AlexDefinitionError

Raised when token definitions (keywords, regexps, operators) are invalid.

::: yourpackage.alex.AlexDefinitionError

---

## Alex

The main class responsible for scanning input text and producing tokens.

::: yourpackage.alex.Alex
    handler: python
    options:
      show_source: true
      docstring_style: google
      members_order: source
