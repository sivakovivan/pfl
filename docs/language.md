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

The interpreter's core loop is:

```text
kind -> posit -> derive -> case -> ask -> result -> explanation -> report
```

## Non-goals

PFL v0.1 does not include imports, packages, natural-language parsing,
defeasible reasoning, modal or deontic logic, external solver backends, or a
web editor. Inference is deterministic and symbolic; it does not use an LLM as
a reasoning engine.
