/* The agent-guided walkthrough (decision D55).
 *
 * Link walks through the real app, start to finish, with a practice person. Pattern from embedded-uiux-walkthrough:
 * real components rather than screenshots, demo-only data, a no-write sandbox, a pointer that moves and clicks, a
 * spotlight on each target, typed narration, and stable data-tour hooks. While it runs:
 *   - every request goes through request() below. Nothing but a read ever reaches the server, lists show only the
 *     practice person, and saves are answered here, in memory. Leaving the tour reloads the page, so nothing from it
 *     can linger in memory either;
 *   - the page is inert: clicks, typing and screen readers stay in the tour card, and only the agent acts on the page;
 *   - Back, Next, Pause/Play, Replay this step and Skip to the app always work, so nobody waits on the typing.
 * Motion follows web-animation-design: ease-in-out for the pointer moving across the screen, ease-out for things
 * entering, under 300 ms for interface changes, and all of it off when the system asks for reduced motion (then the
 * text appears at once and Play is off, so nothing advances on its own).
 * All text is set as text, never as HTML.
 */
(function () {
  'use strict';
  const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const EASE_MOVE = 'cubic-bezier(0.645, 0.045, 0.355, 1)';
  const EASE_OUT = 'cubic-bezier(0.22, 1, 0.36, 1)';
  const CHAPTERS = [['start', 'Start here'], ['groundwork', 'Groundwork'], ['people', 'People & notes'], ['outreach', 'Reaching out']];
  const PRACTICE = { id: -101, name: 'Maya Chen', org: 'Campus Data Club' };
  class Cancel extends Error {}
  const frame = () => new Promise((resolve) => requestAnimationFrame(() => resolve()));
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const iso = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');

  window.LinkWalkthrough = {
    create({ h, btn, S, go, here, orbSvg, tracker, hooks }) {
      let run = null;  // the tour in progress: {i, token, playing, origin, sandbox, ...}
      let ui = null;   // the overlay's parts

      // ---- the sandbox: what the app's requests get while the tour runs -----------------------------------------
      const EMPTY = new Set(['/api/ideas', '/api/checkins', '/api/connections/follow-ups', '/api/encounters', '/api/email-contacts',
        '/api/proposals', '/api/logs', '/api/memory', '/api/evidence', '/api/imports', '/api/drafts', '/api/actions']);
      const person = () => ({ id: PRACTICE.id, name: PRACTICE.name, org: PRACTICE.org, context: 'Met at a club or event', notes: '', category: '',
        next_action: { title: 'Send a thank-you note' }, last_interaction: null, is_sample: 1 });
      const step = () => ({ id: -201, item_id: PRACTICE.id, kind: 'follow_up', title: 'Send Maya a thank-you note', state: 'suggested', commitment: 1,
        importance: 2, effort_min: 10, deadline: null, where_left_off: 'Not started.', is_sample: 1 });
      function samplePlan(inputs) {
        return { id: -401, item_id: inputs.item_id || null, mode: inputs.mode || 'reconnect', status: 'pending', source: 'tour', inputs: { ...inputs },
          result: {}, unavailable_reason: '', created_at: '', updated_at: '',
          payload: { acknowledgment: 'Maya leads a club you want to join, so you already have a genuine reason to talk.', suggested_name: '',
            purpose: 'Ask Maya how to get involved with the data club.',
            reason: 'You share a real interest, and a small, specific question is easy for her to answer.',
            opening: '', closing: '', clarification: '',
            questions: ['What does a new member usually help with first?', 'Which workshop would you suggest for someone learning SQL?'],
            next_step: 'Send Maya a short note asking how to join the spring showcase team.',
            uncertainties: ['You don’t know yet how much time the showcase takes.'],
            considerations: ['Keep it short and give her an easy way to say no.'] } };
      }
      const blocked = () => { const e = new Error('Not saved. This is the tour, so nothing is saved.'); e.status = 409; return e; };
      // Called by the app's api() for every request while the tour runs. send() is the real network call.
      async function request(method, path, body, send) {
        const url = new URL(path, window.location.origin), p = url.pathname, box = run ? run.sandbox : { added: true };
        if (method === 'GET') {
          if (p === '/api/bootstrap') { const b = await send('GET', path); return { ...b, onboarding: { ...b.onboarding, done: true } }; }
          if (p === '/api/people') return box.added ? [person()] : [];
          if (p === '/api/items') return box.added ? [{ id: PRACTICE.id, kind: 'relationship', title: PRACTICE.name, org: PRACTICE.org, status: 'active', is_sample: 1 }] : [];
          if (p === '/api/today') {
            return { minutes: S.minutes || 20, greeting: '', days_away: null, session: null, today: iso(new Date()), reminders: [], parked_ideas: 0, alternatives: [],
              recommended: box.added ? { action: step(), item: { id: PRACTICE.id, title: PRACTICE.name, org: PRACTICE.org },
                reasons: ['You picked this step when you added Maya.', 'It takes about 10 minutes.'] } : null };
          }
          if (p === '/api/workspace/quicklog') return {};
          if (EMPTY.has(p) || p.startsWith('/api/connections/plans')) return [];
          return send(method, path);  // other reads are harmless: they change nothing
        }
        // Nothing below ever reaches the server.
        if (p === '/api/guide/connection' && method === 'POST') {
          await sleep(520);  // long enough for the save feedback to show, as it would for real
          box.added = true;
          const remind = body.next_step && body.remind_in_days ? iso(new Date(Date.now() + body.remind_in_days * 86400000)) : null;
          return { person: { id: PRACTICE.id, name: body.name || PRACTICE.name, org: body.org || '' }, logged: !!(body.memory || body.context),
            next_step: body.next_step || null, remind_on: remind };
        }
        if (p === '/api/connections/plans' && method === 'POST') { await sleep(650); return samplePlan(body || {}); }
        if (/^\/api\/connections\/plans\/-?\d+\/confirm$/.test(p)) return { item_id: PRACTICE.id, log_id: null, action_id: -201 };
        if (p === '/api/workspace/quicklog') return {};
        throw blocked();
      }

      // ---- finding things, moving the pointer, typing ------------------------------------------------------------
      const $ = (sel) => document.querySelector(sel);
      // Inside a closed <details> an element can still report a box, so a closed section counts as hidden (its summary doesn't).
      const folded = (el) => { const d = el.parentElement && el.parentElement.closest('details:not([open])'); return !!d && !d.querySelector(':scope > summary').contains(el); };
      const visible = (el) => !!el && el.isConnected && el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden' && !folded(el);
      const first = (sels) => { for (const s of [].concat(sels)) { const el = typeof s === 'function' ? s() : $(s); if (visible(el)) return el; } return null; };
      function context(token) {
        const alive = () => !!run && run.token === token;
        const check = () => { if (!alive()) throw new Cancel(); };
        const ctx = {
          alive, check,
          async wait(ms) { await sleep(ms); check(); },
          async settle(promise) { try { await promise; } catch (e) { /* a cancelled animation */ } check(); },
          async find(sels, ms = 5000) {
            const until = performance.now() + ms;
            for (;;) { const el = first(sels); if (el) return el; if (performance.now() > until) return null; await frame(); check(); }
          },
          async visit(tab, fresh) {
            if (!fresh && S.tab === tab && window.location.hash === '#' + tab && $('#main .page')) return;
            const done = rendered(tab);
            go(tab);
            await done; check();
          },
          async still(el) {  // a section that is opening or a page that is still drawing moves for a few frames
            let last = null;
            for (let n = 0; n < 30; n++) {
              const top = Math.round(el.getBoundingClientRect().top), ht = Math.round(el.getBoundingClientRect().height);
              if (last && last[0] === top && last[1] === ht) return;
              last = [top, ht];
              await frame(); check();
            }
          },
          async bring(el, retry) {  // scroll a target into the part of the screen the card doesn't cover
            const scroller = scrollParent(el);
            const r = el.getBoundingClientRect(), phone = innerWidth < 640;
            // Already in plain view (on a phone, above the card's half of the screen): leave the page where it is.
            if (r.top >= 56 && r.bottom <= (phone ? innerHeight * 0.5 : innerHeight - 40)) return;
            const aim = phone ? innerHeight * 0.12 : Math.max(24, (innerHeight - Math.min(r.height, innerHeight * 0.6)) / 2);
            const delta = r.top - aim;
            if (Math.abs(delta) < 8) return;
            // The app scrolls inside its sheet on wide screens and scrolls the whole page on phones.
            (scroller || window).scrollBy({ top: delta, behavior: reduced() ? 'auto' : 'smooth' });
            await ctx.wait(reduced() ? 30 : 380);
            const again = el.getBoundingClientRect();
            if (!retry && (again.top < 0 || again.top > innerHeight * 0.7)) await ctx.bring(el, true);  // the page was still growing
          },
          async point(el, where) {
            const r = el.getBoundingClientRect();
            const x = where === 'start' ? r.left + Math.min(30, r.width / 2) : r.left + r.width / 2;
            const y = r.top + Math.min(r.height / 2, 24);
            await moveCursor(ctx, x, y);
            return { x, y };
          },
          async tap(el) {
            if (!el) return;
            await ctx.bring(el);
            const at = await ctx.point(el);
            pulse(at.x, at.y);
            await ctx.wait(reduced() ? 0 : 140);
            el.click();  // the page is inert to people; the agent's click is a script call
            await ctx.wait(reduced() ? 60 : 260);
          },
          async write(el, text) {
            if (!el) return;
            if (el.value === text) return;
            await ctx.bring(el);
            const at = await ctx.point(el, 'start');
            pulse(at.x, at.y);
            const fire = () => el.dispatchEvent(new Event('input', { bubbles: true }));
            if (reduced()) { el.value = text; fire(); return; }
            el.value = ''; fire();
            for (const ch of text) { el.value += ch; fire(); await ctx.wait(ch === ' ' ? 30 : 18 + Math.round(Math.random() * 22)); }
          },
        };
        return ctx;
      }
      // The nearest ancestor that scrolls: the app's sheet on wide screens, or none on phones, where the whole page scrolls.
      // The sheet counts even before it overflows, since a section that just opened may not have grown it yet.
      function scrollParent(el) {
        const pageScrolls = document.scrollingElement.scrollHeight > innerHeight + 2;
        for (let n = el.parentElement; n && n !== document.body; n = n.parentElement) {
          if (!/(auto|scroll)/.test(getComputedStyle(n).overflowY)) continue;
          if (n.scrollHeight > n.clientHeight + 2 || (n.id === 'main' && !pageScrolls)) return n;
        }
        return null;
      }
      function rendered(tab, ms = 7000) {
        return new Promise((resolve) => {
          const done = () => { window.removeEventListener('link:rendered', on); clearTimeout(timer); resolve(); };
          const on = (e) => { if (!tab || !e.detail || e.detail.tab === tab) done(); };
          const timer = setTimeout(done, ms);
          window.addEventListener('link:rendered', on);
        });
      }
      let cur = { x: 0, y: 0 };
      async function moveCursor(ctx, x, y) {
        const c = ui.cursor;
        c.classList.add('is-on');
        if (reduced()) { c.style.transform = 'translate(' + x + 'px,' + y + 'px)'; cur = { x, y }; return; }
        const dist = Math.hypot(x - cur.x, y - cur.y);
        const anim = c.animate([{ transform: 'translate(' + cur.x + 'px,' + cur.y + 'px)' }, { transform: 'translate(' + x + 'px,' + y + 'px)' }],
          { duration: Math.round(Math.min(650, Math.max(240, dist * 0.55))), easing: EASE_MOVE, fill: 'forwards' });
        cur = { x, y };
        c.style.transform = 'translate(' + x + 'px,' + y + 'px)';
        await ctx.settle(anim.finished);
        anim.cancel();
      }
      function pulse(x, y) {
        if (reduced()) return;
        const p = h('span', { class: 'tour-pulse', 'aria-hidden': 'true' });
        p.style.left = x + 'px'; p.style.top = y + 'px';
        ui.layer.append(p);
        const a = p.animate([{ transform: 'translate(-50%,-50%) scale(.6)', opacity: 0.6 }, { transform: 'translate(-50%,-50%) scale(1.5)', opacity: 0 }],
          { duration: 420, easing: EASE_OUT });
        a.finished.then(() => p.remove(), () => p.remove());
      }

      // ---- the spotlight and the card's place ----------------------------------------------------------------------
      let target = null, placing = 0;
      function spot(el) {
        target = el;
        const s = ui.spot;
        if (!el) { s.classList.remove('is-on'); ui.shield.classList.add('is-dim'); return; }
        ui.shield.classList.remove('is-dim');
        const r = el.getBoundingClientRect(), pad = 6;
        const top = Math.max(6, r.top - pad), left = Math.max(6, r.left - pad);
        const bottom = Math.min(innerHeight - 6, r.bottom + pad), right = Math.min(innerWidth - 6, r.right + pad);
        s.style.transform = 'translate(' + left + 'px,' + top + 'px)';
        s.style.width = Math.max(0, right - left) + 'px';
        s.style.height = Math.max(0, bottom - top) + 'px';
        s.classList.add('is-on');
      }
      function place() {
        const card = ui.card, r = target ? target.getBoundingClientRect() : null;
        let at;
        if (innerWidth < 640) at = r && r.top + r.height / 2 > innerHeight * 0.5 && r.top > innerHeight * 0.45 ? 'top' : 'bottom';
        else {
          const w = card.offsetWidth, ht = card.offsetHeight, m = 24;
          const spots = [['bottom-left', m, innerHeight - ht - m], ['top-left', m, m], ['bottom-right', innerWidth - w - m, innerHeight - ht - m], ['top-right', innerWidth - w - m, m]];
          // The corner that covers the least of the target; ties keep the first, so the card doesn't hop around.
          const cover = (x, y) => !r ? 0 : Math.max(0, Math.min(x + w, r.right + 10) - Math.max(x, r.left - 10))
            * Math.max(0, Math.min(y + ht, r.bottom + 10) - Math.max(y, r.top - 10));
          at = spots.reduce((best, sp) => (cover(sp[1], sp[2]) < cover(best[1], best[2]) - 1 ? sp : best))[0];
        }
        if (card.dataset.at === at) return;
        const swap = () => { card.dataset.at = at; };
        if (reduced() || !card.dataset.at) { swap(); return; }
        const n = ++placing;  // a quick fade, so the card never slides across what it is pointing at
        card.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 110, easing: 'ease-out' }).finished.then(() => {
          if (n !== placing) return;
          swap();
          card.animate([{ opacity: 0, transform: 'scale(.98)' }, { opacity: 1, transform: 'scale(1)' }], { duration: 200, easing: EASE_OUT });
        }, () => {});
      }
      let follow = 0;
      function keepUp(e) {
        cancelAnimationFrame(follow);
        follow = requestAnimationFrame(() => { if (!run) return; if (target && target.isConnected) spot(target); if (e && e.type === 'resize') place(); });
      }

      // ---- the typed narration -------------------------------------------------------------------------------------
      let typeTimer = null, typeDone = null, typeFull = '';
      function typeText(text) {
        finishTyping();
        typeFull = text;
        ui.ghost.textContent = text;  // reserves the final height, so the card doesn't grow as it types
        if (reduced()) { ui.text.textContent = text; return Promise.resolve(); }
        ui.text.textContent = '';
        ui.card.classList.add('is-typing');
        return new Promise((resolve) => {
          typeDone = resolve;
          let i = 0;
          const tick = () => {
            i = Math.min(text.length, i + 1);
            ui.text.textContent = text.slice(0, i);
            if (i >= text.length) { finishTyping(); return; }
            typeTimer = setTimeout(tick, /[.,:;!?]/.test(text[i - 1]) ? 110 : 16);
          };
          typeTimer = setTimeout(tick, 140);
        });
      }
      function finishTyping() {
        clearTimeout(typeTimer); typeTimer = null;
        if (ui && typeFull) ui.text.textContent = typeFull;
        if (ui) ui.card.classList.remove('is-typing');
        if (typeDone) { const r = typeDone; typeDone = null; r(); }
      }

      // ---- the steps ----------------------------------------------------------------------------------------------
      const aiMode = () => (S.ai && S.ai.available ? S.ai.mode : 'off');
      // The practice person's answers. Each step sets the answers before it directly, so Back and Next can land on any
      // question; the step's own answer is cleared, so the agent can show it being given.
      const answers = { name: PRACTICE.name, org: PRACTICE.org, met: 'Met at a club or event', when: { kind: 'approx', text: 'this week' },
        memory: 'She runs the SQL workshops. Said the spring showcase needs volunteers.', next: 'Send a thank-you note', remind: 3 };
      const reach = { mode: 'reconnect', recollection: 'Maya Chen. She leads the data club, and I’d like to help with the spring showcase.',
        why_person: 'She runs the data club I want to join.', goal: 'Find a way to get involved this semester.',
        approved_context: 'I’m a sophomore studying data analytics.' };
      async function onGuide(ctx, stepNo, values) {
        await ctx.visit('add');
        await hooks.guidePrefill(values, stepNo);
        ctx.check();
      }
      async function onConnect(ctx, inputs, plan, open) {
        if (open) hooks.openDisc('connection-extra'); else hooks.closeDisc('connection-extra');
        const want = plan ? '#main .plan-story' : '#main .connect-form';
        if (!$(want)) { hooks.connectResume(inputs, plan); await rendered('connect'); ctx.check(); }
        const extra = $('#main [data-tour="more-detail"]');
        if (extra && extra.open !== !!open) extra.open = !!open;
      }
      const field = (key) => '#main [data-tour="field-' + key + '"]';
      const STEPS = [
        // 1. Start here
        { ch: 0, title: 'Hi, I’m Link.', go: 'start',
          text: () => 'I’ll show you how Link works, from start to finish. I’m using a practice person, so nothing you see is saved and nobody is contacted. Pause, go back or skip anytime.' },
        { ch: 0, title: 'What Link is for.', go: 'start', target: '#main [data-tour="start-intro"]',
          text: () => 'Link is a calm place to remember the people you meet, keep what you talked about, and find one small next step when you’re ready.' },
        { ch: 0, title: 'Where your information lives.', go: 'start', target: '#main [data-tour="start-trust"]',
          text: () => here('Everything you add stays on this computer.', 'Everything you add stays in your account, and Delete everything removes it.')
            + ' Link never contacts anyone for you. You decide what to keep and what to send.' },
        { ch: 0, title: 'How far you’ve come.', go: 'start', target: '#main [data-tour="journey"]',
          text: () => 'This bar shows four stages: getting started, groundwork, people and notes, then reaching out. It fills in as you use Link for real. The tour doesn’t count, so practice can’t fill it.' },
        { ch: 0, title: () => (aiMode() === 'live' ? 'About Link’s suggestions.' : 'Sample answers are expected.'), go: 'start', target: '#main [data-tour="start-samples"]',
          text: () => aiMode() === 'live' ? 'Link’s AI is on, so next steps are written from what you type. Always check a suggestion before you save it.'
            : aiMode() === 'mock' ? 'Link’s AI isn’t switched on in this version, so when you ask for a next step you’ll get a sample answer. It shows how the flow works. It isn’t an error, and it isn’t advice written for you.'
              : 'Link’s AI is off right now, so next steps come from a general guide instead of being written for you. Everything else works.' },
        { ch: 0, title: 'Not sure where to start?', go: 'start', target: ['#main [data-tour="where-met"]', '#main [data-tour="start-where"]'],
          text: () => 'Pick the starting point that sounds like you. Met someone? Start with them. No one in mind yet? Do a little groundwork first. Want to see everything? That’s this tour.' },
        { ch: 0, title: 'Every question has a reason.', go: 'start', target: '#main [data-tour="start-why"]',
          text: () => 'Most questions in Link are optional. This part of the page explains what each one is for. I’ll point out the important ones as we go.' },
        { ch: 0, title: 'That’s me, in the corner.', go: 'start', target: '#dock-pill',
          text: () => 'When you use Link, I sit in the corner. Tap me to ask a question or talk something through.'
            + (aiMode() === 'live' ? '' : aiMode() === 'mock' ? ' In this version my replies are samples too.' : ' Chat is off right now.') },
        // 2. Groundwork
        { ch: 1, title: 'Groundwork: About me.', go: 'me', target: '#main .page-head',
          text: () => 'About me holds your goals and how you like to work. Link uses your goals to suggest next steps that fit you. Only you see them.' },
        { ch: 1, title: 'What I’ve done.', go: 'evidence', target: '#main .page-head',
          text: () => 'This is for real things you’ve done, like a class project, a club role or a job. When Link helps you write a message, it only mentions what you choose, so everything stays true.' },
        { ch: 1, title: 'Jobs I’m looking at.', go: 'roles', target: '#main .page-head',
          text: () => 'Save roles you’re curious about here. Link can line a job posting up against what you’ve done, so you can see where you already fit.' },
        { ch: 1, title: 'You don’t have to fill everything in.', go: 'roles',
          target: () => first(['#more-menu[open] .menu-panel', '#mobile-more:not(.hidden)', '#more-menu > summary', '#mobile-more-button']),
          text: () => 'One or two lines on any of these pages is enough to start. Things I pasted and My messages fill in by themselves as you go. You’ll find all of them under Menu.',
          play: async (ctx) => {
            const menu = first(['#more-menu > summary', '#mobile-more-button']);
            if (menu && !first(['#more-menu[open] .menu-panel', '#mobile-more:not(.hidden)'])) await ctx.tap(menu);
            const panel = await ctx.find(['#more-menu[open] .menu-panel', '#mobile-more:not(.hidden)'], 1500);
            if (panel) spot(panel);
          } },
        // 3. People & notes
        { ch: 2, title: 'Add a person.', target: '#main .guide-stage',
          text: () => 'Add a person asks one question at a time. I’ll add a practice person, Maya. A first name is enough; everything else is optional.',
          enter: async (ctx) => { hooks.guideReset(); await ctx.visit('add', true); },
          play: async (ctx) => {
            await ctx.write(await ctx.find('#main .guide-stage input[aria-label="Their name"]'), answers.name);
            await ctx.write(await ctx.find('#main .guide-stage input[aria-label="Where they work or study (optional)"]'), answers.org);
          } },
        { ch: 2, title: 'Watch the preview.', target: '#main .guide-preview',
          text: () => 'As you answer, this card shows exactly what Link will save. Nothing is saved until you press Save at the end.',
          enter: (ctx) => onGuide(ctx, 0, { name: answers.name, org: answers.org }) },
        { ch: 2, title: 'How you met.', target: '#main .guide-stage',
          text: () => 'Where you met makes a first message easier to write. “We met at the data club” is a natural opener. Tapping an answer is enough.',
          enter: (ctx) => onGuide(ctx, 1, { name: answers.name, org: answers.org, met: '', when: null }),
          play: async (ctx) => {
            const chip = (label) => [...document.querySelectorAll('#main .guide-stage .guide-chip')].find((b) => b.textContent === label);
            if (chip('At a club or event')?.getAttribute('aria-pressed') !== 'true') await ctx.tap(chip('At a club or event'));
            if (chip('This week')?.getAttribute('aria-pressed') !== 'true') await ctx.tap(chip('This week'));
          } },
        { ch: 2, title: 'What you remember.', target: '#main .guide-stage',
          text: () => 'A few words now saves you from forgetting later. Fragments are fine, and only you see this.',
          enter: (ctx) => onGuide(ctx, 2, { name: answers.name, org: answers.org, met: answers.met, when: answers.when, memory: '' }),
          play: async (ctx) => { await ctx.write(await ctx.find('#main .guide-stage textarea'), answers.memory); } },
        { ch: 2, title: 'One small next step.', target: '#main .guide-stage',
          text: () => 'Pick one small, specific step. Link reminds you on Today, so you don’t have to keep it in your head.',
          enter: (ctx) => onGuide(ctx, 3, { name: answers.name, org: answers.org, met: answers.met, when: answers.when, memory: answers.memory, next: '', remind: 3 }),
          play: async (ctx) => {
            const chip = (label) => [...document.querySelectorAll('#main .guide-stage .guide-chip')].find((b) => b.textContent === label);
            if (chip(answers.next)?.getAttribute('aria-pressed') !== 'true') await ctx.tap(chip(answers.next));
            const later = await ctx.find(() => chip('In 3 days'), 1200);
            if (later && later.getAttribute('aria-pressed') !== 'true') await ctx.tap(later);
          } },
        { ch: 2, title: 'Check it, then save.', target: '#main .guide-stage',
          text: () => 'Here’s everything at once, so you can fix anything before saving. I’ll press Save now. Maya is a practice person, so nothing is actually stored.',
          enter: (ctx) => onGuide(ctx, 4, { name: answers.name, org: answers.org, met: answers.met, when: answers.when, memory: answers.memory, next: answers.next, remind: answers.remind }),
          play: async (ctx) => {
            await ctx.wait(reduced() ? 0 : 900);
            await ctx.tap(await ctx.find('#main .guide-save', 1500));
            const done = await ctx.find('#main .guide-done', 4000);
            if (done) spot(done);
          } },
        { ch: 2, title: 'Add a note.', go: 'quicklog', target: '#main .quicklog-page textarea',
          text: () => 'After a conversation, Add a note keeps the fragments, even half-remembered ones. You can link it to a person now or later.',
          enter: () => { run.sandbox.added = true; },
          play: async (ctx) => { await ctx.write(await ctx.find('#main .quicklog-page textarea'), 'Coffee chat with Maya. She suggested the Tableau workshop next month.'); } },
        { ch: 2, title: 'Add contacts.', go: 'sources', target: ['#main .source-tabs', '#main .source-hero'],
          text: () => 'Already know people? Add contacts brings them in from a LinkedIn export, your calendar or your email. It only reads, and you choose who to keep.' },
        { ch: 2, title: 'People.', go: 'people', target: ['#main .person-row', '#main .people-directory'],
          text: () => 'Everyone you keep lands in People. Open someone to see what you remember, your conversations, and their next step.',
          enter: () => { run.sandbox.added = true; hooks.clearPerson(); } },
        { ch: 2, title: 'Today is home.', go: 'today', target: ['#main #hero-title', '#main .hero', '#main .page'],
          text: () => 'Today shows one next step at a time, so you’re never facing a long list. Here’s the step picked for Maya. Done it? Mark it. Not today? Set it aside.',
          enter: () => { run.sandbox.added = true; } },
        // 4. Reaching out
        { ch: 3, title: 'Reaching out.', target: ['#main [data-tour="card-reconnect"]', '#main .connect-cards'],
          text: () => 'When you’re ready to contact someone, start here. Link helps you find one small, low-pressure next step. Nobody gets contacted.',
          enter: async (ctx) => { if (!$('#main .connect-cards')) { const done = rendered('connect'); hooks.connectBegin(); await done; ctx.check(); } },
          play: async (ctx) => { await ctx.wait(reduced() ? 0 : 700); await ctx.tap(await ctx.find('#main [data-tour="card-reconnect"]', 1500)); } },
        { ch: 3, title: 'Who, and why them?', target: '#main .connect-form > textarea',
          text: () => 'Start with who you’d like to reach out to and why. A name and one real reason is enough.',
          enter: (ctx) => onConnect(ctx, { mode: 'reconnect' }, null, false),
          play: async (ctx) => { await ctx.write(await ctx.find('#main .connect-form > textarea'), reach.recollection); } },
        { ch: 3, title: 'Add more detail is optional.', target: '#main [data-tour="more-detail"]',
          text: () => 'These four boxes are optional. Each one helps shape a better next step, and you can skip all of them. Here’s why Link asks each one.',
          enter: (ctx) => onConnect(ctx, { mode: 'reconnect', recollection: reach.recollection }, null, false),
          play: async (ctx) => {
            const extra = await ctx.find('#main [data-tour="more-detail"]');
            if (extra && !extra.open) await ctx.tap(extra.querySelector('summary'));
            if (extra) { await ctx.wait(reduced() ? 0 : 200); spot(extra); }
          } },
        { ch: 3, title: 'Why them, or why there?', target: field('why_person'),
          text: () => 'A real reason makes reaching out feel natural, not random. For example: “She leads the data club I want to join.”',
          enter: (ctx) => onConnect(ctx, { mode: 'reconnect', recollection: reach.recollection }, null, true),
          play: async (ctx) => { await ctx.write(await ctx.find(field('why_person') + ' textarea'), reach.why_person); } },
        { ch: 3, title: 'What do you hope to get out of it?', target: field('goal'),
          text: () => 'Knowing your aim keeps the next step small and right-sized. This one stays private: it never goes into a message.',
          enter: (ctx) => onConnect(ctx, { mode: 'reconnect', recollection: reach.recollection, why_person: reach.why_person }, null, true),
          play: async (ctx) => { await ctx.write(await ctx.find(field('goal') + ' textarea'), reach.goal); } },
        { ch: 3, title: 'Anything you’re happy to mention.', target: field('approved_context'),
          text: () => 'This is the only background Link may put in a message it drafts for you. Leave it empty if you’d rather add details yourself.',
          enter: (ctx) => onConnect(ctx, { mode: 'reconnect', recollection: reach.recollection, why_person: reach.why_person, goal: reach.goal }, null, true),
          play: async (ctx) => { await ctx.write(await ctx.find(field('approved_context') + ' textarea'), reach.approved_context); } },
        { ch: 3, title: 'Something you made.', target: field('example'),
          text: () => 'Optional. A class project, a post or a sketch counts. You don’t need a polished portfolio.',
          enter: (ctx) => onConnect(ctx, { ...reach }, null, true) },
        { ch: 3, title: 'Show me a next step.', target: '#main .connect-go',
          text: () => 'Now I’ll ask for a next step. Nothing is sent and nobody is contacted. This only shows you a suggestion.',
          enter: (ctx) => onConnect(ctx, { ...reach }, null, true),
          play: async (ctx) => {
            await ctx.wait(reduced() ? 0 : 600);
            await ctx.tap(await ctx.find('#main .connect-go', 1500));
            const story = await ctx.find('#main .plan-story', 5000);
            if (story) { await ctx.bring(story); spot(story); }
          } },
        { ch: 3, title: 'Here’s a possible next step.', target: '#main .plan-story',
          text: () => 'This practice answer shows the shape of a suggestion: why it fits, one small step, and questions you could ask. '
            + (aiMode() === 'live' ? 'With Link’s AI on, real answers are written from what you type. Check them before you save.'
              : 'In this version, Link’s real answers are samples too, not written for you.'),
          enter: (ctx) => onConnect(ctx, { ...reach }, samplePlan({ ...reach }), true) },
        { ch: 3, title: 'You decide what to keep.', target: ['#main .connect-save', '#main .plan-tools'],
          text: () => 'Nothing is saved until you press Save, and Link never sends anything. Change my answer goes back with your words kept. Back leaves without saving.',
          enter: (ctx) => onConnect(ctx, { ...reach }, samplePlan({ ...reach }), true) },
        { ch: 3, title: 'That’s the whole loop.', final: true,
          text: () => 'Groundwork, people and notes, then one small next step. Your real progress starts when you add something yourself. Where would you like to start?',
          enter: () => { spot(null); } },
      ];

      // ---- the card ---------------------------------------------------------------------------------------------
      function build() {
        const shield = h('div', { class: 'tour-shield' });
        shield.addEventListener('click', () => nudgeCard());
        const spotEl = h('div', { class: 'tour-spot', 'aria-hidden': 'true' });
        const NS = 'http://www.w3.org/2000/svg';
        const cursor = document.createElementNS(NS, 'svg');
        for (const [k, v] of Object.entries({ class: 'tour-cursor', viewBox: '0 0 24 24', width: '24', height: '24', 'aria-hidden': 'true' })) cursor.setAttribute(k, v);
        const arrow = document.createElementNS(NS, 'path');
        arrow.setAttribute('d', 'M4 2.5l15 9.2-6.6 1.5 3.9 7.3-2.6 1.4-3.9-7.3L5 19.6z');
        cursor.append(arrow);
        const title = h('h2', { id: 'tour-title', class: 'tour-title', tabindex: '-1' });
        const stepLabel = h('p', { class: 'tour-step' });
        const text = h('span', { class: 'tour-text-live', 'aria-hidden': 'true' });
        const ghost = h('span', { class: 'tour-text-ghost', 'aria-hidden': 'true' });
        const desc = h('p', { id: 'tour-desc', class: 'sr' });
        const live = h('p', { class: 'sr', 'aria-live': 'polite' });
        const timer = h('div', { class: 'tour-timer', 'aria-hidden': 'true' }, h('span', {}));
        const back = btn('Back', () => goTo(run.i - 1), 'quiet tour-back');
        const play = btn('Pause', () => setPlaying(!run.playing), 'tour-play');
        const replay = btn('Replay step', () => goTo(run.i), 'quiet tour-replay');
        const next = btn('Next', () => goTo(run.i + 1), 'primary tour-next');
        const controls = h('div', { class: 'tour-controls' }, back, play, replay, h('span', { class: 'grow' }), next);
        const finale = h('div', { class: 'tour-finale', hidden: true },
          btn('Add my first person', () => leave('add', true), 'primary'),
          btn('Back to How Link works', () => leave('start', false)),
          btn('Replay the tour', () => goTo(0), 'quiet'),
          btn('Back', () => goTo(run.i - 1), 'quiet'));
        const skip = btn('Skip to the app', () => leave('today', true), 'quiet tour-skip');
        const close = h('button', { type: 'button', class: 'tour-close', 'aria-label': 'Leave the tour and go to the app', onclick: () => leave('today', true) });
        close.append(h('span', { 'aria-hidden': 'true', text: '×' }));
        const trackSlot = h('div', { class: 'tour-track' });
        const card = h('section', { class: 'tour-card', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'tour-title', 'aria-describedby': 'tour-desc' },
          h('header', { class: 'tour-head' }, h('span', { class: 'orb is-ready tour-orb' }, orbSvg(32)),
            h('div', { class: 'tour-id' }, h('strong', { text: 'Link' }), h('span', { class: 'tour-chip', text: 'Practice tour · nothing is saved' })), close),
          trackSlot, stepLabel, title,
          h('p', { class: 'tour-text', onclick: () => finishTyping() }, ghost, text), desc, live, timer, controls, finale,
          h('div', { class: 'tour-foot' }, skip, h('span', { class: 'tour-keys', text: 'Esc leaves the tour' })));
        const layer = h('div', { class: 'tour-layer', id: 'tour-layer' }, shield, spotEl, cursor, card);
        document.body.append(layer);
        return { layer, shield, spot: spotEl, cursor, card, title, stepLabel, text, ghost, desc, live, timer, back, play, replay, next, controls, finale, trackSlot };
      }
      function nudgeCard() {
        if (reduced() || !ui) return;
        ui.card.animate([{ transform: 'translateX(0)' }, { transform: 'translateX(-5px)' }, { transform: 'translateX(4px)' }, { transform: 'translateX(0)' }],
          { duration: 260, easing: EASE_MOVE });
      }
      function paintTracker(i, before) {
        const ch = STEPS[i].ch, final = !!STEPS[i].final;
        const percent = Math.round(100 * i / (STEPS.length - 1));
        const j = { total: 4, percent, complete: final, current: final ? null : CHAPTERS[ch][0], done: final ? 4 : ch,
          stages: CHAPTERS.map(([id, title], n) => ({ id, title, detail: '', done: final || n < ch })) };
        const el = tracker(j, { tour: true, compact: true });
        ui.trackSlot.replaceChildren(el);
        if (reduced() || before == null || before === i) return;
        const was = Math.round(100 * before / (STEPS.length - 1));
        el.journeyParts.fillEl.animate([{ transform: 'scaleX(' + was / 100 + ')' }, { transform: 'scaleX(' + percent / 100 + ')' }], { duration: 400, easing: EASE_MOVE });
        if (STEPS[before].ch < ch || final) {
          const li = el.querySelector('[data-stage="' + CHAPTERS[STEPS[before].ch][0] + '"]');
          if (li) li.classList.add('just-done');
        }
      }
      function paint(i, before) {
        const s = STEPS[i], text = s.text(), title = typeof s.title === 'function' ? s.title() : s.title;
        paintTracker(i, before);
        ui.stepLabel.textContent = 'Step ' + (i + 1) + ' of ' + STEPS.length + ' · ' + CHAPTERS[s.ch][1];
        ui.title.textContent = title;
        ui.desc.textContent = text;
        ui.live.textContent = 'Step ' + (i + 1) + ' of ' + STEPS.length + '. ' + title + ' ' + text;
        ui.back.disabled = i === 0;
        ui.controls.hidden = !!s.final;
        ui.finale.hidden = !s.final;
        ui.play.textContent = run.playing ? 'Pause' : 'Play';
        ui.play.setAttribute('aria-label', run.playing ? 'Pause: stop moving on by itself' : 'Play: move on by itself');
        if (!reduced() && before != null && before !== i) {
          const dir = i > before ? 1 : -1;  // forward slides in from the right, back from the left (page side-by-side)
          for (const el of [ui.title, ui.stepLabel]) el.animate([{ opacity: 0, transform: 'translateX(' + 8 * dir + 'px)', filter: 'blur(3px)' },
            { opacity: 1, transform: 'translateX(0)', filter: 'blur(0)' }], { duration: 250, easing: EASE_OUT });
        }
        return typeText(text);
      }
      function setPlaying(on) {
        run.playing = on;
        ui.play.textContent = on ? 'Pause' : 'Play';
        ui.play.setAttribute('aria-label', on ? 'Pause: stop moving on by itself' : 'Play: move on by itself');
        if (!on) { finishTyping(); stopTimer(); ui.live.textContent = 'Paused. Choose Next when you’re ready.'; }
        else if (run.ready) schedule();
      }
      function stopTimer() {
        clearTimeout(run && run.autoTimer);
        if (ui && ui.timerAnim) { ui.timerAnim.cancel(); ui.timerAnim = null; }
      }
      function schedule() {
        stopTimer();
        const s = STEPS[run.i];
        if (!run.playing || s.final) return;
        const words = (s.text().match(/\S+/g) || []).length;
        const ms = Math.max(2600, words * 280 + 1400 - (run.typedFor || 0));
        if (!reduced()) ui.timerAnim = ui.timer.firstChild.animate([{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], { duration: ms, easing: 'linear', fill: 'forwards' });
        run.autoTimer = setTimeout(() => { if (run && run.playing) goTo(run.i + 1); }, ms);
      }
      async function goTo(i) {
        if (!run) return;
        if (i >= STEPS.length) return;
        i = Math.max(0, i);
        const before = run.i;
        run.i = i;
        const token = ++run.token, ctx = context(token);
        run.ready = false;
        ui.card.dataset.step = String(i); ui.card.dataset.ready = 'false';  // stable hooks for the browser checks
        stopTimer(); finishTyping();
        if (i !== before && document.activeElement && !ui.card.contains(document.activeElement)) ui.next.focus({ preventScroll: true });
        const s = STEPS[i];
        const started = performance.now();
        ui.cursor.classList.remove('is-on');  // the pointer shows only while the agent is doing something
        const typing = paint(i, before);
        try {
          hooks.closeMenus();
          if (s.go) await ctx.visit(s.go);
          if (s.enter) await s.enter(ctx);
          ctx.check();
          const el = s.target ? await ctx.find(s.target, 4000) : null;
          if (el) { await ctx.still(el); await ctx.bring(el); await ctx.still(el); }
          spot(el); place();
          await ctx.settle(typing);
          run.typedFor = performance.now() - started;
          if (s.play) { await ctx.wait(reduced() ? 0 : 250); await s.play(ctx); }
          ctx.check();
          run.ready = true; ui.card.dataset.ready = 'true';
          if (s.final) { ui.finale.querySelector('button').focus({ preventScroll: true }); return; }
          schedule();
        } catch (err) {
          if (!(err instanceof Cancel)) { console.error(err); if (run && run.token === token) { run.ready = true; ui.card.dataset.ready = 'true'; spot(null); place(); } }
        }
      }

      // ---- starting and leaving --------------------------------------------------------------------------------------
      let blockedNodes = [];
      const lateNodes = new MutationObserver((records) => {
        for (const r of records) for (const n of r.addedNodes) if (blockable(n)) { n.inert = true; blockedNodes.push(n); }
      });
      const blockable = (el) => el.nodeType === 1 && el.id !== 'tour-layer' && !['SCRIPT', 'STYLE', 'LINK', 'TEMPLATE'].includes(el.tagName)
        && !['toast', 'sprite-live'].includes(el.id) && !el.inert;
      function blockPage(on) {
        if (on) {
          blockedNodes = [...document.body.children].filter(blockable);
          blockedNodes.forEach((el) => { el.inert = true; });
          lateNodes.observe(document.body, { childList: true });
        } else { lateNodes.disconnect(); blockedNodes.forEach((el) => { el.inert = false; }); blockedNodes = []; }
      }
      function onKey(e) {
        if (!run) return;
        if (e.key === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); leave('today', true); return; }
        // Search (Cmd/Ctrl+K) would open on top of the tour; it waits until the tour ends.
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); e.stopImmediatePropagation(); return; }
        if (e.key !== 'Tab') return;
        // A modal card: Tab and Shift+Tab go round its own controls and never out to the inert page or the browser.
        const items = [...ui.card.querySelectorAll('button, [href]')].filter((el) => !el.disabled && el.offsetParent !== null);
        if (!items.length) return;
        const at = items.indexOf(document.activeElement);
        if (e.shiftKey && at <= 0) { e.preventDefault(); items[items.length - 1].focus(); }
        else if (!e.shiftKey && (at === -1 || at === items.length - 1)) { e.preventDefault(); items[0].focus(); }
      }
      async function start() {
        if (run) return;
        hooks.closeCompanion();
        await hooks.flushQuick();  // the person's own unfinished note is saved first, for real, before the sandbox starts
        hooks.resetQuick();
        run = { i: 0, token: 0, playing: !reduced(), instantWhenPaused: false, sandbox: { added: false }, welcome: !S.onboarding.done, ready: false };
        S.tour = { request };
        if (run.welcome) { S.onboarding = { ...S.onboarding, done: true }; document.body.classList.remove('onboarding'); }
        S.guideFirst = false;
        ui = build();
        blockPage(true);
        document.addEventListener('keydown', onKey, true);
        window.addEventListener('resize', keepUp);
        document.addEventListener('scroll', keepUp, true);
        cur = { x: innerWidth / 2, y: innerHeight - 60 };
        ui.cursor.style.transform = 'translate(' + cur.x + 'px,' + cur.y + 'px)';
        if (!reduced()) ui.card.animate([{ opacity: 0, transform: 'scale(.96)' }, { opacity: 1, transform: 'scale(1)' }], { duration: 250, easing: EASE_OUT });
        ui.card.dataset.at = innerWidth < 640 ? 'bottom' : 'bottom-left';
        ui.next.focus({ preventScroll: true });
        goTo(0);
      }
      // Leaving reloads the page: whatever the tour typed or "saved" lived only in this page's memory, and goes with it.
      async function leave(tab, oriented) {
        if (!run) return;
        const welcome = run.welcome;
        run.token += 1; stopTimer(); finishTyping();
        await hooks.flushQuick();  // a pending draft from the tour goes to the sandbox, which drops it
        hooks.resetQuick();
        run = null;
        S.tour = null;
        document.removeEventListener('keydown', onKey, true);
        window.removeEventListener('resize', keepUp);
        document.removeEventListener('scroll', keepUp, true);
        if (welcome && oriented) { try { await hooks.oriented(); } catch (e) { /* the welcome simply shows again */ } }
        hooks.reload(tab);
      }
      return { start, request, active: () => !!run, steps: () => STEPS.length };
    }
  };
})();
