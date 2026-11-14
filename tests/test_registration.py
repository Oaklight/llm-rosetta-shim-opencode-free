"""The plugin registers every keyless shim the package ships.

Each vendor is a flat leaf with no vendor manifest, so every declaration —
including ``keyless`` — stays on the leaf.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from llm_rosetta.shims import get_shim
from llm_rosetta.shims.provider_shim import _reset_registry

from llm_rosetta_shim_free import register_shims

_PROVIDERS = (
    Path(__file__).resolve().parents[1] / "src" / "llm_rosetta_shim_free" / "providers"
)

#: Every shim the package ships, with the base URL it must carry.
EXPECTED = {
    "kilo_free--chat_completions": "https://api.kilo.ai/api/gateway",
    "llm7--chat_completions": "https://api.llm7.io/v1",
    "opencode_zen_free--chat_completions": "https://opencode.ai/zen/v1",
    "ovhcloud--chat_completions": "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
}


@pytest.fixture()
def _registered():
    _reset_registry()  # clean registry, so only the plugin's shims are present
    register_shims()
    yield
    _reset_registry()


def _config(vendor: str) -> dict:
    return yaml.safe_load(
        (_PROVIDERS / vendor / "provider.yaml").read_text(encoding="utf-8")
    )


def test_registers_every_shim(_registered):
    assert {name for name in EXPECTED if get_shim(name) is not None} == set(EXPECTED)


@pytest.mark.parametrize(("name", "base_url"), sorted(EXPECTED.items()))
def test_each_shim_is_a_keyless_free_source(_registered, name, base_url):
    shim = get_shim(name)
    assert shim is not None
    assert shim.manifest is None
    assert shim.base == "chat_completions"
    assert shim.free_source is True
    assert shim.connection.keyless
    assert shim.connection.base_url == base_url
    # Keyless means "no key required", not "a key from the environment": the
    # shim must not name one, or the gateway would demand it.
    assert shim.connection.api_key_env is None


def test_no_leaf_demands_an_api_key():
    """A free source that demanded a key env var would defeat its own purpose."""
    offenders = []
    for leaf in sorted(_PROVIDERS.rglob("provider.yaml")):
        cfg = yaml.safe_load(leaf.read_text(encoding="utf-8")) or {}
        connection = cfg.get("connection") or {}
        if "api_key" in connection or "api_key_env" in connection:
            offenders.append(str(leaf.relative_to(_PROVIDERS)))
    assert offenders == []


def test_the_vendors_use_different_base_urls():
    """A copy-paste that left one vendor on another's host would be silent."""
    hosts = {url for url in EXPECTED.values()}
    assert len(hosts) == len(EXPECTED)


def test_provider_yaml_declares_the_canonical_names():
    for name in EXPECTED:
        vendor = name.split("--")[0]
        cfg = _config(vendor)
        assert cfg["name"] == name
        assert cfg["model_type"] == "llm"
        assert cfg["format"] == "chat_completions"


def test_the_opencode_lane_declares_the_client_shape():
    conn = _config("opencode_zen_free")["connection"]
    assert conn["keyless"] is True
    assert conn["stream_required"] is True
    assert conn["session_header"] == "x-opencode-session"
    assert conn["session_id_format"] == "opencode"
    assert conn["request_header"] == "x-opencode-request"
    assert conn["request_id_format"] == "opencode"
    # The lane's "credential" is the literal word `public`.
    assert conn["headers"]["Authorization"] == "Bearer public"
    assert conn["headers"]["User-Agent"].startswith("opencode/")


@pytest.mark.parametrize("vendor", sorted({name.split("--")[0] for name in EXPECTED}))
def test_every_hint_is_bilingual(vendor):
    """The admin form shows the hint in the operator's language."""
    hint = _config(vendor)["hint_msg"]
    assert isinstance(hint, dict)
    assert set(hint) >= {"en", "zh"}
    assert all(isinstance(value, str) and value.strip() for value in hint.values())
