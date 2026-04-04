from alex import Token
from alex.tools import (
    create_python_function_tree,
    FuncNode,
    nodes,
)


def make_node(name, children=None):
    node = FuncNode.__new__(FuncNode)
    node.name = name
    node.tokens = []
    node.funcs = children or []
    return node


def test_nodes_yields_nested_function_nodes_depth_first():
    grandchild = make_node("grandchild")
    child = make_node("child", [grandchild])
    root_nodes = [child]
    result = list(nodes(root_nodes))
    assert root_nodes[0].funcs[0].name == "grandchild"


def test_create_python_function_tree_returns_nested_functions():
    tokens = iter(
        [
            Token("KEYWORD", "def", 1, 1),
            Token("ID", "outer", 1, 5),
            Token("LP", "(", 1, 10),
            Token("RP", ")", 1, 11),
            Token("COLON", ":", 1, 12),
            Token("KEYWORD", "def", 2, 5),
            Token("ID", "inner", 2, 9),
            Token("LP", "(", 2, 14),
            Token("RP", ")", 2, 15),
            Token("COLON", ":", 2, 16),
        ]
    )
    result = list(create_python_function_tree(tokens))
    assert result[0].name == 'outer'
    assert result[0].funcs[0].name == 'inner'
