"""LLM7.io schema transforms.

Response-side: LLM7 serves reasoning text on ``message.reasoning`` /
``delta.reasoning``, while the Chat Completions converter reads
``reasoning_content``.

Model-list side: ``GET /v1/models`` mixes chat, image, video, speech and the
``systemone`` decision model, and tags each entry with a ``tier``.  The free
lane is the ``turbo`` tier, so only active chat models in that tier are
offered to a chat picker.
"""

from __future__ import annotations

from typing import Any

from llm_rosetta.transforms import _NamedTransform, hoist_late_system_messages


def _rename_reasoning_field(body: dict[str, Any]) -> dict[str, Any]:
    """Rename ``reasoning`` → ``reasoning_content`` on messages and deltas."""
    choices = body.get("choices")
    if not isinstance(choices, list):
        return body
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        for holder_key in ("message", "delta"):
            holder = choice.get(holder_key)
            if not isinstance(holder, dict):
                continue
            if "reasoning" in holder and "reasoning_content" not in holder:
                holder["reasoning_content"] = holder.pop("reasoning")
    return body


def model_list_transform(
    entries: list[dict[str, Any]],
) -> tuple[list[str], dict[str, str]]:
    """Keep the free-tier chat models.

    Args:
        entries: Upstream ``/models`` entries (OpenAI ``{data: [...]}`` slice).

    Returns:
        ``(model_ids, upstream_map)``.  Ids pass through unchanged, so the map
        is empty.
    """
    ids = [
        m["id"]
        for m in entries
        if m.get("model_type") == "chat" and m.get("tier") == "turbo" and m.get("id")
    ]
    return ids, {}


post_ir_transforms = ()
pre_ir_transforms = (_NamedTransform(_rename_reasoning_field, "rename_reasoning()"),)
ir_transforms = (hoist_late_system_messages(),)
