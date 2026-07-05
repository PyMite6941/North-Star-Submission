"""Discord announcements-channel sync — read-only, one-way, feeds Study RAG.

Pulls messages from a single Discord text channel (e.g. the official Polaris Student
"#announcements" channel) via Discord's official REST API using a bot token scoped to the
minimum permissions (View Channel + Read Message History only — never posts, never
deletes, never joins voice). Writes them to a local Markdown file that `polaris rag
ingest` picks up, so announcements become searchable/citable offline between syncs.

This is a periodic snapshot, not a live embed — see
`docs/discord-announcements-sync.md` for why a live embed isn't possible, and exactly
what has to be set up on the Discord side (by a server admin) before this will work.
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import httpx
from polaris_core.logging import get_logger

logger = get_logger(__name__)

_API_BASE = "https://discord.com/api/v10"
_MAX_PER_REQUEST = 100


class DiscordSyncError(RuntimeError):
    """Raised when Discord rejects the request (bad token, missing permission, etc.)."""


def fetch_channel_messages(
    channel_id: str, bot_token: str, *, limit: int = 200, timeout: float = 10.0
) -> list[dict]:
    """Fetch up to `limit` recent messages from a channel, oldest first.

    Read-only: this only ever GETs `/messages`. Paginates backward via Discord's `before`
    cursor and honours `Retry-After` on a 429 instead of hammering the API.
    """
    if not bot_token:
        raise DiscordSyncError("No bot token configured (DISCORD_BOT_TOKEN).")
    if not channel_id:
        raise DiscordSyncError("No channel id configured (DISCORD_ANNOUNCEMENTS_CHANNEL_ID).")

    headers = {"Authorization": f"Bot {bot_token}"}
    messages: list[dict] = []
    before: str | None = None

    with httpx.Client(timeout=timeout) as client:
        while len(messages) < limit:
            params: dict = {"limit": min(_MAX_PER_REQUEST, limit - len(messages))}
            if before:
                params["before"] = before
            resp = client.get(
                f"{_API_BASE}/channels/{channel_id}/messages", headers=headers, params=params
            )
            if resp.status_code == 429:
                retry_after = float(resp.json().get("retry_after", 1.0))
                logger.warning("Discord rate limit hit; waiting %.1fs", retry_after)
                time.sleep(retry_after)
                continue
            if resp.status_code == 403:
                raise DiscordSyncError(
                    "Discord returned 403 Forbidden — the bot isn't in the server, or lacks "
                    "'View Channel' / 'Read Message History' on this channel."
                )
            if resp.status_code == 401:
                raise DiscordSyncError("Discord returned 401 Unauthorized — check the bot token.")
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            messages.extend(batch)
            before = batch[-1]["id"]
            if len(batch) < _MAX_PER_REQUEST:
                break

    messages.reverse()  # oldest first, readable top-to-bottom
    return messages


def to_markdown(messages: list[dict], channel_name: str = "announcements") -> str:
    """Render fetched messages as a Markdown note, ready for `polaris rag ingest`."""
    lines = [f"# #{channel_name} (synced {datetime.now().isoformat(timespec='minutes')})", ""]
    for m in messages:
        author = m.get("author", {}).get("username", "unknown")
        timestamp = m.get("timestamp", "")
        content = (m.get("content") or "").strip()
        if not content:
            continue  # skip embed-only / attachment-only messages: nothing to index as text
        lines.append(f"## {author} — {timestamp}")
        lines.append(content)
        lines.append("")
    return "\n".join(lines) + "\n"


def sync_channel(
    channel_id: str,
    bot_token: str,
    out_path: str | Path,
    *,
    channel_name: str = "announcements",
    limit: int = 200,
) -> Path:
    """Fetch recent messages and write them to `out_path` as Markdown. Returns the path."""
    messages = fetch_channel_messages(channel_id, bot_token, limit=limit)
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_markdown(messages, channel_name=channel_name), encoding="utf-8")
    logger.info("Synced %d message(s) from #%s → %s", len(messages), channel_name, path)
    return path
