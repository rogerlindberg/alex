from alex import Token


def test_token_repr():
    token = Token('ID', '__init__', 5, 11)
    assert token.__repr__() == '    5: 11  ID           __init__    '
