# PFL

PFL (Philosophy Formalization Language) is a small, deterministic language for
expressing philosophical theories and evaluating cases under them.

This repository contains the Python implementation of the PFL v0.1
interpreter.

## Language overview

PFL's core loop is:

```text
kind -> posit -> derive -> case -> ask -> result -> explanation -> report
```

A theory declares the kinds it discusses, its foundational `posit` terms, and
terms produced by `derive` rules. A `case` introduces concrete values with
`let`, supplies facts, and uses `ask` to query what follows under a theory.

See [the language notes](docs/language.md) for the v0.1 syntax and scope.
