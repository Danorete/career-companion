/* The step-by-step guide for adding a person (decision D52).
 *
 * One question per screen, a live preview of what will be saved, and visible feedback at every moment:
 * the preview fills in as you type, progress fills as you go, saving shows a spinner only if it takes long enough
 * to notice (over 0.4 s, per Nielsen Norman Group's response-time limits), and success is confirmed item by item.
 * All motion is skipped when the system asks for reduced motion. Text is always set as text, never as HTML.
 */
(function () {
  'use strict';
  const MET = [['At a career fair', 'Met at a career fair'], ['In class', 'Met in class'], ['At a club or event', 'Met at a club or event'],
    ['Over coffee', 'Met over coffee'], ['Online', 'Met online'], ['Through work', 'Met through work']];
  const WHEN = [['Today', { kind: 'today' }], ['Yesterday', { kind: 'yesterday' }], ['This week', { kind: 'approx', text: 'this week' }],
    ['A while ago', { kind: 'approx', text: 'a while ago' }], ['Not sure', { kind: 'unknown' }]];
  const STARTERS = ['They work on ', 'We talked about ', 'They suggested ', 'I want to remember '];
  const NEXT = ['Send a thank-you note', 'Connect on LinkedIn', 'Ask a follow-up question', 'Share something I promised'];
  const REMIND = [['Tomorrow', 1], ['In 3 days', 3], ['Next week', 7], ['No reminder', null]];
  const QUESTIONS = 4;
  const EASE = 'cubic-bezier(.22,1,.36,1)';
  const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const SVG = 'http://www.w3.org/2000/svg';
  const sv = (tag, attrs) => { const el = document.createElementNS(SVG, tag); for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v); return el; };

  window.LinkConnectionGuide = {
    create({ h, btn, field, api, S, go, orbSvg }) {
      let draft = null, step = 0, found = [], existing = [], busy = false, moving = false;
      let els = null;  // the live parts of the page: stage, preview rows, progress
      const blank = () => ({ name: '', org: '', met: '', metOther: '', when: null, memory: '', next: '', nextOther: '', remind: 3, source: null, sourceLabel: '' });
      const firstName = () => draft.name.trim().split(/\s+/)[0] || 'them';
      const context = () => {
        if (draft.met !== 'other') return draft.met;
        const own = draft.metOther.trim();
        return own ? (/^met\b/i.test(own) ? own : 'Met ' + own) : '';
      };
      const nextStep = () => (draft.next === 'other' ? draft.nextOther.trim() : draft.next);
      const whenLabel = () => (draft.when ? (WHEN.find(([, v]) => JSON.stringify(v) === JSON.stringify(draft.when)) || ['On ' + (draft.when.date || '')])[0] : '');
      const remindLabel = () => (REMIND.find(([, d]) => d === draft.remind) || [''])[0];
      const longDate = (iso) => { const d = new Date(iso + 'T12:00:00'); return isNaN(d) ? iso : d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' }); };

      function open(options = {}) {
        if (!draft || options.fresh) { draft = blank(); step = 0; }
        if (options.first) S.guideFirst = true;
        go('add');
      }

      async function suggestions() {
        const c = S.calendar || {}, m = c.email || {}, out = [];
        if (c.connected && c.waiting) {
          for (const e of await api('GET', '/api/encounters').catch(() => [])) {
            const past = e.starts_at && new Date(e.starts_at) < new Date();
            out.push({ kind: 'calendar', id: e.id, name: e.name, label: 'From your calendar · ' + (e.title || 'Meeting'),
              when: past ? { kind: 'date', date: e.starts_at.slice(0, 10) } : null });
          }
        }
        if (m.connected && m.waiting) {
          for (const x of await api('GET', '/api/email-contacts').catch(() => [])) {
            out.push({ kind: 'email', id: x.id, name: x.name || x.address.split('@')[0], label: 'You email each other', when: null });
          }
        }
        return out.slice(0, 6);
      }

      async function render(root) {
        // After a save the guide sits on its "saved" screen (step 5). Coming back later starts a new person; without
        // this, opening Add a person again from a menu tried to draw a sixth question and the page failed to load.
        if (!draft || step > QUESTIONS) { draft = blank(); step = 0; }
        [found, existing] = await Promise.all([suggestions(), api('GET', '/api/people').catch(() => [])]);
        root.append(page());
        show(step, 0);
      }

      // ---- the frame: header, progress, the question area and the live preview --------------------------
      function page() {
        const segments = Array.from({ length: QUESTIONS }, () => h('span', { class: 'guide-seg' }));
        const progress = h('div', { class: 'guide-progress', role: 'progressbar', 'aria-label': 'Progress', 'aria-valuemin': '0', 'aria-valuemax': String(QUESTIONS) }, segments);
        const stepLabel = h('span', { class: 'guide-step-label' });
        const eyebrow = h('span', { class: 'eyebrow' });
        const stage = h('div', { class: 'guide-stage' });
        const live = h('p', { class: 'sr', 'aria-live': 'polite' });
        const preview = previewCard();
        const headActions = h('div', { class: 'row guide-head-actions' }, btn('Start over', restart, 'quiet'), btn('Leave for now', () => go('today'), 'quiet'));
        els = { stage, progress, segments, stepLabel, eyebrow, live, headActions, ...preview.parts };
        return h('div', { class: 'page guide-page' },
          h('header', { class: 'guide-head' },
            h('div', { class: 'guide-title' }, eyebrow, stepLabel),
            progress,
            headActions),
          h('div', { class: 'guide-layout' }, stage, preview.el), live);
      }

      function previewCard() {
        const avatar = h('span', { class: 'guide-avatar', 'aria-hidden': 'true', text: '?' });
        const name = h('strong', { class: 'guide-preview-name', text: 'Their name' });
        const org = h('span', { class: 'guide-preview-org muted small' });
        const row = (label) => {
          const value = h('dd', { class: 'is-empty', text: 'Not yet' });
          return { el: h('div', { class: 'guide-fact' }, h('dt', { text: label }), value), value };
        };
        const met = row('How you met'), memory = row('What you remember'), next = row('Next step');
        const status = h('p', { class: 'guide-preview-status', role: 'status', text: 'Not saved yet' });
        const heading = h('span', { class: 'eyebrow', text: 'What Link will save' });
        const el = h('aside', { class: 'guide-preview', 'aria-label': 'What Link will save' }, heading,
          h('div', { class: 'guide-person' }, avatar, h('div', { class: 'guide-person-text' }, name, org)),
          h('dl', { class: 'guide-facts' }, met.el, memory.el, next.el), status);
        return { el, parts: { avatar, pName: name, pOrg: org, pMet: met, pMemory: memory, pNext: next, pStatus: status, pCard: el, pHeading: heading } };
      }

      // Flash a part of the preview so the person sees Link respond to what they just did.
      function flash(el) {
        el.classList.remove('is-updated');
        void el.offsetWidth;  // restart the animation
        el.classList.add('is-updated');
      }
      function setText(el, value, empty) {
        const shown = value || empty;
        if (el.textContent === shown) return;
        el.textContent = shown;
        el.classList.toggle('is-empty', !value);
        if (value) flash(el.closest('.guide-fact') || el);
      }
      function updatePreview() {
        if (!els) return;
        const name = draft.name.trim();
        const initials = name ? name.split(/\s+/).slice(0, 2).map((w) => w[0].toUpperCase()).join('') : '?';
        if (els.avatar.textContent !== initials) { els.avatar.textContent = initials; els.avatar.classList.toggle('is-set', !!name); if (name) flash(els.avatar); }
        setText(els.pName, name, 'Their name');
        setText(els.pOrg, draft.org.trim(), '');
        setText(els.pMet.value, [context(), whenLabel() && whenLabel() !== 'Not sure' ? whenLabel().toLowerCase() : ''].filter(Boolean).join(', '), 'Not yet');
        const memory = draft.memory.trim();
        setText(els.pMemory.value, memory.length > 140 ? memory.slice(0, 137) + '…' : memory, 'Not yet');
        const next = nextStep();
        setText(els.pNext.value, next ? next + (draft.remind != null ? ' · reminder ' + remindLabel().toLowerCase() : '') : '', 'Not yet');
      }

      function updateProgress() {
        const done = Math.min(step, QUESTIONS);
        els.segments.forEach((seg, i) => { seg.classList.toggle('is-done', i < done); seg.classList.toggle('is-now', i === done && step < QUESTIONS); });
        els.progress.setAttribute('aria-valuenow', String(done));
        els.eyebrow.textContent = S.guideFirst ? 'Your first person' : 'Add a person';
        els.stepLabel.textContent = step < QUESTIONS ? 'Step ' + (step + 1) + ' of ' + QUESTIONS + (step === 0 ? ' · about a minute' : '') : step === QUESTIONS ? 'Check and save' : 'Saved';
      }

      // ---- moving between steps ----------------------------------------------------------------------------
      function show(next, dir) {
        if (moving) return;
        step = next;
        const panel = [whoStep, metStep, rememberStep, nextStepStep, reviewStep][step]();
        els.headActions.hidden = false;
        if (els.pCard.classList.contains('is-saved')) {  // a new person after a save: the preview starts fresh
          els.pCard.classList.remove('is-saved'); els.pHeading.textContent = 'What Link will save'; els.pStatus.textContent = 'Not saved yet';
        }
        updateProgress();
        updatePreview();
        swap(panel, dir);
      }
      function swap(panel, dir) {
        const old = els.stage.firstElementChild;
        const settle = () => {
          moving = false;
          const heading = panel.querySelector('h2');
          // The first screen is built before it is attached to the page; focus and announce once it is.
          const land = () => { if (heading && heading.isConnected) heading.focus({ preventScroll: true });
            els.live.textContent = els.stepLabel.textContent + '. ' + (heading ? heading.textContent : ''); };
          if (heading && heading.isConnected) land(); else setTimeout(land, 0);
        };
        if (!old || !dir || reduced()) { els.stage.replaceChildren(panel); settle(); return; }
        moving = true;
        const out = old.animate([{ opacity: 1, transform: 'translateX(0)' }, { opacity: 0, transform: 'translateX(' + (-20 * dir) + 'px)' }],
          { duration: 150, easing: 'ease-in' });
        out.onfinish = () => {
          els.stage.replaceChildren(panel);
          panel.animate([{ opacity: 0, transform: 'translateX(' + (28 * dir) + 'px)' }, { opacity: 1, transform: 'translateX(0)' }], { duration: 280, easing: EASE });
          settle();
        };
      }
      function restart() { draft = blank(); show(0, -1); }

      // ---- building blocks ---------------------------------------------------------------------------------
      function agent(text, thinking) {
        return h('div', { class: 'guide-agent' }, h('span', { class: 'orb guide-orb ' + (thinking ? 'is-thinking' : 'is-ready') }, orbSvg(40)),
          h('p', { class: 'guide-say', text }));
      }
      function chips(label, options, isOn, choose) {
        const group = h('div', { class: 'guide-chips', role: 'group', 'aria-label': label });
        const sync = () => [...group.children].forEach((b, i) => b.setAttribute('aria-pressed', String(isOn(options[i]))));
        options.forEach((option) => group.append(h('button', { type: 'button', class: 'guide-chip', onclick: () => { choose(option); sync(); changed(); }, text: option[0] })));
        sync();
        return group;
      }
      let changed = () => {};
      function panel(id, say, question, hint, body, actions) {
        return h('section', { class: 'guide-panel', 'aria-labelledby': id }, agent(say),
          h('h2', { id, tabindex: '-1', text: question }), hint ? h('p', { class: 'guide-hint', text: hint }) : null,
          h('div', { class: 'guide-body' }, body), h('div', { class: 'guide-actions' }, actions));
      }
      function nav(primaryLabel, canGo, onGo, optional) {
        const back = step > 0 ? btn('Back', () => show(step - 1, -1), 'quiet') : null;
        const primary = btn(primaryLabel(), () => { if (canGo()) onGo(); }, 'primary guide-continue');
        const sync = () => { primary.disabled = !canGo(); primary.textContent = primaryLabel(); primary.classList.toggle('is-skip', !!optional && primaryLabel().startsWith('Skip')); };
        changed = () => { sync(); updatePreview(); };
        sync();
        return [back, h('span', { class: 'grow' }), primary];
      }
      const continueOnEnter = (go) => (e) => { if (e.key === 'Enter' && !e.isComposing) { e.preventDefault(); go(); } };

      // ---- the four questions ------------------------------------------------------------------------------
      function whoStep() {
        const name = h('input', { type: 'text', maxlength: 120, value: draft.name, 'aria-label': 'Their name', placeholder: 'For example: Priya Raman',
          oninput: (e) => { draft.name = e.target.value; dupe(); changed(); }, onkeydown: continueOnEnter(() => advance()) });
        const org = h('input', { type: 'text', maxlength: 200, value: draft.org, 'aria-label': 'Where they work or study (optional)', placeholder: 'For example: Deloitte, or your university',
          oninput: (e) => { draft.org = e.target.value; changed(); }, onkeydown: continueOnEnter(() => advance()) });
        const already = h('div', { class: 'guide-already', role: 'status' });
        const dupe = () => {
          const match = existing.find((p) => p.name.trim().toLowerCase() === draft.name.trim().toLowerCase());
          already.replaceChildren(...(match && !draft.source ? [h('p', { class: 'notice', text: 'You already have ' + match.name + ' in Link.' }),
            btn('Open ' + match.name, () => { S.selectedPerson = match.id; go('people'); }, 'quiet')] : []));
        };
        const source = h('div', { class: 'guide-source' });
        const showSource = () => { markPicked(); source.replaceChildren(...(draft.source ? [h('span', { class: 'guide-source-pill', text: 'Starting from: ' + draft.sourceLabel }),
          btn('Use a different person', () => { draft.source = null; draft.sourceLabel = ''; showSource(); dupe(); changed(); }, 'quiet')] : [])); };
        const picks = found.length ? h('div', { class: 'guide-found' }, h('p', { class: 'guide-found-title', text: 'People Link found' }),
          h('div', { class: 'guide-chips' }, found.map((f) => h('button', { type: 'button', class: 'guide-chip guide-found-chip',
            'aria-pressed': String(!!draft.source && draft.source.kind === f.kind && draft.source.id === f.id), onclick: () => {
            draft.source = { kind: f.kind, id: f.id }; draft.sourceLabel = f.label; draft.name = f.name; if (f.when) draft.when = f.when;
            name.value = f.name; showSource(); dupe(); changed(); name.focus();
          } }, h('strong', { text: f.name }), h('small', { text: f.label }))))) : null;
        const markPicked = () => picks && picks.querySelectorAll('.guide-found-chip').forEach((b, i) =>
          b.setAttribute('aria-pressed', String(!!draft.source && draft.source.kind === found[i].kind && draft.source.id === found[i].id)));
        showSource(); dupe();
        const advance = () => { if (draft.name.trim()) show(1, 1); };
        return panel('guide-q-who', S.guideFirst ? 'Let’s add your first person. It takes about a minute, and you can skip anything you don’t know.' : 'Let’s add someone. You can skip anything you don’t know.',
          'Who did you meet?', 'A first name is enough. You can change it later.',
          [picks, source, field('Their name', name), already, field('Where they work or study (optional)', org)],
          nav(() => 'Continue', () => !!draft.name.trim(), advance));
      }

      function metStep() {
        const other = h('input', { type: 'text', maxlength: 180, value: draft.metOther, 'aria-label': 'How you met, in your words', placeholder: 'For example: through my cousin',
          oninput: (e) => { draft.metOther = e.target.value; changed(); }, onkeydown: continueOnEnter(() => show(2, 1)) });
        const otherWrap = field('In your words', other);
        otherWrap.hidden = draft.met !== 'other';
        const how = chips('How you met', [...MET, ['Something else', 'other']], (o) => draft.met === o[1], (o) => {
          draft.met = draft.met === o[1] ? '' : o[1];
          otherWrap.hidden = draft.met !== 'other';
          if (draft.met === 'other') setTimeout(() => other.focus(), 0);
        });
        const when = chips('When', WHEN, (o) => JSON.stringify(draft.when) === JSON.stringify(o[1]), (o) => {
          draft.when = JSON.stringify(draft.when) === JSON.stringify(o[1]) ? null : o[1];
        });
        const answered = () => !!(context() || draft.when);
        return panel('guide-q-met', 'Nice. Knowing where you met makes the next message easier to write.', 'How do you know ' + firstName() + '?', null,
          [h('p', { class: 'guide-label', text: 'Where' }), how, otherWrap, h('p', { class: 'guide-label', text: 'When' }), when],
          nav(() => (answered() ? 'Continue' : 'Skip this'), () => true, () => show(2, 1), true));
      }

      function rememberStep() {
        const area = h('textarea', { rows: 4, maxlength: 2000, value: draft.memory, 'aria-label': 'What you remember',
          placeholder: 'What they do, what you talked about, anything they suggested…', oninput: (e) => { draft.memory = e.target.value; count(); changed(); } });
        const counter = h('span', { class: 'guide-count muted small' });
        const count = () => { const n = draft.memory.length; counter.textContent = n ? n + ' / 2000 · kept in this draft' : ''; };
        const starters = h('div', { class: 'guide-chips', role: 'group', 'aria-label': 'Sentence starters' }, STARTERS.map((s) => h('button', {
          type: 'button', class: 'guide-chip is-starter', text: s.trim() + '…', onclick: () => {
            draft.memory = (draft.memory.trim() ? draft.memory.trimEnd() + '\n' : '') + s;
            area.value = draft.memory; area.focus(); area.setSelectionRange(area.value.length, area.value.length); count(); changed();
          } })));
        count();
        return panel('guide-q-remember', 'A few words now saves you from forgetting later.', 'What do you remember about ' + firstName() + '?',
          'Short is fine. Only you see this.', [starters, area, counter],
          nav(() => (draft.memory.trim() ? 'Continue' : 'Skip this'), () => true, () => show(3, 1), true));
      }

      function nextStepStep() {
        const other = h('input', { type: 'text', maxlength: 200, value: draft.nextOther, 'aria-label': 'Your next step, in your words', placeholder: 'For example: send her the article',
          oninput: (e) => { draft.nextOther = e.target.value; changed(); remindWrap.hidden = !nextStep(); }, onkeydown: continueOnEnter(() => show(4, 1)) });
        const otherWrap = field('In your words', other);
        otherWrap.hidden = draft.next !== 'other';
        const remind = chips('Reminder', REMIND, (o) => draft.remind === o[1], (o) => { draft.remind = o[1]; });
        const remindWrap = h('div', {}, h('p', { class: 'guide-label', text: 'Remind me' }), remind);
        const what = chips('Next step', [...NEXT.map((n) => [n, n]), ['Something else', 'other']], (o) => draft.next === o[1], (o) => {
          draft.next = draft.next === o[1] ? '' : o[1];
          otherWrap.hidden = draft.next !== 'other';
          remindWrap.hidden = !nextStep();
          if (draft.next === 'other') setTimeout(() => other.focus(), 0);
        });
        remindWrap.hidden = !nextStep();
        return panel('guide-q-next', 'Small and specific works best. Link will remind you, so you don’t have to keep it in your head.',
          'What’s one small next step with ' + firstName() + '?', null, [what, otherWrap, remindWrap],
          nav(() => (nextStep() ? 'Continue' : 'No next step yet'), () => true, () => show(4, 1), true));
      }

      function reviewStep() {
        const error = h('p', { class: 'guide-error', role: 'alert' });
        const line = (label, value, to) => h('div', { class: 'guide-review-row' }, h('dt', { text: label }),
          h('dd', {}, h('span', { class: value ? '' : 'muted', text: value || 'Skipped' }), btn('Edit', () => show(to, -1), 'quiet guide-edit')));
        const met = [context(), whenLabel() && whenLabel() !== 'Not sure' ? whenLabel().toLowerCase() : ''].filter(Boolean).join(', ');
        const next = nextStep() ? nextStep() + (draft.remind != null ? ' · reminder ' + remindLabel().toLowerCase() : ' · no reminder') : '';
        const save = btn('Save ' + firstName(), () => saveAll(save, error), 'primary guide-save');
        save.prepend(h('span', { class: 'guide-spinner', 'aria-hidden': 'true' }));
        return panel('guide-q-review', 'Here’s what I’ll save. Change anything that looks off.', 'Look right?', null,
          [h('dl', { class: 'guide-review' }, line('Name', [draft.name.trim(), draft.org.trim()].filter(Boolean).join(' · '), 0), line('How you met', met, 1),
            line('What you remember', draft.memory.trim(), 2), line('Next step', next, 3)), error],
          [btn('Back', () => show(3, -1), 'quiet'), h('span', { class: 'grow' }), save]);
      }

      // ---- saving, and showing what was saved ----------------------------------------------------------------
      async function saveAll(button, error) {
        if (busy) return;
        busy = true;
        error.textContent = '';
        const label = button.lastChild;
        const was = label.textContent;
        button.disabled = true; button.setAttribute('aria-busy', 'true'); label.textContent = 'Saving…';
        els.pStatus.textContent = 'Saving…'; els.pCard.classList.add('is-saving');
        const orb = els.stage.querySelector('.guide-orb'); if (orb) orb.classList.replace('is-ready', 'is-thinking');
        const slow = setTimeout(() => button.classList.add('is-slow'), 400);  // a spinner only when the wait is noticeable
        try {
          const out = await api('POST', '/api/guide/connection', {
            name: draft.name.trim(), org: draft.org.trim(), context: context(), when: draft.when || { kind: 'unknown' },
            memory: draft.memory.trim(), next_step: nextStep(), remind_in_days: nextStep() ? draft.remind : null, source: draft.source });
          done(out);
        } catch (err) {
          error.textContent = (err.message || 'Couldn’t save.') + ' Your answers are still here.';
          button.disabled = false; button.removeAttribute('aria-busy'); label.textContent = was;
          els.pStatus.textContent = 'Not saved yet'; els.pCard.classList.remove('is-saving');
          if (orb) orb.classList.replace('is-thinking', 'is-ready');
        } finally {
          clearTimeout(slow); button.classList.remove('is-slow'); busy = false;
        }
      }

      function checkMark() {
        const svg = sv('svg', { class: 'guide-check', viewBox: '0 0 52 52', width: '56', height: '56', 'aria-hidden': 'true' });
        svg.append(sv('circle', { class: 'guide-check-ring', cx: '26', cy: '26', r: '24', fill: 'none' }),
          sv('path', { class: 'guide-check-tick', d: 'M15 27l7 7 15-16', fill: 'none' }));
        return svg;
      }

      function done(out) {
        const person = out.person, first = S.guideFirst;
        existing.push({ id: person.id, name: person.name });  // so "Add another person" knows about them
        const items = ['Saved ' + person.name + (person.org ? ' · ' + person.org : '')];
        if (out.logged) items.push('Noted ' + (draft.memory.trim() ? 'what you remember' : 'how you met') + (draft.when && draft.when.kind !== 'unknown' ? ', dated ' + whenLabel().toLowerCase() : ''));
        if (out.next_step) items.push('Next step: ' + out.next_step + (out.remind_on ? ' · reminder ' + longDate(out.remind_on) : ''));
        step = QUESTIONS + 1;
        els.segments.forEach((seg) => { seg.classList.add('is-done'); seg.classList.remove('is-now'); });
        els.progress.setAttribute('aria-valuenow', String(QUESTIONS));
        els.stepLabel.textContent = 'Saved';
        els.pStatus.textContent = 'Saved'; els.pCard.classList.remove('is-saving'); els.pCard.classList.add('is-saved');
        els.pHeading.textContent = 'What Link saved';
        els.headActions.hidden = true;  // the result offers its own next moves
        const list = h('ul', { class: 'guide-saved' }, items.map((t) => h('li', {}, h('span', { class: 'guide-tick', 'aria-hidden': 'true', text: '✓' }), h('span', { text: t }))));
        const result = h('section', { class: 'guide-panel guide-done', 'aria-labelledby': 'guide-q-done' },
          checkMark(), h('h2', { id: 'guide-q-done', tabindex: '-1', text: person.name + ' is in Link.' }), list,
          first ? h('p', { class: 'guide-hint', text: 'That’s your first connection. When it’s time to follow up, it shows on Today.' }) : null,
          h('div', { class: 'guide-actions' }, btn('Add another person', () => { draft = blank(); S.guideFirst = false; show(0, 1); }, 'primary'),
            btn('See ' + person.name.split(/\s+/)[0], () => { S.selectedPerson = person.id; draft = null; go('people'); }, 'quiet'),
            btn('Back to Today', () => { draft = null; go('today'); }, 'quiet')));
        S.guideFirst = false;
        swap(result, 1);
        if (!reduced()) [...list.children].forEach((li, i) => li.animate([{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'translateY(0)' }],
          { duration: 260, delay: 320 + i * 140, easing: EASE, fill: 'backwards' }));
        els.live.textContent = 'Saved. ' + person.name + ' is in Link. ' + items.join('. ') + '.';
        draft = blank();
      }

      // The walkthrough (D55) sets answers directly, so Back and Next can land on any question without typing again.
      async function prefill(values, at) {
        if (!draft || step > QUESTIONS) draft = blank();
        Object.assign(draft, values);
        S.guideFirst = false;
        if (!els || !els.stage.isConnected) { step = at; return; }
        for (let i = 0; moving && i < 40; i++) await new Promise((resolve) => setTimeout(resolve, 25));  // let a slide finish
        moving = false;
        show(at, 0);
      }
      function reset() { draft = blank(); step = 0; }
      return { open, render, prefill, reset };
    }
  };
})();
