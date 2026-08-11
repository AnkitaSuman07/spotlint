import ast

from spotlint.model import RuleContext, Severity, SourceFile
from spotlint.rules import DEFAULT_RULES


def findings(source: str):
    context = RuleContext(
        source_file=SourceFile("test.py", source, ast.parse(source))
    )
    output = []
    for rule in DEFAULT_RULES:
        output.extend(rule.check(context))
    return output


def ids(source: str) -> set[str]:
    return {item.rule_id for item in findings(source)}


def test_ag001_unbounded():
    assert "AG001" in ids("""
while True:
    invoke_agent("hello")
""")


def test_ag001_bounded():
    assert "AG001" not in ids("""
while iteration < max_iterations:
    invoke_agent("hello")
""")


def test_ag002_unhandled():
    assert "AG002" in ids("""
result = search_tool("hello")
""")


def test_ag002_handled():
    assert "AG002" not in ids("""
try:
    result = search_tool("hello")
except Exception:
    result = None
""")


def test_ag003_timeout():
    assert "AG003" in ids("""
requests.get("https://example.com")
""")


def test_ag003_timeout_present():
    assert "AG003" not in ids("""
requests.get("https://example.com", timeout=5)
""")


def test_ag004_retry_or_fallback():
    assert "AG004" in ids("""
requests.get("https://example.com", timeout=5)
""")


def test_ag004_try_except():
    assert "AG004" not in ids("""
try:
    requests.get("https://example.com", timeout=5)
except Exception:
    pass
""")


def test_ag005_secret():
    assert "AG005" in ids("""
API_KEY = "super-secret-production-value"
""")


def test_ag005_env():
    assert "AG005" not in ids("""
API_KEY = os.environ["API_KEY"]
""")


def test_severity_order():
    assert Severity.CRITICAL.rank > Severity.HIGH.rank > Severity.MEDIUM.rank > Severity.LOW.rank
