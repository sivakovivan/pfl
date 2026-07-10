# PFL

PFL (Philosophy Formalization Language) is a small, deterministic language for
expressing philosophical theories, applying cases to them, and explaining what
follows. Its v0.1 interpreter is written in Python and does not use an LLM as a
reasoning engine.

The core workflow is:

```text
kind -> posit -> derive -> case -> ask -> result -> explanation -> report
```

## Requirements and installation

PFL requires Python 3.13 or newer. Create a virtual environment and install the
project in editable mode:

```bash
python -m venv .venv
python -m pip install --editable .
python -m pip install pytest
```

With `uv`, the equivalent development setup is:

```bash
uv sync
```

Both approaches install the `pfl` command.

## Quick start

Run the simple choice example:

```bash
pfl check examples/example_theory.pfl
pfl run examples/example_theory.pfl
pfl explain examples/example_theory.pfl
```

The result includes:

```text
ask favourable_outcome(alice, optionA)
Result: true
```

Run the larger existential reasoning example:

```bash
pfl run examples/medicine_case.pfl
```

This evaluates `MedicineCase` under `MinimalPreferenceEthics` and derives
`morally_disfavored(take_medicine)`.

## Commands

```text
pfl check <file>     Parse and semantically validate a PFL file.
pfl run <file>       Run every case and print true/unknown ask results.
pfl explain <file>   Run cases and recursively explain their results.
pfl report <file>    Show kinds, terms, dependencies, and semantic debt.
pfl desugar <file>   Show readable statements as canonical predicates/rules.
```

## Language overview

A theory declares formal categories with `kind`, foundational commitments with
`posit`, and sufficient rules with `derive`. A case selects a theory with
`under`, introduces concrete instances with `let`, supplies facts, and makes
queries with `ask`.

```pfl
theory ExampleTheory {
    kind Subject
    kind Option

    posit chooses(actor: Subject, option: Option)
        reads "{actor} chooses {option}"

    derive selected(actor: Subject, option: Option):
        actor chooses option
}

case ExampleCase under ExampleTheory {
    let alice: Subject
    let optionA: Option

    alice chooses optionA
    ask selected(alice, optionA)
}
```

`reads` templates provide deterministic surface syntax; they are token
templates, not natural-language parsing. Simple `some X: Kind where:` blocks
introduce existential variables in derive bodies.

See [the language notes](docs/language.md) and the files in
[examples](examples/) for the supported v0.1 syntax.

## Development

Run the full test suite from the repository root:

```bash
pytest
```

The implementation uses a `src/` package layout. Major components are kept in
focused modules for parsing, semantic checks, desugaring, compilation,
inference, explanations, and reports.

## v0.1 limitations

PFL v0.1 intentionally supports only deterministic forward chaining with
`true` and `unknown` query results. It does not include:

- explicit negation or `false`/`conflict` results;
- imports, packages, or theory inheritance;
- `or`, `forall`, defeasible, modal, or deontic reasoning;
- unrestricted recursion or function symbols;
- general natural-language parsing;
- external solver or LLM reasoning backends;
- a web editor.

These are later-version concerns. v0.1 focuses on a transparent,
human-maintainable `posit -> derive -> case -> ask` loop.
