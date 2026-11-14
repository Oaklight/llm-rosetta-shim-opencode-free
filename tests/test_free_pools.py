"""The three pools that joined the OpenCode lane: Kilo, LLM7 and OVHcloud.

LLM7 and OVHcloud serve reasoning on ``reasoning`` rather than
``reasoning_content``, and both ship the rename.  Kilo's free lane carries no
reasoning transform: the field name it uses has not been probed, and an
unverified rename is worse than none.

Two publish a typed or marked catalogue and need a filter; OVHcloud's carries
no type field and is offered whole.
"""

from __future__ import annotations

import pytest

from llm_rosetta.shims import get_shim
from llm_rosetta.shims.provider_shim import _reset_registry
from llm_rosetta.shims.providers import get_model_list_transform

from llm_rosetta_shim_free import register_shims

_REASONING_SHIMS = (
    "llm7--chat_completions",
    "ovhcloud--chat_completions",
)


@pytest.fixture()
def _registered():
    _reset_registry()
    register_shims()
    yield
    _reset_registry()


@pytest.mark.parametrize("shim_name", _REASONING_SHIMS)
def test_reasoning_is_renamed_on_the_message(_registered, shim_name):
    shim = get_shim(shim_name)
    assert shim is not None
    body = {
        "choices": [
            {"message": {"role": "assistant", "reasoning": "thinking", "content": "hi"}}
        ]
    }
    for transform in shim.pre_ir_transforms:
        body = transform(body)
    message = body["choices"][0]["message"]
    assert message["reasoning_content"] == "thinking"
    assert "reasoning" not in message


@pytest.mark.parametrize("shim_name", _REASONING_SHIMS)
def test_reasoning_is_renamed_on_the_stream_delta(_registered, shim_name):
    """The streaming path is the one that loses the text silently."""
    shim = get_shim(shim_name)
    assert shim is not None
    body = {"choices": [{"delta": {"reasoning": "part"}}]}
    for transform in shim.pre_ir_transforms:
        body = transform(body)
    assert body["choices"][0]["delta"]["reasoning_content"] == "part"


@pytest.mark.parametrize("shim_name", _REASONING_SHIMS)
def test_a_response_without_reasoning_is_untouched(_registered, shim_name):
    shim = get_shim(shim_name)
    assert shim is not None
    body = {"choices": [{"message": {"role": "assistant", "content": "hi"}}]}
    before = {"choices": [{"message": {"role": "assistant", "content": "hi"}}]}
    for transform in shim.pre_ir_transforms:
        body = transform(body)
    assert body == before


def test_kilo_free_offers_only_the_free_slice(_registered):
    """The keyless lane refuses the paid models, so the picker must not list them."""
    transform = get_model_list_transform("kilo_free--chat_completions")
    assert transform is not None
    entries = [
        {"id": "kilo-auto/free", "isFree": True},
        {"id": "cohere/north-mini-code:free", "isFree": True},
        {"id": "nvidia/nemotron-3-ultra", "isFree": False},
        {"isFree": True},  # no id
    ]
    ids, upstream = transform(entries)
    assert ids == ["kilo-auto/free", "cohere/north-mini-code:free"]
    assert upstream == {}


def test_llm7_offers_only_free_chat_models(_registered):
    transform = get_model_list_transform("llm7--chat_completions")
    assert transform is not None
    entries = [
        {"id": "chat-turbo-a", "model_type": "chat", "tier": "turbo"},
        {"id": "chat-turbo-b", "model_type": "chat", "tier": "turbo"},
        {"id": "chat-pro", "model_type": "chat", "tier": "pro"},
        {"id": "image-turbo", "model_type": "image", "tier": "turbo"},
        {"id": "decision", "model_type": "systemone", "tier": "pro"},
        {"model_type": "chat", "tier": "turbo"},  # no id
    ]
    ids, upstream = transform(entries)
    assert ids == ["chat-turbo-a", "chat-turbo-b"]
    assert upstream == {}


def test_ovhcloud_ships_no_model_list_hook(_registered):
    """Without a hook the admin sorts the upstream list itself."""
    assert get_model_list_transform("ovhcloud--chat_completions") is None
