"""Tests for the RAG prompt builder."""

from app.services.prompting import ContextEntry, PromptBuilder


def _entries() -> list[ContextEntry]:
    return [
        ContextEntry(
            index=1,
            content="The Eiffel Tower is in Paris.",
            source="guide.txt (page 2)",
        ),
        ContextEntry(
            index=2,
            content="London has the Thames.",
            source="cities.txt",
        ),
    ]


def test_messages_separate_system_context_and_question():
    messages = PromptBuilder().build_messages(
        query="Where is the Eiffel Tower?",
        entries=_entries(),
    )

    assert [m["role"] for m in messages] == ["system", "user"]
    assert "Do not invent facts" in messages[0]["content"]


def test_user_message_contains_numbered_context_sources():
    messages = PromptBuilder().build_messages(
        query="Where is the Eiffel Tower?",
        entries=_entries(),
    )
    user = messages[1]["content"]

    assert "Context:" in user
    assert "[1] (source: guide.txt (page 2))" in user
    assert "The Eiffel Tower is in Paris." in user
    assert "[2] (source: cities.txt)" in user
    assert "Question: Where is the Eiffel Tower?" in user


def test_prompt_encourages_unavailability_answer_and_citations():
    instructions = PromptBuilder()._system_instructions
    assert "not present in the context" in instructions
    assert "information is unavailable" in instructions
    assert "[n]" in instructions


def test_build_messages_with_empty_entries():
    messages = PromptBuilder().build_messages(query="anything", entries=[])
    assert messages[1]["content"] == (
        "Context:\n\n\n\nQuestion: anything"
    )