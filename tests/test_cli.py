from flowmark.cli import main


def test_bad_example(capsys):
    code = main(["check", "examples/bad_agent.py"])
    output = capsys.readouterr().out
    assert code == 1
    assert "AG001" in output
    assert "AG005" in output


def test_good_example(capsys):
    code = main(["check", "examples/good_agent.py"])
    output = capsys.readouterr().out
    assert code == 0
    assert "no findings" in output


def test_json(capsys):
    code = main(["check", "examples/bad_agent.py", "--format", "json"])
    output = capsys.readouterr().out
    assert code == 1
    assert '"findings"' in output
