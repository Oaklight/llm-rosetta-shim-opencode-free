"""The plugin registers its ``opencode_zen_free--chat_completions`` shim."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from llm_rosetta.shims import get_shim
from llm_rosetta.shims.provider_shim import _reset_registry

from llm_rosetta_shim_opencode_zen_free import register_shims

_SHIM = "opencode_zen_free--chat_completions"
_YAML = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "llm_rosetta_shim_opencode_zen_free"
    / "providers"
    / "opencode_zen_free"
    / "provider.yaml"
)


@pytest.fixture()
def _registered():
    _reset_registry()  # clean registry, so only the plugin's shims are present
    register_shims()
    yield
    _reset_registry()


def _config() -> dict:
    return yaml.safe_load(_YAML.read_text(encoding="utf-8"))


def test_registers_the_free_lane_shim(_registered):
    shim = get_shim(_SHIM)
    assert shim is not None
    assert shim.base == "chat_completions"
    assert shim.free_source is True
    assert shim.connection.keyless
    assert shim.connection.base_url == "https://opencode.ai/zen/v1"
    assert shim.connection.api_key_env is None


def test_provider_yaml_declares_the_canonical_name():
    cfg = _config()
    assert cfg["name"] == _SHIM
    assert cfg["model_type"] == "llm"
    assert cfg["format"] == "chat_completions"


def test_the_shim_declares_the_client_shape():
    conn = _config()["connection"]
    assert conn["keyless"] is True
    assert conn["stream_required"] is True
    assert conn["session_header"] == "x-opencode-session"
    assert conn["session_id_format"] == "opencode"
    assert conn["request_header"] == "x-opencode-request"
    assert conn["request_id_format"] == "opencode"
    # The lane's "credential" is the literal word `public`.
    assert conn["headers"]["Authorization"] == "Bearer public"
    assert conn["headers"]["User-Agent"].startswith("opencode/")


def test_the_hint_is_bilingual():
    """The admin form shows the hint in the operator's language."""
    hint = _config()["hint_msg"]
    assert isinstance(hint, dict)
    assert set(hint) >= {"en", "zh"}
    assert all(isinstance(value, str) and value.strip() for value in hint.values())
