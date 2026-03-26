import alex


def test_alex():
    """
    >>> alex = alex.Alex()

    >>> alex._msg_prefix('obj', 'y', 'z')
    "obj (y, 'z'):"

    >>> alex._re_msg_prefix('y', 'z')
    "Regexp (y, 'z'):"

    >>> alex._op_msg_prefix('y', 'z')
    "Operator (y, 'z'):"
    """
