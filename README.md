# PFL

PFL (Philosophy Formalization Language) is a meta-language for explicitly, deterministically and fundamentally expressing philosophical theories with associated primitives, and testing them against specific cases.

The deterministic philosophy flows as follows:

```text
kind -> posit -> derive -> case -> ask -> result -> explanation -> report
```

## Installation

```bash
git clone https://github.com/sivakovivan/pfl.git
cd pfl
uv sync
```

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
pfl -h               Show this help message.
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

Run the unit tests from the repository root:

```bash
uv run pytest
```