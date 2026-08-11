# PFL v0.1 language guide

PFL is a small, deterministic language for making a philosophical theory
explicit, applying it to a case, and asking what the theory implies.

It does not establish that a theory is true. It records the theory's stated
commitments and shows which conclusions follow from them.

```text
theory → kinds → posits → rules → case → question → result → explanation
```

## The building blocks

| Construct | Meaning |
| --- | --- |
| `theory` | A named philosophical system or fragment of one |
| `kind` | A category of thing used by the theory, such as `Person` or `Action` |
| `posit` | A primitive relation the theory takes as given |
| `derive` | A sufficient rule for a conclusion |
| `case ... under ...` | A concrete or hypothetical situation evaluated under a theory |
| `let` | A particular thing in a case and its kind |
| `ask` | A question about whether a relation follows in the case |
| `some ... where:` | An existential witness used inside a rule |

## A complete small example

This is a deliberately limited preference-utilitarian fragment. It says that,
for one person, an available action is morally preferred when it gives that
person an outcome they prefer to the outcome of an available alternative.

```pfl
theory MinimalPreferenceUtilitarianism {
    kind Person
    kind Action
    kind Outcome

    posit available_to(action: Action, person: Person)
        reads "{action} is available to {person}"

    posit produces(action: Action, outcome: Outcome)
        reads "{action} produces {outcome}"

    posit prefers(person: Person, better: Outcome, worse: Outcome)
        reads "{person} prefers {better} to {worse}"

    derive better_for(person: Person, better_action: Action, worse_action: Action):
        some better_outcome: Outcome where:
            better_action produces better_outcome
            some worse_outcome: Outcome where:
                worse_action produces worse_outcome
                person prefers better_outcome to worse_outcome

    derive morally_preferred(person: Person, action: Action):
        action is available to person
        some alternative: Action where:
            alternative is available to person
            better_for(person, action, alternative)
}

case MedicineChoice under MinimalPreferenceUtilitarianism {
    let alice: Person
    let take_medicine: Action
    let leave_medicine: Action
    let alice_recovers: Outcome
    let alice_remains_ill: Outcome

    take_medicine is available to alice
    leave_medicine is available to alice
    take_medicine produces alice_recovers
    leave_medicine produces alice_remains_ill
    alice prefers alice_recovers to alice_remains_ill

    ask morally_preferred(alice, take_medicine)
}
```

The answer is `true`. PFL can explain the result by tracing it through
`morally_preferred`, `better_for`, the facts about the two actions, and Alice's
stated preference.

## Writing a theory

A theory contains kinds, primitive relations, and rules:

```pfl
theory Example {
    kind Person

    posit reflects(person: Person)
        reads "{person} reflects"

    derive thoughtful(person: Person):
        person reflects
}
```

`posit` declarations introduce the foundational vocabulary. PFL does not try to
prove a posit: it makes the commitment visible. `derive` declarations state
sufficient conditions; they do not automatically state necessary conditions.

## Canonical and readable statements

Every posit has a canonical predicate-call form:

```pfl
reflects(alice)
```

A `reads` template can add a human-friendly alternative:

```pfl
posit reflects(person: Person)
    reads "{person} reflects"
```

That makes the following equivalent:

```pfl
reflects(alice)
alice reflects
```

Templates are controlled syntax, not natural-language understanding. Each
placeholder must match exactly one declared posit argument; literal words must
match exactly. If more than one template could read a statement, PFL reports
`PFL006`.

## Rules and existential witnesses

Rules use forward chaining: if every line in a rule body is known, PFL derives
the rule's conclusion. Variables in a rule must be declared either in its
header or in a `some` block.

```pfl
derive has_better_alternative(person: Person, action: Action):
    some alternative: Action where:
        alternative is available to person
        better_for(person, alternative, action)
```

`some alternative: Action where:` means “there is an action called
`alternative` of kind `Action` for which the indented statements hold.”

## Cases and questions

A case selects a theory, declares its particular objects with `let`, gives
facts, and asks questions:

```pfl
case ReflectionCase under Example {
    let alice: Person

    alice reflects
    ask thoughtful(alice)
}
```

## Results

PFL v0.1 returns:

- `true` when the requested predicate is a stated case fact or can be derived;
- `unknown` when the predicate is valid but PFL cannot derive that instance.

`unknown` does not mean false. PFL v0.1 uses an open-world, positive
forward-chaining model: lack of a derivation is only lack of a derivation.
Unknown predicate names are semantic errors, not `unknown` results.

## Current limits

PFL v0.1 supports typed predicates, readable templates, sufficient rules, and
simple existential witnesses. It does not yet support negation, exceptions,
competing arguments, probabilities, or countermodel generation.

Use `pfl check`, `pfl run`, `pfl explain`, `pfl report`, and `pfl desugar` to
validate, evaluate, explain, inspect, and expand a PFL file.
