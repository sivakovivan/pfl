from pfl.ast_nodes import (
    ArgDecl,
    AskDecl,
    CaseDecl,
    Document,
    KindDecl,
    PositDecl,
    PredicateCall,
    TheoryDecl,
)


def test_builds_core_document_nodes() -> None:
    subject = KindDecl("Subject")
    prefers = PositDecl(
        "prefers",
        (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
        "{actor} prefers {option}",
    )
    theory = TheoryDecl("ExampleTheory", (subject,), (prefers,))
    query = PredicateCall("prefers", ("alice", "optionA"))
    case = CaseDecl(
        "SpecificChoiceCase",
        "ExampleTheory",
        asks=(AskDecl(query),),
    )

    document = Document((theory,), (case,))

    assert document.theories[0].posits[0].args[1].kind == "Option"
    assert document.cases[0].asks[0].expression == query


def test_document_defaults_to_no_declarations() -> None:
    assert Document() == Document(theories=(), cases=())
