# MailPilot — Autonomous Email-to-WhatsApp Agent

MailPilot connects to your mailbox over IMAP, scores every incoming email for
importance (rule engine plus optional AI), and forwards the ones that matter to
your WhatsApp as a clean alert card. It deduplicates everything it has already
seen, rate-limits alerts per cycle, and keeps a full audit trail.

```
Inbox (IMAP) ──> Fetcher ──> Importance Classifier ──> WhatsApp Sender
   (Gmail/Outlook/Yahoo)      rules + AI scoring        Meta Cloud API / Twilio
                                        │
                                   state.json (dedupe + history)
```

## Features

- Works with any IMAP provider (Gmail, Outlook, Yahoo presets)
- Hybrid importance filter: weighted keyword categories, VIP list, blocklist,
  bulk/promotion penalties, direct-to-you bonus — optional GPT re-scoring on top
- WhatsApp delivery via Meta Cloud API **or** Twilio (sandbox-friendly)
- `state.json` dedupe so no email is ever sent twice
- Per-cycle quota so a burst of emails cannot spam your phone
- Dry-run mode: see exactly what would be forwarded, send nothing
- Rotating log file in `logs/agent.log` plus `status` command

## Email backends: Gmail API (recommended) or IMAP

`email.backend` in `config.yaml` picks how MailPilot reads mail:

| backend      | transport   | best for                                            |
| ------------ | ----------- | --------------------------------------------------- |
| `gmail_api`  | HTTPS       | restricted/proxy networks where IMAP ports are blocked |
| `imap`       | TCP :993    | normal networks; any provider (Gmail/Outlook/Yahoo) |
| `auto`       | either      | uses Gmail API when `gmail_token.json` exists, else IMAP |

On flaky networks both backends also auto-resolve DNS through DNS-over-HTTPS
(Cloudflare/Google) and can tunnel IMAP through your system HTTP proxy when a
direct connection fails.

### One-time Gmail API setup (~5 minutes)

1. https://console.cloud.google.com -> create project "MailPilot".
2. APIs & Services -> Library -> search **Gmail API** -> **Enable**.
3. APIs & Services -> OAuth consent screen -> External -> fill app name/email ->
   add yourself under **Test users** -> Save.
4. APIs & Services -> Credentials -> **Create credentials** -> **OAuth client ID**
   -> Application type **Desktop app** -> Create.
5. Copy the client ID and secret into `.env`:
   ```
   GMAIL_CLIENT_ID=xxxx.apps.googleusercontent.com
   GMAIL_CLIENT_SECRET=GOCSPX-xxxx
   ```
6. Run the one-time browser consent:
   ```powershell
   python main.py auth-gmail
   ```
   A browser opens -> sign in -> Allow -> token is saved to `gmail_token.json`
   (auto-refreshes forever after that).

## Quick start

```powershell
cd email-whatsapp-agent
python -m venv .venv
.venv\Scripts\activate          # Windows (use source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
copy .env.example .env          # then edit .env with real values
python main.py status           # verify config loads
python main.py run --dry-run    # first check, nothing is sent
python main.py watch            # go live, checks every 5 minutes
```

## 1. Email credentials

Use an **App Password**, not your normal password.

| Provider | IMAP host              | How to get an app password                                  |
| -------- | ---------------------- | ----------------------------------------------------------- |
| Gmail    | `imap.gmail.com`       | Google Account -> Security -> 2FA -> App passwords           |
| Outlook  | `outlook.office365.com`| Microsoft account -> Security -> Advanced security options   |
| Yahoo    | `imap.mail.yahoo.com`  | Account Security -> Generate app password                    |

Put them in `.env`:

```
EMAIL_ADDRESS=you@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
```

## 2. WhatsApp delivery

### Option A — Meta WhatsApp Cloud API (recommended, free tier)

1. Go to https://developers.facebook.com and create an app (type: Business).
2. Add the **WhatsApp** product. On the *API Setup* page you get:
   - a temporary/permanent access token -> `WHATSAPP_TOKEN` in `.env`
   - a **Phone number ID** -> `whatsapp.meta_phone_number_id` in `config.yaml`
3. While in test mode, add your own phone number as a recipient and send the
   join message from WhatsApp to the test number.
4. Set `whatsapp.to_number` in `config.yaml` to your number in international
   format, e.g. `"+256700000000"`.

### Option B — Twilio sandbox (fastest to try)

1. Create a Twilio account, open Messaging -> Try it out -> WhatsApp sandbox.
2. Join the sandbox from your phone (`join <code>` message).
3. In `.env` set `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`.
4. In `config.yaml` set `provider: twilio` and keep the default
   `twilio_from_number` (the sandbox number) unless you have a real one.

## 3. Tuning what counts as "important"

Everything lives in `config.yaml`:

```yaml
classifier:
  min_score: 40            # raise this to forward fewer emails
  use_llm: true            # AI double-check when OPENAI_API_KEY is present
  vip_senders:
    - boss@yourcompany.com # always forwarded (+60 points)
  blocked_senders: []      # never forwarded
```

Scoring model (0-100):

| Signal                                    | Points |
| ----------------------------------------- | ------ |
| VIP sender                                | +60    |
| Security keywords (OTP, password reset..) | up to +64 |
| Urgent keywords (ASAP, deadline...)       | up to +56 |
| Finance keywords (invoice, payment...)    | up to +44 |
| Meeting keywords (invite, interview...)   | up to +40 |
| Personal keywords (can you call...)       | up to +32 |
| Sent directly to you                      | +12    |
| Has attachments                           | +5     |
| Automated sender (noreply@...)            | -18    |
| Newsletter / promo signals                | -45    |

If `OPENAI_API_KEY` is set, each email additionally gets a 0-10 rating from
GPT-4o-mini ("10 = must act now"); its verdict can override borderline rule
results. Without a key the agent silently runs on rules only.

## Commands

```text
python main.py run --dry-run   one pass, print what would be sent
python main.py run             one pass, live sending
python main.py watch           loop forever (default every 300s)
python main.py watch --dry-run continuous dry run
python main.py status          stats + last 10 processed emails
```

Useful flags: `--config path/to/config.yaml`, `-v` verbose logging.

## Run it in the cloud (free, no local PC needed)

The repo ships with `.github/workflows/mailpilot.yml`: a GitHub Actions job that
runs one full cycle every ~5 minutes on GitHub's servers (dedupe state is kept
in the Actions cache). Your PC can be switched off completely.

1. Create a **private** repository on GitHub (private keeps your numbers safe).
2. Upload this whole `email-whatsapp-agent` folder to it (GitHub web UI:
   "uploading an existing file" drag & drop works).
3. Repo -> Settings -> Secrets and variables -> Actions -> New repository secret.
   Add these four:
   - `EMAIL_ADDRESS`
   - `EMAIL_PASSWORD`
   - `WHATSAPP_TOKEN`
   - `GEMINI_API_KEY`
4. Repo -> Actions tab -> enable workflows if asked -> select "MailPilot" ->
   "Run workflow" to trigger the first cycle immediately.
5. From now on GitHub runs it automatically every 5 minutes. Note: free-tier
   cron can drift 3-15 minutes late; for instant IDLE push keep a device
   running `python main.py watch`.

## Run at startup

Windows Task Scheduler:

```text
Program:    D:\...\email-whatsapp-agent\.venv\Scripts\python.exe
Arguments:  D:\...\email-whatsapp-agent\main.py watch
Start in:   D:\...\email-whatsapp-agent
Trigger:    At log on
```

Linux/macOS cron:

```cron
@reboot cd /path/to/email-whatsapp-agent && .venv/bin/python main.py watch >> logs/cron.out 2>&1
```

## Project layout

```
email-whatsapp-agent/
├── main.py               CLI entrypoint (run | watch | status)
├── config.yaml           tuning: hosts, numbers, thresholds, keyword lists
├── .env.example          template for secrets -> copy to .env
├── requirements.txt
└── agent/
    ├── settings.py       config + env loading, validation
    ├── email_client.py   IMAP fetch, MIME parsing, HTML->text
    ├── classifier.py     importance scoring engine (+ optional LLM)
    ├── whatsapp.py       alert formatting + Meta/Twilio senders
    ├── state.py          JSON dedupe store + history
    └── agent.py          orchestration, cycle loop, logging setup
```

## Troubleshooting

- **Meta error 131030 (recipient not allowed)** — test numbers only deliver to
  recipients added in API Setup -> To -> Manage phone number list.
- **API returns 200 but no message arrives** — free-form texts only deliver
  inside a 24-hour window that opens when YOU message the business number once.
  From your phone, send any message (e.g. "hi") to the test number
  (+1 555-199-9734), then run MailPilot again. Outside windows MailPilot
  automatically falls back to the pre-approved `hello_world` template.
- **IMAP login failed (Gmail)** — app password required; normal passwords are rejected.
- **TLS handshake timeout on IMAP** — your network filters port 993; switch to
  `backend: gmail_api` (HTTPS works almost everywhere).
- **Twilio sandbox expired** — re-send `join <code>` from WhatsApp.
- **Nothing forwards** — run `--dry-run`, watch the printed scores, lower
  `min_score` or add keywords/VIP senders.
- **Duplicate alerts after wiping state** — delete `state.json` to re-scan;
  delete `logs/agent.log` if you want fresh logs.

Security notes: credentials stay local in `.env` (never committed); MailPilot
only reads mail via read-only IMAP sessions and never replies or deletes.
