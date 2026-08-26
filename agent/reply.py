import json
import logging
import smtplib
from email.message import EmailMessage as StdEmailMessage
from email.utils import formataddr
from pathlib import Path

logger = logging.getLogger("mailpilot.reply")

COMMANDS_DIR = Path("commands")


def parse_plus_command(text):
    text = (text or "").strip()
    if not text.lower().startswith("/plus"):
        return None
    rest = text[len("/plus"):].strip()
    if ":" not in rest:
        return {"error": "Usage: /plus email:message"}
    to, _, body = rest.partition(":")
    to = to.strip()
    body = body.strip()
    if "@" not in to or "." not in to:
        return {"error": f"'{to}' does not look like an email address"}
    if not body:
        return {"error": "Message body is empty"}
    return {"to": to, "message": body}


def smtp_send(account, to_addr, body):
    msg = StdEmailMessage()
    msg["From"] = formataddr(("MailPilot", account.address))
    msg["To"] = to_addr
    msg["Subject"] = "Sent via MailPilot"
    msg.set_content(body)
    host = getattr(account, "smtp_host", None) or "smtp.gmail.com"
    port = int(getattr(account, "smtp_port", 0) or 465)
    with smtplib.SMTP_SSL(host, port, timeout=30) as server:
        server.login(account.address, account.password)
        server.sendmail(account.address, [to_addr], msg.as_string())
    logger.info("Outgoing message delivered to %s via %s", to_addr, account.address)


class CommandProcessor:
    def __init__(self, settings, sender=None):
        self.settings = settings
        self.sender = sender
        self.commands_dir = COMMANDS_DIR
        self.commands_dir.mkdir(parents=True, exist_ok=True)

    def _default_account(self):
        for acc in self.settings.accounts:
            if acc.address and acc.password:
                return acc
        return None

    def pending(self):
        path = self.commands_dir / "pending.jsonl"
        if not path.exists():
            return []
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        path.write_text("", encoding="utf-8")
        parsed = []
        for line in lines:
            try:
                parsed.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return parsed

    def record(self, result):
        with open(self.commands_dir / "results.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(result) + "\n")

    def process(self):
        commands = self.pending()
        results = []
        for cmd in commands:
            parsed = parse_plus_command(cmd.get("text", ""))
            if parsed and "error" in parsed:
                result = {"ok": False, "to": "", "detail": parsed["error"]}
            elif parsed:
                account = self._default_account()
                if account is None:
                    result = {"ok": False, "to": parsed["to"], "detail": "no SMTP-capable account configured"}
                else:
                    try:
                        smtp_send(account, parsed["to"], parsed["message"])
                        result = {"ok": True, "to": parsed["to"], "via": account.address}
                    except Exception as exc:
                        result = {"ok": False, "to": parsed["to"], "detail": str(exc)[:200]}
            else:
                continue
            self.record(result)
            results.append(result)
            if self.sender is not None and not getattr(self.sender, "_dry", False):
                try:
                    if result["ok"]:
                        self.sender.send_text(f"MailPilot: delivered your message to {result['to']}")
                    else:
                        self.sender.send_text(f"MailPilot: could not send ({result['detail'][:120]})")
                except Exception:
                    pass
        return results
