import pytest

from app.services.json_utils import extract_json
from app.services.llm import ChatMessage, ProviderError, ask_json
from pydantic import BaseModel


def test_extract_raw_json():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_fenced_json():
    text = "Here you go:\n```json\n{\"a\": [1, 2]}\n```\nThanks!"
    assert extract_json(text) == {"a": [1, 2]}


def test_extract_json_with_prose_and_braces_in_strings():
    text = 'Sure! {"text": "curly } brace {\\"quoted\\"", "n": 3} hope that helps'
    assert extract_json(text)["n"] == 3


def test_extract_json_array():
    assert extract_json("prefix [1, 2, 3] suffix") == [1, 2, 3]


def test_extract_json_invalid_raises():
    with pytest.raises(ValueError):
        extract_json("no json here at all")


class Thing(BaseModel):
    name: str


class FakeJsonProvider:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0

    def chat(self, messages, *, temperature=0.2, max_tokens=None):
        self.calls += 1
        return self.replies.pop(0)


def test_ask_json_retries_once_on_bad_output():
    provider = FakeJsonProvider(["this is not json", '{"name": "ok"}'])
    result = ask_json(provider, [ChatMessage(role="user", content="go")], Thing)
    assert result.name == "ok"
    assert provider.calls == 2


def test_ask_json_raises_after_retries():
    provider = FakeJsonProvider(["still not json", "nope"])
    with pytest.raises(ProviderError):
        ask_json(provider, [ChatMessage(role="user", content="go")], Thing)
    assert provider.calls == 2


def test_zai_provider_requires_api_key():
    from app.core.config import settings

    if settings.ZAI_API_KEY:
        pytest.skip("ZAI_API_KEY set in environment")
    from app.services.llm.zai import ZaiProvider

    with pytest.raises(ProviderError):
        ZaiProvider()
