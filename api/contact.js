// Vercel function for the contact form. Sends the message by email through Resend.
// Env vars (set in Vercel): RESEND_API_KEY, CONTACT_TO (the inbox that receives leads),
// CONTACT_FROM (a sender on a domain verified in Resend, e.g. "Inspire Campaigns <site@inspirecampaigns.com>").
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const clean = (v, max) => String(v ?? '').trim().slice(0, max);
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
  if (body.company) return res.status(200).json({ ok: true }); // honeypot: bots fill the hidden field

  const firstName = clean(body.firstName, 80);
  const lastName = clean(body.lastName, 80);
  const email = clean(body.email, 200);
  const message = clean(body.message, 5000);
  if (!firstName || !EMAIL.test(email) || message.length < 10) return res.status(400).json({ error: 'Invalid form' });

  const { RESEND_API_KEY, CONTACT_TO, CONTACT_FROM } = process.env;
  if (!RESEND_API_KEY || !CONTACT_TO || !CONTACT_FROM) return res.status(503).json({ error: 'Contact form not configured' });

  const name = `${firstName} ${lastName}`.trim();
  const when = new Date().toLocaleString('en-US', { timeZone: 'America/New_York', dateStyle: 'medium', timeStyle: 'short' });
  // Hitting Reply answers the person who filled in the form, because reply_to is their address.
  const html = `<div style="margin:0;padding:24px;background:#0F2A3F;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#FFFFFF;border-radius:14px;overflow:hidden">
    <tr><td style="height:6px;background:#F0476A;font-size:0;line-height:0">&nbsp;</td></tr>
    <tr><td style="padding:28px 28px 8px">
      <p style="margin:0;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#7A8794">New enquiry from inspirecampaigns.com</p>
      <h1 style="margin:10px 0 0;font-size:24px;line-height:1.2;color:#10161C">${esc(name)}</h1>
      <p style="margin:6px 0 0;font-size:15px;color:#48525C"><a href="mailto:${esc(email)}" style="color:#1F6FB2;text-decoration:none">${esc(email)}</a></p>
    </td></tr>
    <tr><td style="padding:20px 28px 0">
      <div style="background:#F4F6F8;border-radius:10px;padding:18px 20px">
        <p style="margin:0;font-size:16px;line-height:1.55;color:#10161C;white-space:pre-wrap">${esc(message)}</p>
      </div>
    </td></tr>
    <tr><td style="padding:18px 28px 28px">
      <p style="margin:0;font-size:14px;color:#48525C">Hit <strong>Reply</strong> to answer ${esc(firstName)} directly.</p>
      <p style="margin:14px 0 0;font-size:12px;color:#8A949E">Sent ${esc(when)} ET from the contact form.</p>
    </td></tr>
  </table>
</div>`;
  const text = `New enquiry from inspirecampaigns.com\n\n${name}\n${email}\n\n${message}\n\nReply to this email to answer ${firstName} directly.\nSent ${when} ET from the contact form.`;
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: CONTACT_FROM,
      to: CONTACT_TO.split(',').map((s) => s.trim()),
      reply_to: email,
      subject: `New project enquiry: ${name}`,
      html,
      text,
    }),
  });
  if (!r.ok) return res.status(502).json({ error: 'Email failed' });
  return res.status(200).json({ ok: true });
}
