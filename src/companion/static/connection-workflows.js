/* Relationship coaching is a workflow, not a second chat inbox.
 * All imported/model text uses text nodes. Every consequential save is a review click.
 */
(function () {
  'use strict';
  window.LinkWorkflows = {
    create({h, btn, field, select, disc, api, act, S, go, render, toast, orbSvg, connectionMotif, openSource, tip}) {
      let flow = null;
      const linkWrote = new Set();
      const remember = (text) => { linkWrote.add(text); return text; };
      const plain = (name) => String(name || '').replace(/^\[SAMPLE\]\s*/, '');
      const modes = {
        starting: ['Find a starting point', "You don't need a contact list. What would you like to explore, and where do you already spend time?", 'A field, class, workplace, interest or community. “I’m not sure” is a useful answer.'],
        reconnect: ['Approach someone', 'Who comes to mind, and what makes you interested in talking to them?', 'A name and fragments are enough. Include what you would genuinely like to learn.'],
        met: ['Make sense of an encounter', 'Tell me about someone you met. What do you remember?', 'An approximate time, a topic, or something you might have offered. Uncertainty is fine.'],
        prepare: ['Prepare for a conversation', 'What would you like to learn from this conversation?', 'We can develop an introduction, questions, and a respectful closing together.'],
        follow_up: ['Continue a connection', 'What has changed since your conversation?', 'Did you try their advice, finish something you discussed, or find a resource they might appreciate?'],
        opportunity: ['Ask for help', 'What help would make a difference, and why this person?', 'Choose a clear request. An introduction or referral is never assumed.']
      };
      // The user version asks shorter, plainer questions (D53). The developer version keeps the originals above.
      const SIMPLE = {
        starting: ['What are you curious about?', 'A field, a class, a club, or “I’m not sure.”'],
        reconnect: ['Who do you want to reach out to?', 'Their name and why them is enough.'],
        met: ['Who did you meet?', 'Whatever you remember is enough.'],
        prepare: ['What do you want to learn from them?', 'Link helps with an opening line and good questions.'],
        follow_up: ['What’s new since you talked?', 'Something you tried, finished, or found for them.'],
        opportunity: ['What help would you like?', 'Be specific, and make it easy for them to say no.']
      };
      const ask = (mode) => (S.mode === 'dev' ? [modes[mode][1], modes[mode][2]] : SIMPLE[mode]);
      // User version uses everyday words. Developer version keeps the original labels.
      const pick = (dev, user) => (S.mode === 'dev' ? dev : user);
      const PLAIN = {starting:'I don’t know where to start', reconnect:'Reach out to someone', met:'I just met someone',
        prepare:'Prepare for a conversation', follow_up:'Follow up with someone', opportunity:'Ask for help'};
      const title = mode => (S.mode === 'dev' ? modes[mode][0] : PLAIN[mode]);
      const asks = [['perspective','Career perspective'],['feedback','Feedback on my work'],['team','A team or role'],['introduction','An introduction'],['referral','Discuss a referral']];
      const input = (label, key, values, max=1000, rows=2) => field(label, h('textarea', {
        'aria-label':label, rows, maxlength:max, value:values[key]||'', oninput:e=>values[key]=e.target.value
      }));
      function open(options={}) { flow={inputs:{mode:'starting',...options},plan:null}; go('connect'); }
      async function skip(target='today') {
        if(await act(()=>api('POST','/api/onboarding/skip'))) {
          S.onboarding.done=true; document.body.classList.remove('onboarding'); go(target);
          if(target==='today')setTimeout(()=>tip('skip-nudge','Want to add your first person? Open People and choose Add person. It takes about a minute.','handoff'),900);
        }
      }
      // One question and three starter cards (D53). "I just met someone" is the step-by-step guide (D52); on a first
      // visit, "Skip for now" is the other way to begin (D51). Imports and privacy notes live in Add and Settings.
      function startPath(mode, onboarding) {
        // The user version's "I just met someone" is the step-by-step guide; the developer version keeps the AI encounter flow.
        if (mode === 'met' && S.mode !== 'dev') { S.guideFirst = !!onboarding; if (onboarding) skip('add'); else go('add'); return; }
        flow = {inputs: {mode}, plan: null};
        render();
      }
      function choose(root, onboarding) {
        const note = pick({starting:'Explore a direction, even with no contacts.',reconnect:'Find a genuine reason to start a conversation.',met:'Keep the fragments and decide what comes next.'},
          {starting:'No contacts needed. Explore ideas and find one small first step.',
           reconnect:'Get help writing a first message. Start with just a name; nothing is sent.',
           met:'Save a few quick details now, so you remember them later.'});
        const page=h('section',{class:'page connect-simple'+(onboarding?' is-welcome':'')},
          onboarding?h('div',{class:'connect-brand'},h('span',{class:'orb is-ready'},orbSvg(36)),h('span',{text:'Link'})):null,
          h('h1',{text:pick('Where shall we begin?','What do you need help with?')}),
          // A first visit says what Link is for, in one line, right under the question (D54).
          onboarding?h('p',{class:'connect-lede',text:'Link remembers who you met, what you talked about, and what to say next.'}):null,
          // Each card is named by its title; the helper line is its description, so names stay short for screen readers.
          h('div',{class:'connect-cards'},['starting','reconnect','met'].map(mode=>h('button',{type:'button',class:'connect-card',onclick:()=>startPath(mode,onboarding),
            'aria-labelledby':'connect-'+mode+'-title','aria-describedby':'connect-'+mode+'-note'},
            h('span',{class:'connect-card-text'},h('strong',{id:'connect-'+mode+'-title',text:title(mode)}),h('small',{id:'connect-'+mode+'-note',text:note[mode]})),h('span',{class:'path-arrow','aria-hidden':'true',text:'→'})))),
          onboarding?h('div',{class:'connect-skip-row'},
            h('button',{type:'button',class:'btn quiet connect-skip','aria-describedby':'connect-skip-note',onclick:()=>skip()},'Skip for now'),
            h('span',{id:'connect-skip-note',class:'connect-skip-note',text:'Goes straight to Today, your home screen.'})):null,
          onboarding&&S.demo?h('p',{class:'connect-demo',text:pick('Fictional demo · mock AI · separate database','Demo with sample people')}):null);
        root.append(page);
      }
      async function start(root,onboarding=false) {
        if(!flow) {
          choose(root,onboarding);
          if(!onboarding) await history(root.querySelector('.connect-simple'));
          return;
        }
        const values=flow.inputs;
        const page=h('section',{class:'page connect-simple connect-step'+(onboarding?' is-welcome':'')});
        root.append(page);
        page.append(btn('Back',()=>{flow=null;render();},'quiet connect-back'));
        if(flow.plan) { review(page,flow.plan,onboarding); return; }
        let person=null;
        if(values.item_id) {
          person=await api('GET','/api/people/'+values.item_id);
          page.append(h('p',{class:'connect-with',text:pick('Working with '+person.name+'. Private notes and previous chats are not included.','With '+person.name)}));
          if(values.approved_context===undefined)values.approved_context=person.context||'';
        }
        const [question, hint] = ask(values.mode);
        page.append(h('h1',{id:'connect-question',text:question}),h('p',{class:'connect-hint',text:hint}));
        const textKey=['prepare','opportunity'].includes(values.mode)?'learning_question':'recollection';
        const main=h('textarea',{...(S.mode==='dev'?{}:{'aria-labelledby':'connect-question'}),rows:4,maxlength:textKey==='recollection'?4000:1000,value:values[textKey]||'',
          placeholder:'In your own words…',oninput:e=>{values[textKey]=e.target.value;submit.disabled=!e.target.value.trim();}});
        const submit=h('button',{type:'submit',class:'btn primary big connect-go'},S.ai.available?pick('Think it through with Link','Show me a next step'):pick('Build a plan without AI','Show me a next step'));
        submit.disabled=!(values[textKey]||'').trim();
        const form=h('form',{class:'connect-form',onsubmit:async e=>{
          e.preventDefault();
          if(!(values[textKey]||'').trim())return;
          submit.disabled=true;submit.setAttribute('aria-busy','true');submit.textContent='Thinking…';
          const result=await act(()=>api('POST','/api/connections/plans',values));
          submit.disabled=false;submit.removeAttribute('aria-busy');
          if(result) { flow.plan=result;render(); } else submit.textContent=pick('Think it through with Link','Show me a next step');
        }},S.mode==='dev'?field('Tell Link',main):main);  // the developer version keeps its visible label
        const more=[];
        const helpType=values.mode==='opportunity'?field('Type of help',select(asks,values.ask_type||'perspective',v=>values.ask_type=v)):null;
        if(helpType&&S.mode==='dev')form.append(helpType); else if(helpType)more.push(helpType);  // shown up front for builders
        // Honest limits stay on the page in both versions.
        if(values.mode==='opportunity')form.append(h('p',{class:'muted small',text:pick('We can make the ask specific and easy to decline. An introduction or referral needs their agreement; Link cannot tell you whether someone will say yes.',
          'An introduction or referral needs their OK. Link can’t tell you whether someone will say yes.')}));
        const goalField=input(pick('What are you hoping to work toward? (private planning)','What do you hope to get out of it?'), 'goal',values,600);
        const goalBox=goalField.querySelector('textarea');
        const goalAdded=h('p',{class:'muted small',role:'status'});
        if(values.mode==='starting')more.push(h('p',{class:'muted small',text:pick('A classmate, recent graduate, former supervisor, professor, volunteer group or professional community can be a starting point. No campus access? Start with a public community or open event; Link cannot verify availability.',
            'Where could you start? Link can’t check whether a group or event is open to you.')}),
          h('div',{class:'row'},['Class or student group','Work or volunteering','Public community','No existing connection'].map(label=>btn(label,()=>{
            // The choice is written into the visible goal box and said on the page, not only in a tip.
            values.goal=label;goalBox.value=label;goalAdded.textContent=pick('Context added: '+label,'Added to your goal: '+label.toLowerCase()+'.');},'quiet'))),goalAdded);
        more.push(input(pick('Why this person or setting?','Why them, or why there?'), 'why_person',values,800),
          goalField,
          input(pick('Professional context approved for later messages','Anything you’re happy to mention to them'), 'approved_context',values,2000),
          input(pick('An example of your work you are comfortable sharing','Something you made that you’d be glad to share'), 'example',values,1200));
        form.append(submit,h('p',{class:'connect-promise',text:'Nobody gets contacted. You decide what to keep.'}),
          disc('connection-extra',pick('More context','Add more detail'),'Optional',...more));
        page.append(form);  // the promise stays on the page, so turning tips off never hides it
        tip('connect-path-'+values.mode,'Tell me a little, and I’ll suggest one small next step.');
      }
      function review(root,plan,onboarding) {
        const out=plan.payload, simple=S.mode!=='dev';
        const story=h('section',{class:'plan-story'}), tools=h('section',{class:'plan-tools','aria-label':'Review and work on this plan'});
        root.append(h('div',{class:simple?'plan-column':'plan-spread'},story,tools));
        // Honest about where the answer came from, in plain words for the user version.
        const source=simple?(plan.source==='live'?'Suggested by Link’s AI. Check it before you save.':plan.source==='mock'?'This is a sample answer, not advice written for you.':'A general guide, written without AI.')
          :(plan.source==='live'?'AI proposal · review before saving':plan.source==='mock'?'Mock example · not personalized analysis':'AI unavailable · general guide');
        story.append(...[h('h1',{text:'Here’s a possible next step.'}),
          source?h('p',{class:simple?'connect-hint':'notice',text:source}):null,
          h('p',{text:out.acknowledgment}),h('section',{class:'panel stack'},h('h2',{text:out.purpose}),h('p',{text:out.reason}),h('p',{text:out.next_step})),
          out.questions.length?(simple?disc('plan-questions','Questions you could ask','',h('ul',{},out.questions.map(q=>h('li',{text:q}))))
            :h('section',{class:'stack'},h('h3',{text:'Questions to explore'}),h('ul',{},out.questions.map(q=>h('li',{text:q}))))):null,
          out.uncertainties.length?disc('plan-uncertainty','What remains uncertain','Keep these as questions',...out.uncertainties.map(t=>h('p',{text:t}))):null,
          out.considerations.length?disc('plan-considerations','Things to consider','',...out.considerations.map(t=>h('p',{text:t}))):null].filter(Boolean));  // native append would print "null" for a skipped part
        if(plan.status==='confirmed') {
          tools.append(h('p',{class:'notice',text:'Saved. No one has been contacted.'}),
            h('div',{class:'row'},btn('Back to Today',()=>go('today'),'primary'),plan.item_id?btn('Open person',()=>{S.selectedPerson=plan.item_id;go('people');}):null),
            messageTools(plan),practiceTools(plan));
          return;
        }
        if(out.clarification) {
          const detail=h('textarea',{'aria-label':'Optional clarification',rows:2,maxlength:1000,value:flow.inputs.additional_detail||'',oninput:e=>flow.inputs.additional_detail=e.target.value});
          tools.append(disc('plan-clarify','One optional question','You can save without answering',h('p',{text:out.clarification}),detail,
            btn('Update the proposal',async()=>{const result=await act(()=>api('POST','/api/connections/plans',flow.inputs));if(result){flow.plan=result;render();}})));
        }
        if(simple){ simpleSave(tools,plan,out); return; }
        const f={name:out.suggested_name||'',existing_person_id:null,organization:'',context:'',next_action:'',preference:'',save_recollection:false};
        const save=h('button',{type:'submit',class:'btn primary big'},'Save my plan');
        const next=h('input',{'aria-label':'Next action to commit to',maxlength:200,value:'',placeholder:'Optional: choose a step when ready',oninput:e=>f.next_action=e.target.value});
        const form=h('form',{class:'panel stack',onsubmit:async e=>{
          e.preventDefault();save.disabled=true;
          const result=await act(()=>api('POST','/api/connections/plans/'+plan.id+'/confirm',f),'Plan saved.');
          save.disabled=false;
          if(result){S.onboarding.done=true;document.body.classList.remove('onboarding');flow.plan={...plan,status:'confirmed',item_id:result.item_id,result};go('connect');}
        }},h('h3',{text:'Choose what to keep'}),h('p',{class:'muted small',text:'Saving the plan alone is fine. These optional fields create records only when you confirm.'}));
        if(!plan.item_id) {
          const existing=h('div',{});
          api('GET','/api/people').then(people=>{if(people.length)existing.append(field('Or use an existing person',select([['','Create a new person / leave unassigned'],...people.map(p=>[p.id,p.name])], '',value=>f.existing_person_id=value?Number(value):null)));}).catch(()=>{});
          form.append(existing,disc('plan-person','Add the person','Optional; a log can remain unassigned',
          field('Name',h('input',{'aria-label':'Person name to save',maxlength:200,value:f.name,oninput:e=>f.name=e.target.value})),
          field('Organization',h('input',{maxlength:200,oninput:e=>f.organization=e.target.value})),
          input('Context approved for this person’s messages','context',f,2000)));
        }
        if(plan.inputs.recollection)form.append(h('label',{class:'check'},h('input',{type:'checkbox',onchange:e=>f.save_recollection=e.target.checked}),'Save my original recollection as a private quick log (date unknown)'),
          disc('plan-original','See the recollection to be saved','',h('p',{text:plan.inputs.recollection})));
        form.append(field('Next action to commit to',next),btn('Use the suggested step',()=>{f.next_action=out.next_step.slice(0,200);next.value=f.next_action;},'quiet'),
          disc('plan-preference','How should Link work with you?','Optional',input('Working preference to remember','preference',f,1000)),
          save,btn('Change my input',()=>{flow.plan=null;render();},'quiet'));
        tools.append(form,messageTools(plan),practiceTools(plan));
      }
      // The user version saves in one tap: the suggested step and name come prefilled, and the note is kept unless
      // unticked. Every value is visible and editable before Save, so nothing is saved that the person didn't see.
      function simpleSave(tools,plan,out) {
        const note=plan.inputs.recollection||'';
        const wroteIt=!!note&&!linkWrote.has(note);  // a summary Link prefilled is not saved as the person's own words by default
        const f={name:out.suggested_name||'',existing_person_id:null,organization:'',context:'',next_action:(out.next_step||'').slice(0,200),
          preference:'',save_recollection:wroteIt};
        let personName='', people=[];
        const who=h('p',{class:'connect-with'});
        const noteLabel=h('span',{});
        const sayWho=()=>{
          const name=plan.item_id?personName:f.existing_person_id?plain((people.find(p=>p.id===f.existing_person_id)||{}).name):f.name.trim();
          noteLabel.textContent=name?'Keep this note with '+name:'Keep this note (only you see it)';
        };
        const save=h('button',{type:'submit',class:'btn primary big'},'Save');
        const form=h('form',{class:'connect-save stack',onsubmit:async e=>{
          e.preventDefault();save.disabled=true;save.setAttribute('aria-busy','true');save.textContent='Saving…';
          const result=await act(()=>api('POST','/api/connections/plans/'+plan.id+'/confirm',f));
          save.disabled=false;save.removeAttribute('aria-busy');save.textContent='Save';
          if(result){S.onboarding.done=true;document.body.classList.remove('onboarding');flow.plan={...plan,status:'confirmed',item_id:result.item_id,result};
            if(!tip('confirm','Saved. Your next step is waiting on Today.','confirm'))toast('Saved. Your next step is on Today.');go('connect');}
        }},h('h2',{text:'Save it?'}),who,
          field('Your next step',h('input',{maxlength:200,value:f.next_action,oninput:e=>f.next_action=e.target.value})));
        if(plan.item_id){  // say who it is saved to, so nothing lands on someone the screen didn't name
          api('GET','/api/people/'+plan.item_id).then(p=>{personName=plain(p.name);who.textContent='Saving to '+personName;sayWho();}).catch(()=>{});
        } else form.append(field('Their name (optional)',h('input',{maxlength:200,value:f.name,oninput:e=>{f.name=e.target.value;sayWho();}})));
        if(note){
          form.append(h('label',{class:'check'},h('input',{type:'checkbox',checked:wroteIt,onchange:e=>f.save_recollection=e.target.checked}),noteLabel),
            h('blockquote',{class:'connect-note-preview',text:note}));  // the exact words that would be kept
        }
        const options=[];
        if(!plan.item_id){
          const existing=h('div',{});
          api('GET','/api/people').then(list=>{people=list;if(list.length)existing.append(field('Or someone already in Link',select([['','Someone new'],...list.map(p=>[p.id,plain(p.name)])],'',value=>{f.existing_person_id=value?Number(value):null;sayWho();})));}).catch(()=>{});
          options.push(existing,field('Where they work or study',h('input',{maxlength:200,oninput:e=>f.organization=e.target.value})),
            input('What you’re comfortable sharing with them','context',f,2000));
        }
        options.push(input('How should Link work with you?','preference',f,1000));
        sayWho();
        form.append(save,disc('plan-more','More options','',...options),btn('Change my answer',()=>{flow.plan=null;render();},'quiet'));
        tools.append(form,messageTools(plan),practiceTools(plan));
      }
      function messageTools(plan) {
        // The exact fields below, plus public voice/evidence explicitly selected by the user,
        // are the only inputs to the separate outward drafting call.
        const ask=asks.find(([id])=>id===plan.inputs.ask_type)?.[1]||'Career perspective';
        const v={context:plan.inputs.approved_context||'',instruction:(plan.mode==='opportunity' ? ask+': ' : '')+(plan.inputs.learning_question||'')};
        const output=h('div',{class:'stack'});
        return disc('plan-message-'+plan.id,'Prepare a message','Review the context first',
          h('p',{class:'muted small',text:pick('Only these two fields and your public voice preferences go to drafting. Private planning, rough recollections, and chat are excluded. Include the recipient name yourself if wanted.','Link uses these two boxes and the writing style you saved in About me. Your private notes stay out.')}),
          input('Context I approve for this message','context',v,1500,3),input('What I want to ask or say','instruction',v,1000),
          btn('Generate a message',async()=>{const result=await act(()=>api('POST','/api/drafts/generate',{purpose:plan.mode==='follow_up'?'follow_up':'outreach',audience:'peer',evidence_ids:[],instruction:v.instruction||'Write a brief message with a specific request and an easy way to decline. Use placeholders rather than unsupported facts.',shareable_note:v.context,include_item_context:false}));
            if(!result)return;const draft=result.draft;
            const text=h('textarea',{'aria-label':'Connection message draft',rows:6,maxlength:8000,value:draft.body});
            const send=btn('I sent this',async()=>{
              if(!plan.item_id){toast('Associate a person before recording a sent interaction. Your draft is saved in Career tools.');return;}
              send.disabled=true;
              const logged=await act(()=>api('POST','/api/logs',{item_id:plan.item_id,note:'Sent a message: '+text.value,when:{kind:'today'},keep_exchange:false}),'Sent interaction recorded.');
              if(!logged)send.disabled=false;
            });
            output.replaceChildren(text,h('p',{class:'muted small',text:'Draft saved in Career tools. Review it before sending. Copying does not record contact.'}),
              ...(S.mode==='dev'?(draft.gaps||[]).map(t=>h('p',{class:'notice',text:t})):[]),  // checker internals: developer version only
              ...(S.mode==='dev'?(draft.report?.issues||[]).map(t=>h('p',{class:'notice',text:typeof t==='string'?t:JSON.stringify(t)})):[]),
              btn('Copy message',async()=>{try{await navigator.clipboard.writeText(text.value);toast('Copied, not sent.');}catch(e){toast('Select the text and copy manually.');}}),send);
          },'primary'),output);
      }
      function practiceTools(plan) {
        const output=h('div',{class:'stack'});let answer='',previous_question='';
        return disc('plan-practice-'+plan.id,'Practice a short conversation','Optional rehearsal',
          h('p',{text:pick('This is a fictional rehearsal, not a prediction of what this person will say. Only approved professional context and your practice answer are used.','Practice only. They may answer differently.')}),
          field('Your introduction or answer',h('textarea',{'aria-label':'Your practice answer',rows:3,maxlength:3000,oninput:e=>answer=e.target.value})),
          btn('Practice with Link',async()=>{const result=await act(()=>api('POST','/api/connections/plans/'+plan.id+'/practice',{answer,previous_question}));
            if(result){previous_question=result.next_question.slice(0,500);output.append(h('div',{class:'panel stack'},h('p',{class:'notice',text:'Fictional rehearsal'}),h('p',{text:result.simulated_reply}),h('p',{text:result.feedback}),h('p',{text:result.next_question})));}}),output);
      }
      async function history(root) {
        if(!root)return;
        const plans=await api('GET','/api/connections/plans');
        if(!plans.length)return;
        if(S.mode!=='dev') {  // the user version: one quiet way back in, not a list to manage
          const last=plans[0];
          root.append(h('div',{class:'connect-resume'},btn('Pick up where you left off →',()=>{flow={inputs:last.inputs,plan:last};render();},'quiet')));
          return;
        }
        root.append(h('section',{class:'stack connect-history'},h('h3',{text:'Your saved preparation'}),plans.slice(0,5).map(plan=>h('div',{class:'row spread'},
          h('span',{text:title(plan.mode)+' · '+(plan.status==='confirmed'?'saved':'awaiting review')}),
          h('div',{class:'row'},btn('Resume plan',()=>{flow={inputs:plan.inputs,plan};render();}),btn('Delete plan',async()=>{if(confirm('Delete this plan? People and actions you already confirmed remain.')){await act(()=>api('DELETE','/api/connections/plans/'+plan.id));render();}},'quiet'))))));
      }
      async function personTools(root,person) {
        root.append(h('div',{class:'row'},btn('Help me prepare',()=>open({mode:'prepare',item_id:person.id})),
          btn('Find a reason to follow up',()=>open({mode:'follow_up',item_id:person.id})),
          btn('Ask for help or an opportunity',()=>open({mode:'opportunity',item_id:person.id}))));
        const plans=await api('GET','/api/connections/plans?item_id='+person.id);
        if(plans.length)root.append(disc('person-plans',pick('Saved preparation','Saved plans'),pick('Resume without another AI call','Pick up where you left off'),plans.slice(0,4).map(plan=>btn(title(plan.mode),()=>{flow={inputs:plan.inputs,plan};go('connect');},'quiet'))));
      }
      async function todayTools(page,compact=false) {
        if(!compact)page.append(h('div',{class:'row'},btn('I’m stuck — help me choose',()=>{flow=null;go('connect');}),btn('Something happened',()=>go('quicklog'),'quiet')));
        if(!compact)page.append(h('div',{class:'starting-prompts row'},btn('I don’t know anyone yet',()=>open({mode:'starting'}),'quiet'),btn('I just met someone',()=>open({mode:'met'}),'quiet'),btn('Help me reconnect',()=>open({mode:'reconnect'}),'quiet')));
        const [plans,candidates]=await Promise.all([api('GET','/api/connections/plans'),api('GET','/api/connections/follow-ups')]);
        const last=plans[0];
        if(last)page.append(disc('resume-connection-plan',pick('Resume your connection plan','Pick up where you left off'),title(last.mode),
          h('p',{text:last.payload.next_step}),btn('Continue',()=>{flow={inputs:last.inputs,plan:last};go('connect');})));
        if(candidates.length)page.append(disc('substantive-followup','A possible conversation to revisit',candidates[0].name,
          candidates.slice(0,3).map(c=>h('div',{class:'stack'},h('strong',{text:c.name}),h('p',{text:c.reason}),
            c.possible_commitments?h('p',{class:'muted small',text:'Unconfirmed: '+c.possible_commitments}):null,
            btn('Review and decide',()=>open({mode:'follow_up',item_id:c.item_id,recollection:remember([c.summary,c.possible_commitments ? 'Possible commitment (unconfirmed): '+c.possible_commitments : '',c.suggestions].filter(Boolean).join('\n'))})),btn('Not relevant',async()=>{await act(()=>api('POST','/api/connections/follow-ups/'+c.id+'/dismiss'));render();},'quiet')))));
      }
      function quickPrompts(note) {
        const prompt=h('div',{class:'row'},h('span',{class:'muted small',text:'Need a memory cue?'}));
        const help=h('p',{class:'muted small',role:'status'});
        ['What stood out?','Did either of you offer to do anything?','What would you like to ask next time?'].forEach(q=>prompt.append(btn(q,()=>{help.textContent=q+' Leave it unknown if you’re not sure.';note.focus();},'quiet')));
        return h('div',{},prompt,help);
      }
      return {open,begin:()=>{flow=null;go('connect');},start,onboard:root=>start(root,true),personTools,todayTools,quickPrompts};
    }
  };
})();
