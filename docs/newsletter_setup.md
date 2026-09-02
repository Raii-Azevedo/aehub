# Newsletter "What's New" — setup & go-live

Sends a periodic email with everything created/updated in the HUB in the last
`NEWSLETTER_PERIOD_DAYS` days (default 15). Reuses the existing `AllowedEmail`
table for recipients — no second user list.

Code: `core/newsletter_utils.py` (data + rendering + sending), `core/management/commands/send_newsletter.py`
(CLI entrypoint), `core/templates/core/email/newsletter.html` (the email itself).

## 1. Required Railway env vars (for real sending)

None of these exist yet in the project — you need to add them under the service's
**Variables** tab for actual emails to go out in production. Until they're set,
`EMAIL_BACKEND` falls back to Django's console backend (prints the email to the
Railway logs instead of sending it), so nothing breaks — it just won't deliver.

| Variable | Example | Notes |
|---|---|---|
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP server. If using Google Workspace, this is usually `smtp.gmail.com` with an **app password**, or your workspace's relay host if IT has one set up. |
| `EMAIL_PORT` | `587` | |
| `EMAIL_USE_TLS` | `True` | |
| `EMAIL_HOST_USER` | `hub@artefact.com` | The sending mailbox. |
| `EMAIL_HOST_PASSWORD` | *(app password / SMTP credential)* | Never a normal login password — generate an app-specific password. |
| `DEFAULT_FROM_EMAIL` | `AE Knowledge Hub <hub@artefact.com>` | What recipients see as the sender. |
| `SITE_URL` | `https://aertefact.up.railway.app` | Already defaults to the current Railway domain — only override if the domain changes. |

If Artefact IT prefers a transactional provider (SendGrid, Mailgun, Postmark, Resend,
Amazon SES) instead of raw SMTP, that's a one-line change: set `EMAIL_BACKEND` to the
provider's Django backend (usually via the `anymail` package) and its own API-key
variable — the rest of this feature (`newsletter_utils.py`, the template, the command)
doesn't change at all.

## 2. Phase 1 (current state) — test mode

Two variables control who receives the newsletter:

| Variable | Default | Effect |
|---|---|---|
| `NEWSLETTER_TEST_MODE` | `True` | While `True`, **only** `NEWSLETTER_TEST_RECIPIENTS` receives the email, no matter how many people are in `AllowedEmail`. |
| `NEWSLETTER_TEST_RECIPIENTS` | `raissa.azevedo@artefact.com` | Comma-separated list. |

This means right now, with zero extra configuration, the newsletter can only ever
reach `raissa.azevedo@artefact.com` — exactly as requested for the approval phase.

## 3. Going live to everyone

Once the design/content is approved:

1. In Railway → service Variables, set `NEWSLETTER_TEST_MODE=False`.
2. That's it — no code change. `_get_recipients()` in `core/newsletter_utils.py`
   automatically switches to every email in `AllowedEmail` (the exact same table
   used everywhere else in the HUB: login, roles, ranking, etc.).
3. To go back to test mode at any point (e.g. testing a template change), just set
   `NEWSLETTER_TEST_MODE=True` again.

## 4. Running it manually

```bash
# See what would be collected/sent without sending anything:
python manage.py send_newsletter --dry-run

# Force a different lookback window (e.g. test with 30 days of history):
python manage.py send_newsletter --dry-run --dias 30

# Send for real, to a specific address only (ignores test-mode/AllowedEmail):
python manage.py send_newsletter --to raissa.azevedo@artefact.com

# Send for real, using whatever NEWSLETTER_TEST_MODE currently resolves to:
python manage.py send_newsletter
```

## 5. Scheduling — recurring every 15 days

Cron (used by Railway's **Cron Schedule** feature, and by most schedulers) is
calendar-based, not interval-based — there's no native "every 15 days" expression.
The command itself doesn't care what schedule triggers it: it always looks back
exactly `NEWSLETTER_PERIOD_DAYS` days from the moment it runs. So the schedule
just needs to fire roughly every 15 days; the content window is always correct
regardless of tiny drift.

Recommended: in Railway, add a **Cron Schedule** to this service (Settings → Cron
Schedule) running:

```
0 9 1,16 * *
```

This fires at 09:00 on the 1st and 16th of every month (an interval of 15-16 days,
close enough that `NEWSLETTER_PERIOD_DAYS=15` never misses anything — a slightly
generous window is safer than a tight one for a "what's new" digest). The command
to run is:

```
python manage.py send_newsletter
```

If Railway's plan/setup doesn't support Cron Schedule on this service, the same
command can run from any external scheduler that can reach the app (a separate tiny
Railway cron service, GitHub Actions on a schedule hitting a protected endpoint, etc.) —
nothing in `newsletter_utils.py` depends on how it's triggered.

`NEWSLETTER_PERIOD_DAYS` is itself an env var, so the lookback window can be tuned
independently of the trigger schedule (e.g. keep the cron at "1st and 16th" but set
`NEWSLETTER_PERIOD_DAYS=16` to guarantee zero gap/overlap).

## 6. What counts as "new"

For each content type, an item is included if it was created **or** updated within
the window (`data_criacao` / `data_atualizacao`, the same fields the `changelog`
page already uses). Snippets and Certifications only track creation (no update
timestamp exists in their tables today), so those two are creation-only.

The single "🌟 Destaque do período" highlight is simply the most recently created
item across every section — deterministic, always genuinely the newest thing in the Hub.

## 7. Testing without touching production

`core/newsletter_utils.py` and the management command have no Railway-specific
code — they were verified end-to-end against a disposable local SQLite database
seeded with realistic content (some inside the 15-day window, some outside, one
"updated-but-old" case) and Django's in-memory (`locmem`) email backend, covering:

- Has-news case: correct item counts, correct New/Updated badges, correct highlight, correct links.
- No-news case: the friendly "maybe it's your turn to contribute" alternative is sent (not skipped).
- Test mode: only the configured test recipient(s) receive the email even with multiple `AllowedEmail` rows present.
- Go-live: flipping `NEWSLETTER_TEST_MODE` off sends to every seeded `AllowedEmail` row automatically.
