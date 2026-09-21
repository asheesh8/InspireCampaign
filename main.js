// Inspire Campaigns. No build step: plain ES module, loaded on every page.
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
const root = document.documentElement;

/* ---------- smooth scrolling (Lenis) in light and dark. Trippy mode and reduced motion scroll natively. ---------- */
let lenis = null;
const syncSmooth = () => {
  const want = !reduceMotion && window.Lenis && root.dataset.theme !== 'pop';
  if (want && !lenis) lenis = new window.Lenis({ lerp: 0.1, wheelMultiplier: 0.95, anchors: { offset: -84 }, autoRaf: true });
  if (!want && lenis) { lenis.destroy(); lenis = null; }
};
syncSmooth();
const lockScroll = (on) => { if (lenis) on ? lenis.stop() : lenis.start(); };

/* ---------- colour modes: light, dark, pop ("Trippy") ---------- */
const MODES = { light: { emoji: '☀️', color: '#F3F1EC' }, dark: { emoji: '\u{1F319}', color: '#0F0F0D' }, pop: { emoji: '\u{1F300}', color: '#0F2A3F' } };
const themeMeta = $('meta[name="theme-color"]');
const syncModeUI = () => {
  const t = root.dataset.theme;
  $$('[data-modes-cur]').forEach((el) => (el.textContent = MODES[t].emoji));
  $$('[data-mode]').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.mode === t)));
  if (themeMeta) themeMeta.content = MODES[t].color;
};
const setTheme = (t, from) => {
  if (!MODES[t] || t === root.dataset.theme) return;
  try { localStorage.setItem('ic-mode', t); } catch {}
  const apply = () => { root.dataset.theme = t; syncModeUI(); syncSmooth(); };
  if (!document.startViewTransition || reduceMotion) return apply();
  if (from) {
    const r = from.getBoundingClientRect();
    root.style.setProperty('--vt-x', `${r.left + r.width / 2}px`);
    root.style.setProperty('--vt-y', `${r.top + r.height / 2}px`);
  }
  root.dataset.vt = 'theme';
  document.startViewTransition(apply).finished.finally(() => delete root.dataset.vt);
};
syncModeUI();

const modes = $('[data-modes]');
if (modes) {
  const btn = $('[data-modes-btn]', modes);
  const menu = $('[data-modes-menu]', modes);
  const items = $$('[data-mode]', menu);
  const open = (on, focusItem) => {
    btn.setAttribute('aria-expanded', String(on));
    menu.hidden = !on;
    if (on && focusItem) (items.find((i) => i.getAttribute('aria-checked') === 'true') || items[0]).focus();
  };
  btn.addEventListener('click', () => open(menu.hidden, true));
  menu.addEventListener('click', (e) => {
    const item = e.target.closest('[data-mode]');
    if (!item) return;
    open(false);
    btn.focus();
    setTheme(item.dataset.mode, btn);
  });
  menu.addEventListener('keydown', (e) => {
    const i = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % items.length].focus(); }
    if (e.key === 'ArrowUp') { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
    if (e.key === 'Escape' || e.key === 'Tab') { open(false); if (e.key === 'Escape') btn.focus(); }
  });
  document.addEventListener('click', (e) => !modes.contains(e.target) && !menu.hidden && open(false));
}

/* ---------- nav, sheet, dock ---------- */
const nav = $('[data-nav]');
const sentinel = $('[data-top-sentinel]');
if (nav && sentinel) new IntersectionObserver(([e]) => nav.classList.toggle('is-stuck', !e.isIntersecting)).observe(sentinel);

const burger = $('[data-burger]');
const sheet = $('[data-sheet]');
if (burger && sheet) {
  const set = (open) => {
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    burger.innerHTML = `<i class="ph ${open ? 'ph-x' : 'ph-list'}" aria-hidden="true"></i>`;
    sheet.hidden = !open;
    document.body.classList.toggle('sheet-open', open);
    lockScroll(open);
  };
  burger.addEventListener('click', () => set(burger.getAttribute('aria-expanded') !== 'true'));
  sheet.addEventListener('click', (e) => e.target.closest('a') && set(false));
  addEventListener('keydown', (e) => e.key === 'Escape' && !sheet.hidden && set(false));
}

// hide the mobile CTA dock while a full-size CTA or the footer is on screen
const dock = $('[data-dock]');
if (dock) {
  const seen = new Set();
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => (e.isIntersecting ? seen.add(e.target) : seen.delete(e.target)));
    dock.classList.toggle('is-hidden', seen.size > 0);
  });
  $$('[data-hide-dock]').forEach((el) => io.observe(el));
}

/* ---------- reveals ---------- */
const hero = $('[data-hero]');
requestAnimationFrame(() => hero?.classList.add('is-ready'));
const revealer = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (!e.isIntersecting) return;
    e.target.classList.add('is-in');
    revealer.unobserve(e.target);
  });
}, { rootMargin: '0px 0px -8% 0px' });
$$('.reveal').forEach((el) => revealer.observe(el));

/* ---------- autoplaying loops: pause off screen, never autoplay under reduced motion ---------- */
const loops = $$('video[autoplay]');
if (reduceMotion) loops.forEach((v) => { v.removeAttribute('autoplay'); v.pause(); });
else {
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    const v = e.target;
    if (e.isIntersecting) v.play().catch(() => {}); else v.pause();
  }));
  loops.forEach((v) => io.observe(v));
}

/* ---------- hero reels drift toward the pointer (eased, so it never snaps) ---------- */
const stage = $('[data-stage]');
if (stage && finePointer && !reduceMotion) {
  const reels = $$('[data-depth]', stage);
  let tx = 0, ty = 0, x = 0, y = 0, raf = 0;
  const tick = () => {
    x += (tx - x) * 0.08; y += (ty - y) * 0.08;
    reels.forEach((r) => {
      const d = Number(r.dataset.depth);
      r.style.setProperty('--px', `${(x * 18 * d).toFixed(2)}px`);
      r.style.setProperty('--py', `${(y * 14 * d).toFixed(2)}px`);
    });
    raf = Math.abs(tx - x) + Math.abs(ty - y) > 0.001 ? requestAnimationFrame(tick) : 0;
  };
  const kick = () => { if (!raf) raf = requestAnimationFrame(tick); };
  hero.addEventListener('pointermove', (e) => {
    const r = stage.getBoundingClientRect();
    tx = ((e.clientX - r.left) / r.width - 0.5) * 2;
    ty = ((e.clientY - r.top) / r.height - 0.5) * 2;
    kick();
  });
  hero.addEventListener('pointerleave', () => { tx = 0; ty = 0; kick(); });
}

/* ---------- work tiles: silent preview on hover (desktop) or while in view (touch) ---------- */
const startPreview = (tile) => {
  const v = $('video', tile);
  if (!v || reduceMotion) return;
  if (!v.src) v.src = v.dataset.src;
  v.play().then(() => tile.classList.add('is-playing')).catch(() => {});
};
const stopPreview = (tile) => {
  const v = $('video', tile);
  if (!v) return;
  v.pause();
  tile.classList.remove('is-playing');
};
const tiles = $$('[data-tile]');
if (finePointer) {
  tiles.forEach((t) => {
    t.addEventListener('pointerenter', () => startPreview(t));
    t.addEventListener('pointerleave', () => stopPreview(t));
    t.addEventListener('focusin', () => startPreview(t));
    t.addEventListener('focusout', () => stopPreview(t));
  });
} else {
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    e.isIntersecting ? startPreview(e.target) : stopPreview(e.target);
  }), { threshold: 0.7 });
  tiles.forEach((t) => io.observe(t));
}

/* ---------- lightbox player ---------- */
const player = $('[data-player]');
if (player) {
  const video = $('[data-player-video]', player);
  const title = $('[data-player-title]', player);
  let opener = null;
  const close = () => player.open && player.close();
  player.addEventListener('close', () => {
    video.pause();
    video.removeAttribute('src');
    video.load();
    lockScroll(false);
    if (!reduceMotion) $$('.hero video').forEach((v) => v.play().catch(() => {}));
    opener?.focus();
  });
  $('[data-player-close]', player).addEventListener('click', close);
  player.addEventListener('click', (e) => e.target === player && close()); // backdrop click
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-play]');
    if (!btn) return;
    e.preventDefault();
    opener = btn;
    player.classList.toggle('is-tall', btn.hasAttribute('data-tall'));
    title.textContent = btn.dataset.title || '';
    video.src = btn.dataset.play;
    $$('.hero video').forEach((v) => v.pause());
    lockScroll(true);
    player.showModal();
    video.play().catch(() => {});
  });
}

/* ---------- work page filters ---------- */
const filters = $('[data-filters]');
const gallery = $('[data-gallery]');
if (filters && gallery) {
  const empty = $('[data-empty]');
  filters.addEventListener('click', (e) => {
    const chip = e.target.closest('[data-filter]');
    if (!chip) return;
    const cat = chip.dataset.filter;
    const run = () => {
      $$('[data-filter]', filters).forEach((c) => c.setAttribute('aria-pressed', String(c === chip)));
      let shown = 0;
      $$('[data-tile]', gallery).forEach((t) => {
        const on = cat === 'all' || t.dataset.cat === cat;
        t.hidden = !on;
        if (on) { shown++; t.classList.add('is-in'); }
      });
      empty.hidden = shown > 0;
    };
    document.startViewTransition && !reduceMotion ? document.startViewTransition(run) : run();
  });
}

/* ---------- Vermont maps ---------- */
// Pins are drawn in screen pixels; k (viewBox units per rendered pixel) keeps them the same size at any zoom.
const pinScale = (svg) => {
  const w = svg.getBoundingClientRect().width;
  if (!w) return;
  const k = svg.viewBox.baseVal.width / w;
  $$('.pin__in', svg).forEach((g) => g.setAttribute('transform', `scale(${k.toFixed(3)})`));
};
const maps = $$('svg.vmap');
maps.forEach(pinScale);
const mapSizer = new ResizeObserver((entries) => entries.forEach((e) => pinScale(e.target)));
maps.forEach((m) => mapSizer.observe(m));

const atlas = $('[data-atlas]');
if (atlas) {
  const svg = $('svg.vmap', atlas);
  const full = svg.viewBox.baseVal;
  const home = [full.x, full.y, full.width, full.height];
  const reset = $('[data-atlas-reset]', atlas);
  const COUNTY = { burlington: 'Chittenden', winooski: 'Chittenden', colchester: 'Chittenden', johnson: 'Lamoille' };
  let anim = 0;
  const tweenTo = (to) => {
    cancelAnimationFrame(anim);
    const vb = svg.viewBox.baseVal;
    const from = [vb.x, vb.y, vb.width, vb.height];
    const t0 = performance.now();
    const dur = reduceMotion ? 0 : 900;
    const step = (now) => {
      const p = dur ? Math.min(1, (now - t0) / dur) : 1;
      const e = 1 - Math.pow(1 - p, 4); // ease-out quart
      const v = from.map((f, i) => f + (to[i] - f) * e);
      svg.setAttribute('viewBox', v.map((n) => n.toFixed(1)).join(' '));
      pinScale(svg);
      if (p < 1) anim = requestAnimationFrame(step);
    };
    anim = requestAnimationFrame(step);
  };
  const select = (id) => {
    $$('[data-place]', atlas).forEach((p) => p.classList.toggle('is-on', p.dataset.place === (id || 'all')));
    $$('[data-place-btn]', atlas).forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.placeBtn === id)));
    $$('.pin', svg).forEach((p) => p.classList.toggle('is-on', p.dataset.pin === id));
    $$('.vmap__c', svg).forEach((c) => c.classList.toggle('is-lit', !!id && c.dataset.county === COUNTY[id]));
    svg.classList.toggle('is-zoomed', !!id);
    reset.hidden = !id;
    if (!id) return tweenTo(home);
    const pin = $(`[data-pin="${id}"]`, svg).transform.baseVal[0].matrix;
    const w = id === 'johnson' ? 380 : 190; const h = w * (home[3] / home[2]);
    tweenTo([pin.e - w / 2, pin.f - h / 2, w, h]);
  };
  atlas.addEventListener('click', (e) => {
    const b = e.target.closest('[data-place-btn]');
    const pin = e.target.closest('.pin');
    if (b) select(b.getAttribute('aria-pressed') === 'true' ? null : b.dataset.placeBtn);
    else if (pin) select(pin.dataset.pin);
    else if (e.target.closest('[data-atlas-reset]')) select(null);
  });
  const fromHash = location.hash.slice(1);
  if (COUNTY[fromHash]) select(fromHash);
}

/* ---------- contact form ---------- */
// Posts JSON to /api/contact (a Vercel function). Validation runs on the client first, then again on the server.
const form = $('[data-contact]');
if (form) {
  const status = $('[data-status]', form);
  const submit = $('button[type="submit"]', form);
  const rules = {
    firstName: (v) => (v.trim() ? '' : 'Please add your first name.'),
    email: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()) ? '' : 'Please enter a valid email, like you@business.com.'),
    message: (v) => (v.trim().length >= 10 ? '' : 'Tell us a little more, at least a sentence.'),
  };
  const check = (input) => {
    const rule = rules[input.name];
    if (!rule) return true;
    const msg = rule(input.value);
    input.setAttribute('aria-invalid', String(Boolean(msg)));
    const err = $(`#${input.id}-err`);
    if (err) err.textContent = msg;
    return !msg;
  };
  form.addEventListener('blur', (e) => e.target.name in rules && e.target.value && check(e.target), true);
  form.addEventListener('input', (e) => e.target.getAttribute('aria-invalid') === 'true' && check(e.target));

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const inputs = Object.keys(rules).map((n) => form.elements[n]);
    const bad = inputs.filter((i) => !check(i));
    if (bad.length) { bad[0].focus(); return; }

    const name = form.elements.firstName.value.trim();
    submit.disabled = true;
    status.classList.remove('is-error');
    status.textContent = 'Sending...';
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      if (!res.ok) throw new Error(String(res.status));
      form.innerHTML = `<div class="sent" role="status" tabindex="-1">
        <span class="gallop" aria-hidden="true"></span>
        <h2 class="h3">Got it. Thanks, ${escapeHtml(name)}.</h2>
        <p>We'll be in touch soon. In the meantime, see what we've been making on <a class="link" href="https://www.instagram.com/inspirecampaigns/" target="_blank" rel="noopener">Instagram</a>.</p>
      </div>`;
      $('.sent', form).focus();
    } catch {
      submit.disabled = false;
      status.classList.add('is-error');
      status.innerHTML = 'That didn\'t send. Please try again, or message us on <a class="link" href="https://www.instagram.com/inspirecampaigns/" target="_blank" rel="noopener">Instagram</a>.';
    }
  });
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
