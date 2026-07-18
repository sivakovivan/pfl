# PFL v0.1 language notes

PFL is a deterministic language for describing a philosophical theory,
applying it to a case, and asking what follows.

The v0.1 language is centered on these constructs:

- `theory` names a philosophical system.
- `kind` declares a category used by the system.
- `posit` declares a foundational term and may provide a `reads` template.
- `derive` declares a sufficient rule for a derived term.
- `case Name under Theory` supplies a thought experiment.
- `let` declares a concrete case value.
- `ask` queries whether a known term follows.
- `some X: Kind where:` introduces a rule-local existential variable.

The interpreter's core loop is:

```text
kind -> posit -> derive -> case -> ask -> result -> explanation -> report
```

## Canonical and readable statements

Predicate calls use canonical positional form:

```pfl
chooses(alice, optionA)
```

A posit may define a `reads` template for a more readable surface syntax:

```pfl
posit chooses(actor: Subject, option: Option)
    reads "{actor} chooses {option}"
```

The readable statement is then equivalent to the call:

```pfl
alice chooses optionA
```

Every placeholder must correspond to exactly one declared posit argument.
Literal tokens match exactly. If multiple templates match one statement, PFL
reports `PFL006`.

## Derivation and existential variables

Each `derive` block is a sufficient forward-chaining rule. A simple existential witness can be introduced with `some`:

```pfl
derive avoidable_setback(P: Subject, Actor: Subject, A: Option):
    Actor chooses A
    some B: Option where:
        B is available to Actor
        option_worse_for(P, A, B)
```

## Ask results

PFL v0.1 returns:

- `true` when the requested predicate is a case fact or is derived;
- `unknown` when the term is valid but no fact or rule derives that instance.

Unknown term names are semantic errors, not `unknown` query results.
