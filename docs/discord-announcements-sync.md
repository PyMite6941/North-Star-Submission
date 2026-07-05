# Discord announcements sync

Pulls the official Polaris Student `#announcements` channel into Study RAG so it's
searchable and citable **offline**, between syncs. This is a **one-way, read-only,
periodic snapshot** — not a live embed. That's a deliberate choice, not a limitation we
missed:

- Discord's only no-bot embed option (the **guild widget**) shows online members, voice
  channels, and an invite link — it never shows text channel messages. There is no
  zero-setup way to display real channel content.
- Actually reading messages requires a bot with API access, which means either
  continuous polling or a persistent gateway connection — both need the app to be online
  all the time and to hold a live credential, which conflicts with this project's
  offline-first, no-account design (see [`SUBMISSION.md`](../SUBMISSION.md)).

So instead: sync on demand (or on a schedule, whenever there's a connection), write what
was fetched to a local Markdown file, and let the existing Study RAG pipeline
(`polaris rag ingest`) make it permanently available offline — same as any other note.

## What has to happen first (on the Discord side)

**This part cannot be done from this repo or by an AI agent** — it requires someone with
**admin/moderator access to the official Polaris Student Discord**
(<https://discord.gg/QurUJfv2>) to complete these steps. A contest entrant's own Discord
account does not have the access to do this unless a Polaris Student admin grants it.

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and
   create a new Application, then add a **Bot** to it.
2. On the Bot page, enable the **"Message Content Intent"** toggle (a privileged intent —
   without it, the bot can see a channel exists but not read message text).
3. Open **OAuth2 → URL Generator**. Under **Scopes**, check `bot`. Under **Bot
   Permissions**, check only:
   - `View Channel`
   - `Read Message History`

   Do **not** grant `Send Messages`, `Manage Server`, `Administrator`, or anything else —
   this integration only ever reads.
4. Copy the generated URL and have a **Polaris Student server admin** open it and approve
   adding the bot to the server. (Only someone with "Manage Server" on that Discord can do
   this step.)
5. In Discord, enable **Developer Mode** (User Settings → Advanced), then right-click the
   `#announcements` channel → **Copy Channel ID**.
6. Copy the bot's token from the Developer Portal (Bot page → "Reset Token" if it's not
   already visible — Discord only shows it once).

## What to put in `.env`

Never commit these — `.env` is already git-ignored.

```bash
DISCORD_BOT_TOKEN=<the bot token from step 6>
DISCORD_ANNOUNCEMENTS_CHANNEL_ID=<the channel id from step 5>
```

`polaris config show` will confirm both are set without ever printing the token itself
(it's masked the same way `GROQ_API_KEY` is).

## Running the sync

```bash
polaris rag sync-discord                      # fetch, write a note, and ingest it
polaris rag sync-discord --no-ingest           # just write the note, ingest later yourself
polaris rag sync-discord --limit 50            # fewer messages
polaris rag sync-discord --export path/to.md   # custom output path
```

By default it writes to
`study local notes with vector db/discord_sync/announcements.md` and immediately runs
`polaris rag ingest` on it, so `polaris rag ask "..." --show-sources` can cite it right
away. Re-running the command overwrites that file and re-ingests it (the existing
incremental-ingest content-hash logic in `study_rag/ingest.py` means an unchanged sync is
a no-op).

## Operational notes

- **Rate limits**: the sync paginates in batches of 100 and backs off on a 429 using
  Discord's `Retry-After` value — see `packages/study_rag/discord_sync.py`. Run it a few
  times a day at most (e.g. a cron job / scheduled task); there's no reason to poll more
  often than announcements actually get posted.
- **Read-only, always**: the code only ever issues `GET /channels/{id}/messages`. It
  never posts, edits, deletes, or joins voice — matching the minimal permission scope
  from step 3.
- **Scope it to one channel on purpose**: only sync a public, read-only announcements
  channel, not a general-chat channel where students are talking — this keeps other
  members' conversations out of a local vector DB entirely.
- **If the bot is removed or the token is revoked**, the sync simply starts failing with
  a clear `DiscordSyncError` (403/401) — nothing else in North Star depends on it.
