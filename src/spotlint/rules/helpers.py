import ast


AGENT_CALLS = {
    "agent.run",
    "agent.invoke",
    "agent.arun",
    "agent.ainvoke",
    "executor.run",
    "executor.invoke",
    "workflow.run",
    "workflow.invoke",
    "chain.run",
    "chain.invoke",
}

TOOL_HINTS = {
    "call_tool",
    "invoke_tool",
    "execute_tool",
    "run_tool",
}

NETWORK_CALLS = {
    "requests.get",
    "requests.post",
    "requests.put",
    "requests.patch",
    "requests.delete",
    "requests.request",
    "httpx.get",
    "httpx.post",
    "httpx.put",
    "httpx.patch",
    "httpx.delete",
    "httpx.request",
    "urllib.request.urlopen",
}


def call_name(node: ast.Call) -> str:
    fn = node.func

    if isinstance(fn, ast.Name):
        return fn.id

    if isinstance(fn, ast.Attribute):
        parts = []
        current = fn

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)

        return ".".join(reversed(parts))

    return ""


def is_agent_call(node: ast.Call) -> bool:
    return call_name(node).lower() in {
        name.lower()
        for name in AGENT_CALLS
    }


def is_tool_call(node: ast.Call) -> bool:
    name = call_name(node).lower()

    return any(
        hint in name
        for hint in TOOL_HINTS
    )


def is_agent_or_tool_call(node: ast.Call) -> bool:
    return (
        is_agent_call(node)
        or is_tool_call(node)
    )


def is_network_call(node: ast.Call) -> bool:
    return call_name(node).lower() in {
        name.lower()
        for name in NETWORK_CALLS
    }


def has_keyword(node: ast.Call, keyword: str) -> bool:
    return any(
        arg.arg == keyword
        for arg in node.keywords
    )


def build_parent_map(tree: ast.AST) -> dict[int, ast.AST]:
    parents = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent

    return parents


def enclosing_nodes(
    tree: ast.AST,
    node: ast.AST,
    node_type
):
    parents = build_parent_map(tree)

    current = parents.get(id(node))

    while current is not None:

        if isinstance(current, node_type):
            yield current

        current = parents.get(id(current))


def inside_try_except(
    tree: ast.AST,
    node: ast.AST
) -> bool:

    return any(
        block.handlers
        for block in enclosing_nodes(
            tree,
            node,
            ast.Try
        )
    )