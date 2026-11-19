/* The starting page, "How Link works", and its progress tracker (decision D55).
 *
 * A first visit lands here instead of on a blank form: what Link is, where everything is kept, how sample answers work,
 * three concrete ways in for "I don't know where to start", and why Link asks each question. The tracker shows four
 * stages, filled only by real records (the server counts them; samples and the tour never do). The tour's own tracker
 * is drawn dashed and labelled as practice, so the two can't be mistaken for each other.
 *
 * Motion follows the transitions.dev tokens: progress grows on transform only, a finished stage draws its check, the
 * percentage swaps with a short rise. Everything is skipped when the system asks for reduced motion.
 * All text is set as text, never as HTML.
 */
(function () {
  'use strict';
  const SVG = 'http://www.w3.org/2000/svg';
  const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const EASE_MOVE = 'cubic-bezier(0.645, 0.045, 0.355, 1)';  // ease-in-out: an on-screen bar changing size
  const EASE_OUT = 'cubic-bezier(0.22, 1, 0.36, 1)';
  const STAGE_SHORT = { start: 'Start here', groundwork: 'Groundwork', people: 'People & notes', outreach: 'Reaching out' };

  window.LinkStart = {
    create({ h, btn, api, act, S, go, here, orbSvg, workflows, guide, tip, store, walkthrough }) {
      const sv = (tag, attrs) => { const el = document.createElementNS(SVG, tag); for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v); return el; };
      function check() {
        const svg = sv('svg', { viewBox: '0 0 16 16', width: '12', height: '12', 'aria-hidden': 'true', class: 'journey-check' });
        svg.append(sv('path', { d: 'M3.5 8.5l3 3 6-7', fill: 'none' }));
        return svg;
      }
      const seenKey = 'journeySeen';
      const seen = () => { const v = store.get(seenKey, null); return Array.isArray(v) ? v : null; };

      // ---- the tracker ---------------------------------------------------------------------------------------
      // j: {stages:[{id,title,detail,done}], done, total, percent, current, complete}. opts.tour draws the practice version.
      function tracker(j, opts = {}) {
        const tour = !!opts.tour, compact = !!opts.compact;
        const total = j.stages.length, at = j.stages.findIndex((s) => s.id === j.current);
        const pct = j.percent;
        // The tour counts parts, not stages, so its tracker can't be read as real progress.
        const where = j.complete ? (tour ? 'Tour complete' : 'All ' + total + ' stages done')
          : (tour ? 'Part ' : 'Stage ') + (at + 1) + ' of ' + total + ': ' + j.stages[at].title;
        const title = tour ? 'Tour progress' : 'How far you’ve come';
        const pctEl = h('span', { class: 'journey-pct', text: pct + '%' });
        const fillEl = h('span', { class: 'journey-fill' });
        fillEl.style.transform = 'scaleX(' + (pct / 100) + ')';
        const bar = h('div', { class: 'journey-bar', role: 'progressbar', 'aria-label': title, 'aria-valuemin': '0', 'aria-valuemax': '100',
          'aria-valuenow': String(pct), 'aria-valuetext': pct + ' percent. ' + where + '.' }, fillEl);
        const list = h('ol', { class: 'journey-stages' }, j.stages.map((s, i) => {
          const state = s.done ? 'is-done' : s.id === j.current ? 'is-current' : 'is-next';
          const said = s.done ? (tour ? 'seen' : 'done') : s.id === j.current ? (tour ? 'showing now' : 'you are here') : (tour ? 'coming up' : 'not yet');
          return h('li', { class: 'journey-stage ' + state, 'data-stage': s.id, 'aria-current': s.id === j.current ? 'step' : null },
            h('span', { class: 'journey-dot', 'aria-hidden': 'true' }, s.done ? check() : h('span', { text: String(i + 1) })),
            h('span', { class: 'journey-name' }, h('span', { text: compact ? STAGE_SHORT[s.id] || s.title : s.title }),
              h('span', { class: 'sr', text: ', ' + said })));
        }));
        const head = h('div', { class: 'journey-head' },
          h('h2', { class: 'journey-title', id: opts.id ? opts.id + '-title' : null, text: title }),
          h('p', { class: 'journey-meta' }, pctEl, h('span', { 'aria-hidden': 'true', text: ' · ' }), h('span', { class: 'journey-where', text: where })));
        const parts = [head, bar, list];
        if (tour) parts.push(h('p', { class: 'journey-note', text: 'Practice only: your real progress doesn’t change.' }));
        else if (!compact && !j.complete) {
          const stage = j.stages[at];
          parts.push(h('p', { class: 'journey-next' }, h('strong', { text: 'Up next: ' }), stage.detail, ' ', nextLink(stage.id)));
        } else if (!compact && j.complete) parts.push(h('p', { class: 'journey-next', text: 'You’ve tried every part of Link. Keep going at your own pace.' }));
        if (compact && !tour) parts.push(h('a', { class: 'journey-more', href: '#start', text: 'How Link works' }));
        const el = h('section', { class: 'journey' + (tour ? ' is-tour' : '') + (compact ? ' is-compact' : ''), 'data-tour': tour ? null : 'journey',
          'aria-labelledby': opts.id ? opts.id + '-title' : null, 'aria-label': opts.id ? null : title }, parts);
        el.journeyParts = { fillEl, pctEl, list };
        return el;
      }
      function nextLink(id) {
        const to = { start: null, groundwork: ['me', 'Open About me'], people: ['add', 'Add a person'], outreach: ['connect', 'Reach out to someone'] }[id];
        if (!to) return null;
        return h('a', { href: '#' + to[0], class: 'journey-go', text: to[1] + ' →' });
      }

      // Pages are built off-screen and attached once their data has loaded, so wait until the tracker is on the page.
      function whenShown(el, fn, tries = 0) {
        if (el.isConnected) { requestAnimationFrame(() => fn()); return; }
        if (tries < 120) requestAnimationFrame(() => whenShown(el, fn, tries + 1));
      }
      // Animate from what this viewer last saw to what is true now, then remember it. Real progress only.
      function celebrate(el, j) {
        const before = seen();
        store.set(seenKey, j.stages.filter((s) => s.done).map((s) => s.id));
        if (!before) return;  // first sight: nothing to compare with
        const fresh = j.stages.filter((s) => s.done && !before.includes(s.id));
        const lost = before.filter((id) => !j.stages.some((s) => s.id === id && s.done));
        if (!fresh.length && !lost.length) return;
        const fromPct = Math.round(100 * before.filter((id) => j.stages.some((s) => s.id === id)).length / j.stages.length);
        if (fresh.length) {
          const names = fresh.map((s) => s.title).join(', ');
          const said = (fresh.length === 1 ? 'Stage done: ' : 'Stages done: ') + names + '. ' + (j.complete ? 'That’s all four.' : 'You’re ' + j.percent + '% of the way.');
          if (!tip('journey-' + fresh.map((s) => s.id).join('-'), said, 'confirm')) {
            const live = document.getElementById('sprite-live'); if (live) live.textContent = said;
          }
        }
        if (reduced()) return;
        const { fillEl, pctEl, list } = el.journeyParts;
        fillEl.animate([{ transform: 'scaleX(' + fromPct / 100 + ')' }, { transform: 'scaleX(' + j.percent / 100 + ')' }],
          { duration: 600, easing: EASE_MOVE, fill: 'backwards', delay: 150 });
        pctEl.animate([{ opacity: 0, transform: 'translateY(6px)', filter: 'blur(2px)' }, { opacity: 1, transform: 'translateY(0)', filter: 'blur(0)' }],
          { duration: 250, easing: EASE_OUT, fill: 'backwards', delay: 450 });
        for (const s of fresh) {
          const li = list.querySelector('[data-stage="' + s.id + '"]');
          if (li) li.classList.add('just-done');  // CSS draws the check and settles the dot
        }
      }

      // ---- the page ------------------------------------------------------------------------------------------
      let focusWhere = false;
      async function enter(then) {
        if (!S.onboarding.done) {  // leaving the welcome finishes the first stage, for real
          const out = await act(() => api('POST', '/api/journey/oriented', {}));
          if (!out) return;
          S.onboarding.done = true; S.journey = out;
          document.body.classList.remove('onboarding');
        }
        then();
      }
      const skipToApp = () => enter(() => {
        go('today');
        setTimeout(() => tip('skip-nudge', 'Want to add your first person? Open Add, then Add a person. It takes about a minute.', 'handoff'), 900);
      });
      const startTour = () => walkthrough().start();

      function trust() {
        const line = (text) => h('li', {}, h('span', { class: 'start-tick', 'aria-hidden': 'true' }), h('span', { text }));
        return h('ul', { class: 'start-trust', 'data-tour': 'start-trust' },
          line(here('Everything you add stays on this computer.', 'Everything you add stays in your account. Delete everything removes it.')),
          line('Link never contacts anyone. You decide what to keep and what to send.'),
          line('Most questions are optional. A name and one detail is enough to start.'));
      }
      function where() {
        const card = (key, title, text, actions, extra) => h('article', { class: 'start-path', 'data-tour': 'where-' + key, 'aria-labelledby': 'where-' + key + '-title' },
          h('h3', { id: 'where-' + key + '-title', text: title }), h('p', { text }), h('div', { class: 'start-path-actions' }, actions), extra || []);
        const to = (label, tab, cls, before) => btn(label, () => enter(() => { if (before) before(); go(tab); }), cls || '');
        return h('section', { class: 'start-where', 'aria-labelledby': 'start-where-title', 'data-tour': 'start-where' },
          h('h2', { id: 'start-where-title', tabindex: '-1', text: 'Not sure where to start?' }),
          h('p', { class: 'start-sub', text: 'Pick the one that sounds most like you. You can always come back here.' }),
          card('met', 'I met or noticed someone recently, and I don’t want to forget them.',
            'Start with them. Add a person walks you through it one question at a time. Add a note is for quick fragments, like what you talked about.',
            [to('Add a person', 'add', 'primary', () => { S.guideFirst = true; }), to('Add a note', 'quicklog', 'quiet')]),
          card('none', 'I don’t have a specific person in mind yet.',
            'Start with a little groundwork, so Link’s suggestions fit you. One or two lines is plenty. You don’t need to fill out every page.',
            [to('About me', 'me'), to('What I’ve done', 'evidence'), to('Jobs I’m looking at', 'roles')],
            [h('p', { class: 'start-path-more' }, 'Or let Link suggest a place to begin: ',
              btn('Explore ideas with Link', () => enter(() => workflows.open({ mode: 'starting' })), 'quiet start-inline')),
            h('p', { class: 'start-path-more' }, 'Already added someone? Check ',
              btn('People', () => enter(() => go('people')), 'quiet start-inline'), ' or ',
              btn('Today', () => enter(() => go('today')), 'quiet start-inline'))]),
          card('see', 'I want to see the whole thing first.',
            'Watch Link walk through every step with a practice person: groundwork, people and notes, then reaching out. Nothing is saved.',
            [btn('Start the walkthrough', startTour, 'primary')]));
      }
      function samples() {
        const mode = S.ai && S.ai.available ? S.ai.mode : 'off';
        const text = mode === 'live'
          ? 'Link’s AI is on. When you ask for a next step, what you type is sent to Link’s AI provider to write a suggestion. Check it before you save.'
          : mode === 'mock'
            ? 'Link’s AI isn’t switched on in this version. When you ask for a next step, Link shows a sample answer instead of one written for you. That’s expected, not an error: it shows what a next step looks like and how saving works.'
            : 'Link’s AI is off right now. When you ask for a next step, Link shows a general guide instead of one written for you.';
        return h('section', { class: 'start-samples', 'aria-labelledby': 'start-samples-title', 'data-tour': 'start-samples' },
          h('h2', { id: 'start-samples-title', text: mode === 'live' ? 'About Link’s suggestions' : 'About sample answers' }),
          h('p', { text }),
          h('p', { class: 'start-sub', text: (mode === 'live' ? '' : 'Your people and notes save normally. ') + 'In the walkthrough, every answer is a practice answer.' }));
      }
      function why() {
        const item = (q, a) => h('div', { class: 'start-why-item' }, h('dt', { text: q }), h('dd', { text: a }));
        const group = (key, summary, items) => h('details', { class: 'start-why-group', 'data-tour': 'why-' + key },
          h('summary', {}, h('span', { text: summary })), h('dl', {}, items));
        return h('section', { class: 'start-why', 'aria-labelledby': 'start-why-title', 'data-tour': 'start-why' },
          h('h2', { id: 'start-why-title', text: 'Why Link asks what it asks' }),
          h('p', { class: 'start-sub', text: 'Every question has a reason, and most are optional. Open a group to see what each one is for.' }),
          group('add', 'When you add a person', [
            item('Who did you meet?', 'So you can find them again. A first name is enough.'),
            item('How do you know them?', 'Where you met makes a first message easier. “We met at the career fair” is a natural opener.'),
            item('What do you remember?', 'Fragments are fine. Only you see this, and it helps you pick up where you left off.'),
            item('What’s one small next step?', 'Small and specific is easier to actually do. Link reminds you on Today, so you don’t have to keep it in your head.')]),
          group('reach', 'When you reach out (Add more detail · Optional)', [
            item('Why them, or why there?', 'A real reason makes reaching out feel natural, not random. For example: “She leads the data club I want to join.”'),
            item('What do you hope to get out of it?', 'Knowing your aim keeps the next step small and right-sized. This stays private: it never goes into a message.'),
            item('Anything you’re happy to mention to them', 'This is the only background Link may put in a message it drafts for you. Leave it empty if you’d rather add details yourself.'),
            item('Something you made that you’d be glad to share', 'Optional. A class project, a post or a sketch counts. You don’t need a polished portfolio.')]),
          group('ground', 'Groundwork pages', [
            item('About me', 'Your goals and how you like to work, so Link’s suggestions fit you. Only you see them.'),
            item('What I’ve done', 'Real things you’ve done, like a class project or a club role. A message only mentions what you choose, so it stays true.'),
            item('Jobs I’m looking at', 'Roles you’re curious about, so you can compare them with what you’ve done.'),
            item('Things I pasted and My messages', 'These fill in as you go: text you paste in, and messages Link helped you write.')]));
      }
      function ctas(id) {
        const welcome = !S.onboarding.done;
        const skip = btn(welcome ? 'Skip to the app' : 'Go to Today', skipToApp, 'quiet start-skip');
        skip.setAttribute('aria-describedby', id + '-skip-note');
        return h('div', { class: 'start-cta' },
          h('div', { class: 'start-cta-row' }, btn('Show me how it works', startTour, 'primary big start-tour'), skip),
          h('p', { id: id + '-skip-note', class: 'start-cta-note',
            text: 'The walkthrough takes about 3 minutes and uses a practice person, so nothing is saved. Pause, go back or skip anytime. '
              + (welcome ? 'Skip goes to Today, your home screen.' : 'Replay it later from Menu, then Take the tour.') }));
      }
      async function render(root, opts = {}) {
        const welcome = !!opts.welcome;
        if (!S.journey) { try { S.journey = await api('GET', '/api/journey'); } catch (e) { /* the page still explains Link without it */ } }
        const j = S.journey;
        const track = j ? tracker(j, { id: 'start-journey' }) : null;
        const page = h('section', { class: 'page start-page' + (welcome ? ' is-welcome' : ''), 'aria-labelledby': 'start-title' },
          welcome ? h('div', { class: 'connect-brand' }, h('span', { class: 'orb is-ready' }, orbSvg(36)), h('span', { text: 'Link' })) : null,
          h('header', { class: 'start-intro', 'data-tour': 'start-intro' },
            h('p', { class: 'eyebrow', text: 'How Link works' }),
            h('h1', { id: 'start-title', tabindex: '-1', text: welcome ? 'Welcome to Link.' : 'How Link works.' }),
            h('p', { class: 'start-lede', text: 'Link is a calm place to remember the people you meet, keep what you talked about, and figure out one small, low-pressure next step.' }),
            trust()),
          track, ctas('start-top'), where(), samples(), why(),
          h('div', { class: 'start-end' }, h('h2', { text: 'Ready when you are.' }), ctas('start-end')),
          S.demo ? h('p', { class: 'connect-demo', text: 'Demo with sample people' }) : null);
        root.append(page);
        if (track && !welcome) whenShown(track, () => celebrate(track, j));
        else if (track) store.set(seenKey, j.stages.filter((s) => s.done).map((s) => s.id));
        if (focusWhere) {
          focusWhere = false;
          requestAnimationFrame(() => { const t = document.getElementById('start-where-title'); if (t) { t.scrollIntoView({ block: 'start', behavior: reduced() ? 'auto' : 'smooth' }); t.focus({ preventScroll: true }); } });
        }
      }
      // Today's one-line version, shown until every stage is done (and once more to mark the finish).
      function compact(j) {
        const before = seen();
        if (j.complete && before && before.length === j.stages.length) return null;
        const el = tracker(j, { compact: true });
        whenShown(el, () => celebrate(el, j));
        return el;
      }
      return { render, tracker, compact, showWhere: () => { focusWhere = true; go('start'); } };
    }
  };
})();
