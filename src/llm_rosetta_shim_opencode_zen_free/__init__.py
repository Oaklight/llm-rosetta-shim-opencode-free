"""OpenCode Zen's keyless free lane as a llm-rosetta plugin package.

Delivered as a plugin package: llm-rosetta discovers the
``llm_rosetta.shim_providers`` entry point and calls :func:`register_shims`,
which loads this package's bundled shim directory into the shim registry.
"""

from __future__ import annotations

from pathlib import Path

from llm_rosetta.shims import load_providers_from_dir

__version__ = "0.1.0"

_PROVIDERS_DIR = Path(__file__).parent / "providers"


def register_shims() -> None:
    """Load the bundled ``opencode_zen_free--chat_completions`` shim.

    Entry point for the ``llm_rosetta.shim_providers`` group.
    """
    load_providers_from_dir(_PROVIDERS_DIR)
