from pathlib import Path

from pfl.cli import main


def test_check_command_validates_file(
    tmp_path: Path,
    capsys,
) -> None:
    source = tmp_path / "example.pfl"
    source.write_text(
        """
        theory ExampleTheory {
            kind Subject
        }
        case ExampleCase under ExampleTheory {
            let alice: Subject
        }
        """,
        encoding="utf-8",
    )

    exit_code = main(["check", str(source)])

    output = capsys.readouterr()
    assert exit_code == 0
    assert f"OK: {source}" in output.out
    assert "- ExampleTheory" in output.out
    assert "- ExampleCase" in output.out
    assert output.err == ""


def test_check_command_prints_diagnostic(
    tmp_path: Path,
    capsys,
) -> None:
    source = tmp_path / "invalid.pfl"
    source.write_text(
        "case ExampleCase under MissingTheory {}",
        encoding="utf-8",
    )

    exit_code = main(["check", str(source)])

    output = capsys.readouterr()
    assert exit_code == 1
    assert "PFL004" in output.err


def test_run_command_evaluates_true_and_unknown_asks(
    tmp_path: Path,
    capsys,
) -> None:
    source = tmp_path / "choice.pfl"
    source.write_text(
        """
        theory ExampleTheory {
            kind Subject
            kind Option
            posit prefers(actor: Subject, option: Option)
            posit chooses(actor: Subject, option: Option)
            derive favourable_outcome(actor: Subject, option: Option):
                prefers(actor, option)
                chooses(actor, option)
        }
        case SpecificChoiceCase under ExampleTheory {
            let alice: Subject
            let optionA: Option
            let optionB: Option
            prefers(alice, optionA)
            chooses(alice, optionA)
            ask favourable_outcome(alice, optionA)
            ask favourable_outcome(alice, optionB)
        }
        """,
        encoding="utf-8",
    )

    exit_code = main(["run", str(source)])

    output = capsys.readouterr()
    assert exit_code == 0
    assert "Case: SpecificChoiceCase" in output.out
    assert "ask favourable_outcome(alice, optionA)\nResult: true" in output.out
    assert "ask favourable_outcome(alice, optionB)\nResult: unknown" in output.out


def test_explain_command_shows_derivation(
    tmp_path: Path,
    capsys,
) -> None:
    source = tmp_path / "action.pfl"
    source.write_text(
        """
        theory ActionTheory {
            kind Subject
            posit acts(actor: Subject)
            derive acknowledged(actor: Subject):
                acts(actor)
        }
        case ActionCase under ActionTheory {
            let alice: Subject
            acts(alice)
            ask acknowledged(alice)
        }
        """,
        encoding="utf-8",
    )

    exit_code = main(["explain", str(source)])

    output = capsys.readouterr()
    assert exit_code == 0
    assert "Result: true" in output.out
    assert "derived by acknowledged" in output.out
    assert "acts(alice)\n      given in case" in output.out


def test_report_command_prints_theory_structure(
    tmp_path: Path,
    capsys,
) -> None:
    source = tmp_path / "report.pfl"
    source.write_text(
        """
        theory ExampleTheory {
            kind Subject
            posit acts(actor: Subject)
            derive acknowledged(actor: Subject):
                acts(actor)
        }
        """,
        encoding="utf-8",
    )

    exit_code = main(["report", str(source)])

    output = capsys.readouterr()
    assert exit_code == 0
    assert "Theory: ExampleTheory" in output.out
    assert "- acts(actor: Subject)" in output.out
    assert "- acknowledged(actor: Subject)" in output.out
    assert "- acknowledged\n  depends on:\n  - acts" in output.out
    assert "Semantic debt:\n- none" in output.out


def test_desugar_command_prints_canonical_rules_and_facts(
    tmp_path: Path,
    capsys,
) -> None:
    source = tmp_path / "readable.pfl"
    source.write_text(
        """
        theory ActionTheory {
            kind Subject
            posit acts(actor: Subject)
                reads "{actor} acts"
            derive acknowledged(actor: Subject):
                actor acts
        }
        case ActionCase under ActionTheory {
            let alice: Subject
            alice acts
            ask acknowledged(alice)
        }
        """,
        encoding="utf-8",
    )

    exit_code = main(["desugar", str(source)])

    output = capsys.readouterr()
    assert exit_code == 0
    assert "- acknowledged(actor) :- acts(actor)" in output.out
    assert "Facts:\n- acts(alice)" in output.out
    assert "Asks:\n- acknowledged(alice)" in output.out
