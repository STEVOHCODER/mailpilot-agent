const VERIFY_TOKEN = '28ada79281805079cda4f9b9d3ae5877';

export default {
  async fetch(request) {
    return handleRequest(request);
  }
};

async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;

  if (path === '/privacy') {
    return new Response(PRIVACY_HTML, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }

  if (path === '/terms') {
    return new Response(TERMS_HTML, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }

  if (path === '/delete') {
    return new Response(DELETE_HTML, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }

  if (path === '/webhook' && request.method === 'GET') {
    const mode = url.searchParams.get('hub.mode');
    const token = url.searchParams.get('hub.verify_token');
    const challenge = url.searchParams.get('hub.challenge');
    if (mode === 'subscribe' && token === VERIFY_TOKEN) {
      return new Response(challenge, { status: 200 });
    }
    return new Response('Forbidden', { status: 403 });
  }

  if (path === '/webhook' && request.method === 'POST') {
    try {
      const body = await request.json();
      const entries = body.entry || [];
      for (const entry of entries) {
        const changes = entry.changes || [];
        for (const change of changes) {
          const value = change.value || {};
          const messages = value.messages || [];
          for (const msg of messages) {
            const ns = MAILPLOT_KV;
            await ns.put('pending', JSON.stringify([{
              from: msg.from || '',
              text: (msg.text && msg.text.body) || '',
              ts: Date.now()
            }]));
          }
        }
      }
    } catch (e) {}
    return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'Content-Type': 'application/json' } });
  }

  return new Response('Not Found', { status: 404 });
}

const PRIVACY_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MailPilot - Privacy Policy</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#1a1a2e;background:#f8f9fa;line-height:1.7;max-width:800px;margin:0 auto;padding:40px 20px}
h1{font-size:2rem;margin-bottom:8px;color:#1a1a2e}
h2{font-size:1.3rem;margin:28px 0 10px;color:#1a1a2e}
.meta{color:#6c757d;font-size:.9rem;margin-bottom:32px}
p,li{font-size:1rem;color:#333}
ul{margin-left:20px;margin-bottom:12px}
li{margin-bottom:6px}
footer{margin-top:40px;padding-top:16px;border-top:1px solid #dee2e6;color:#6c757d;font-size:.85rem}
</style>
</head>
<body>
<h1>MailPilot Privacy Policy</h1>
<p class="meta">Effective Date: August 26, 2026 &bull; Last Updated: August 26, 2026</p>
<p>MailPilot ("we", "our") is an email-to-WhatsApp forwarding agent. This Privacy Policy explains how we handle your data.</p>
<h2>1. Data We Collect</h2>
<ul>
<li><strong>Email metadata</strong> &mdash; sender, recipient, subject, timestamp, and body of emails from your connected Gmail account(s).</li>
<li><strong>WhatsApp messages</strong> &mdash; messages you send to MailPilot via WhatsApp for command processing (e.g., <code>/plus</code> reply commands).</li>
<li><strong>Credentials</strong> &mdash; Gmail app passwords and WhatsApp API tokens, stored encrypted as GitHub Actions secrets. We never log or expose these.</li>
</ul>
<h2>2. How We Use Your Data</h2>
<ul>
<li>Emails are fetched, classified for importance, summarized by AI (Google Gemini), and forwarded as alerts to your WhatsApp.</li>
<li>WhatsApp commands are processed to send emails on your behalf via SMTP.</li>
<li>Data is used solely to operate the MailPilot service for your personal use.</li>
</ul>
<h2>3. Data Storage &amp; Retention</h2>
<ul>
<li>Email deduplication state is stored in GitHub Actions cache (expires after 7 days).</li>
<li>Pending WhatsApp commands are stored temporarily in Cloudflare KV and deleted immediately after processing.</li>
<li>We do not store email bodies long-term. Only message IDs are kept to prevent duplicate alerts.</li>
</ul>
<h2>4. Third-Party Services</h2>
<ul>
<li><strong>Google Gemini API</strong> &mdash; used for email classification and summarization.</li>
<li><strong>Meta Cloud API</strong> &mdash; used for WhatsApp message delivery.</li>
<li><strong>Cloudflare</strong> &mdash; used for webhook bridging.</li>
<li><strong>GitHub Actions</strong> &mdash; used for workflow automation.</li>
</ul>
<h2>5. Data Sharing</h2>
<p>We do not sell, trade, or share your personal data with third parties beyond what is necessary to operate the service.</p>
<h2>6. Data Deletion</h2>
<p>You may request deletion of all your data by messaging "delete my data" on WhatsApp or emailing us. We will process deletion within 24 hours.</p>
<h2>7. Security</h2>
<p>All credentials are stored as encrypted GitHub Actions secrets. API communications use TLS encryption.</p>
<h2>8. Contact</h2>
<p>For privacy questions or data deletion requests: <strong>stevohsunb@gmail.com</strong></p>
<footer>&copy; 2026 MailPilot. All rights reserved.</footer>
</body>
</html>`;

const TERMS_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MailPilot - Terms of Service</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;max-width:800px;margin:0 auto;padding:40px 20px;line-height:1.7;color:#333}
h1{margin-bottom:8px;font-size:2rem}h2{margin:24px 0 8px;font-size:1.3rem}
.meta{color:#6c757d;font-size:.9rem;margin-bottom:32px}
footer{margin-top:40px;padding-top:16px;border-top:1px solid #dee2e6;color:#6c757d;font-size:.85rem}
</style>
</head>
<body>
<h1>MailPilot Terms of Service</h1>
<p class="meta">Effective: August 26, 2026</p>
<h2>1. Acceptance</h2><p>By using MailPilot you agree to these terms.</p>
<h2>2. Description</h2><p>MailPilot monitors Gmail inboxes and forwards important email alerts to WhatsApp. It can also send emails on your behalf via WhatsApp commands.</p>
<h2>3. User Responsibilities</h2>
<ul>
<li>You must own or have authorization for any email account connected to MailPilot.</li>
<li>You are responsible for the content of emails sent via the /plus command.</li>
<li>You must not use MailPilot for spam, phishing, or any illegal activity.</li>
</ul>
<h2>4. Service Availability</h2><p>MailPilot runs on free-tier infrastructure (GitHub Actions, Cloudflare Workers). We do not guarantee 100% uptime.</p>
<h2>5. Limitation of Liability</h2><p>MailPilot is provided "as is" without warranties. We are not liable for any damages arising from use of the service.</p>
<h2>6. Termination</h2><p>We reserve the right to suspend or terminate access at any time.</p>
<h2>7. Contact</h2><p>Questions? Email <strong>stevohsunb@gmail.com</strong></p>
<footer>&copy; 2026 MailPilot. All rights reserved.</footer>
</body>
</html>`;

const DELETE_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MailPilot - Data Deletion</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;line-height:1.7;color:#333}
h1{margin-bottom:12px;font-size:2rem}
code{background:#f0f0f0;padding:2px 6px;border-radius:4px}
pre{background:#f0f0f0;padding:12px;border-radius:6px;overflow-x:auto}
</style>
</head>
<body>
<h1>Data Deletion Request</h1>
<p>To request deletion of all your data, send a message on WhatsApp saying:</p>
<pre>delete my data</pre>
<p>Or email <strong>stevohsunb@gmail.com</strong> with your request.</p>
<p>We will process deletion requests within 24 hours.</p>
</body>
</html>`;