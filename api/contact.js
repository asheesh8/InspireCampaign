// Vercel function for the contact form. Sends the message by email through Resend.
// Env vars (set in Vercel): RESEND_API_KEY, CONTACT_TO (the inbox that receives leads),
// CONTACT_FROM (a sender on a domain verified in Resend, e.g. "Inspire Campaigns <site@inspirecampaigns.com>").
// TODO(owner): confirm which inbox should receive website leads.
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
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: CONTACT_FROM,
      to: CONTACT_TO.split(',').map((s) => s.trim()),
      reply_to: email,
      subject: `New project inquiry from ${name}`,
      html: `<p><strong>${esc(name)}</strong> &lt;${esc(email)}&gt;</p><p style="white-space:pre-wrap">${esc(message)}</p>`,
    }),
  });
  if (!r.ok) return res.status(502).json({ error: 'Email failed' });
  return res.status(200).json({ ok: true });
}
