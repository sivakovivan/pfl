from pathlib import Path

from pfl.cli import main


EXAMPLES = Path(__file__).parents[1] / "examples"


def test_example_theory_returns_favourable_outcome(
    capsys,
) -> None:
    exit_code = main(["run", str(EXAMPLES / "example_theory.pfl")])

    output = capsys.readouterr()
    assert exit_code == 0
    assert "Case: SpecificChoiceCase" in output.out
    assert "ask favourable_outcome(alice, optionA)" in output.out
    assert "Result: true" in output.out


def test_medicine_case_returns_morally_disfavored(
    capsys,
) -> None:
    exit_code = main(["run", str(EXAMPLES / "medicine_case.pfl")])

    output = capsys.readouterr()
    assert exit_code == 0
    assert "Case: MedicineCase" in output.out
    assert "ask morally_disfavored(take_medicine)" in output.out
    assert "Result: true" in output.out
