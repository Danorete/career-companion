/* Relationship coaching is a workflow, not a second chat inbox.
 * All imported/model text uses text nodes. Every consequential save is a review click.
 */
(function () {
  'use strict';
  window.LinkWorkflows = {
    create({h, btn, field, select, disc, api, act, S, go, render, toast, orbSvg, connectionMotif, openSource}) {
      let flow = null;
      const modes = {
        starting: ['Find a starting point', "You don't need a contact list. What would you like to explore, and where do you already spend time?", 'A field, class, workplace, interest or community. “I’m not sure” is a useful answer.'],
        reconnect: ['Approach someone', 'Who comes to mind, and what makes you interested in talking to them?', 'A name and fragments are enough. Include what you would genuinely like to learn.'],
        met: ['Make sense of an encounter', 'Tell me about someone you met. What do you remember?', 'An approximate time, a topic, or something you might have offered. Uncertainty is fine.'],
        prepare: ['Prepare for a conversation', 'What would you like to learn from this conversation?', 'We can develop an introduction, questions, and a respectful closing together.'],
        follow_up: ['Continue a connection', 'What has changed since your conversation?', 'Did you try their advice, finish something you discussed, or find a resource they might appreciate?'],
        opportunity: ['Ask for help', 'What help would make a difference, and why this person?', 'Choose a clear request. An introduction or referral is never assumed.']
      };
      const asks = [['perspective','Career perspective'],['feedback','Feedback on my work'],['team','A team or role'],['introduction','An introduction'],['referral','Discuss a referral']];
      const input = (label, key, values, max=1000, rows=2) => field(label, h('textarea', {
        'aria-label':label, rows, maxlength:max, value:values[key]||'', oninput:e=>values[key]=e.target.value
      }));
      function open(options={}) { flow={inputs:{mode:'starting',...options},plan:null}; go('connect'); }
      async function skip() {
        if(await act(()=>api('POST','/api/onboarding/skip'))) {
          S.onboarding.done=true; document.body.classList.remove('onboarding'); go('today');
        }
      }
      function choose(root, onboarding) {
        const descriptions={starting:'Explore a direction, even with no contacts.',reconnect:'Find a genuine reason to start a conversation.',met:'Keep the fragments and decide what comes next.'};
        const page=h('section',{class:(onboarding?'onb connection-onboarding':'page connection-page')+' studio-welcome'},
          h('div',{class:'welcome-cover'},h('div',{class:'cover-brand'},h('span',{class:'orb is-ready'},orbSvg(35)),h('span',{text:'Link'})),
            h('span',{class:'eyebrow',text:'Your connection studio'}),h('h1',{text:'Good people. Real possibilities.'}),
            h('p',{class:'cover-caption',text:'A little confidence. A thoughtful conversation. Your next opportunity can start here.'}),connectionMotif()),
          h('div',{class:'welcome-choices'},h('span',{class:'eyebrow',text:'01 / A place to begin'}),h('h2',{text:'Where shall we begin?'}),
            h('p',{text:'Tell Link what’s on your mind. We’ll build the context together.'}),
            h('div',{class:'connection-paths'},['starting','reconnect','met'].map(mode=>h('button',{type:'button',class:'path-choice','aria-label':modes[mode][0],onclick:()=>{flow={inputs:{mode},plan:null};render();}},
              h('span',{},h('strong',{text:modes[mode][0]}),h('small',{text:descriptions[mode]})),h('span',{class:'path-arrow','aria-hidden':'true',text:'→'})))),
            h('div',{class:'welcome-import-path'},h('strong',{text:'Already have a network?'}),h('p',{class:'muted small',text:'Bring LinkedIn contacts, select conversation excerpts, or prepare from a calendar file. You choose what stays.'}),btn('Import my connections',async()=>{
              if(onboarding){if(!await act(()=>api('POST','/api/onboarding/skip')))return;S.onboarding.done=true;document.body.classList.remove('onboarding');}
              openSource('connections');
            },'quiet')),
            disc('welcome-privacy','Your context stays in your control','',h('p',{text:'No résumé or contact import required. You review what gets saved. Live planning uses the fields you provide and saved working preferences. Public messages use a separate approved context. Mock mode shows a general example.'})),
            btn(onboarding?'Explore the workspace first':'Back to Today',()=>onboarding?skip():go('today'),'quiet')));
        if(S.demo)page.querySelector('.welcome-choices').prepend(h('p',{class:'notice',text:'Fictional demo · mock AI · separate database'}));
        root.append(page);
      }
      async function start(root,onboarding=false) {
        if(!flow) {
          choose(root,onboarding);
          if(!onboarding) await history(root);
          return;
        }
        const values=flow.inputs;
        const page=h('section',{class:onboarding?'onb connection-onboarding':'page connection-page'});
        root.append(page);
        page.append(h('div',{class:'row spread'},h('strong',{text:'Link · '+modes[values.mode][0]}),btn('Choose another path',()=>{flow=null;render();},'quiet')));
        if(flow.plan) { review(page,flow.plan,onboarding); return; }
        let person=null;
        if(values.item_id) {
          person=await api('GET','/api/people/'+values.item_id);
          page.append(h('p',{class:'notice',text:'Working with '+person.name+'. Private notes and previous chats are not included.'}));
          if(values.approved_context===undefined)values.approved_context=person.context||'';
        }
        page.append(h('div',{class:'guide-intro'},h('span',{class:'eyebrow',text:'A conversation with Link'}),h('h1',{text:modes[values.mode][1]}),h('p',{class:'muted',text:modes[values.mode][2]})));
        const textKey=['prepare','opportunity'].includes(values.mode)?'learning_question':'recollection';
        const form=h('form',{class:'stack',onsubmit:async e=>{
          e.preventDefault();
          submit.disabled=true;
          const result=await act(()=>api('POST','/api/connections/plans',values));
          submit.disabled=false;
          if(result) { flow.plan=result;render(); }
        }},input('Tell Link',textKey,values, textKey==='recollection'?4000:1000,4));
        if(values.mode==='opportunity')form.append(field('Type of help',select(asks,values.ask_type||'perspective',v=>values.ask_type=v)),h('p',{class:'muted small',text:'We can make the ask specific and easy to decline. An introduction or referral needs their agreement; Link cannot tell you whether someone will say yes.'}));
        if(values.mode==='starting')form.append(disc('connection-access','Help me think of possibilities','Optional',
          h('p',{text:'A classmate, recent graduate, former supervisor, professor, volunteer group or professional community can be a starting point. No campus access? Start with a public community or open event; Link cannot verify availability.'}),
          ...['Class or student group','Work or volunteering','Public community','No existing connection'].map(label=>btn(label,()=>{values.goal=label;hint.textContent='Context added: '+label;},'quiet'))));
        const hint=h('p',{class:'muted small',role:'status'});form.append(hint);
        form.append(disc('connection-extra','More context','Optional',
          input('Why this person or setting?', 'why_person',values,800),
          input('What are you hoping to work toward? (private planning)', 'goal',values,600),
          input('Professional context approved for later messages', 'approved_context',values,2000),
          input('An example of your work you are comfortable sharing', 'example',values,1200)));
        const submit=h('button',{type:'submit',class:'btn primary big'},S.ai.available?'Think it through with Link':'Build a plan without AI');
        form.append(submit,h('p',{class:'muted small',text:'No one will be contacted. Link proposes a plan; you choose what becomes a person, note, or task.'}));
        page.append(form,btn('Not now',()=>onboarding?skip():go('today'),'quiet'));
      }
      function review(root,plan,onboarding) {
        const out=plan.payload;
        const story=h('section',{class:'plan-story'}), tools=h('section',{class:'plan-tools','aria-label':'Review and work on this plan'});
        root.append(h('div',{class:'plan-spread'},story,tools));
        story.append(h('h1',{text:'Here’s a possible next step.'}),
          h('p',{class:'notice',text:plan.source==='live'?'AI proposal · review before saving':plan.source==='mock'?'Mock example · not personalized analysis':'AI unavailable · general guide'}),
          h('p',{text:out.acknowledgment}),h('section',{class:'panel stack'},h('h2',{text:out.purpose}),h('p',{text:out.reason}),h('p',{text:out.next_step})),
          out.questions.length?h('section',{class:'stack'},h('h3',{text:'Questions to explore'}),h('ul',{},out.questions.map(q=>h('li',{text:q})))):null,
          out.uncertainties.length?disc('plan-uncertainty','What remains uncertain','Keep these as questions',...out.uncertainties.map(t=>h('p',{text:t}))):null,
          out.considerations.length?disc('plan-considerations','Things to consider','',...out.considerations.map(t=>h('p',{text:t}))):null);
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
      function messageTools(plan) {
        // The exact fields below, plus public voice/evidence explicitly selected by the user,
        // are the only inputs to the separate outward drafting call.
        const ask=asks.find(([id])=>id===plan.inputs.ask_type)?.[1]||'Career perspective';
        const v={context:plan.inputs.approved_context||'',instruction:(plan.mode==='opportunity' ? ask+': ' : '')+(plan.inputs.learning_question||'')};
        const output=h('div',{class:'stack'});
        return disc('plan-message-'+plan.id,'Prepare a message','Review the context first',
          h('p',{class:'muted small',text:'Only these two fields and your public voice preferences go to drafting. Private planning, rough recollections, and chat are excluded. Include the recipient name yourself if wanted.'}),
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
              ...(draft.gaps||[]).map(t=>h('p',{class:'notice',text:t})),
              ...(draft.report?.issues||[]).map(t=>h('p',{class:'notice',text:typeof t==='string'?t:JSON.stringify(t)})),
              btn('Copy message',async()=>{try{await navigator.clipboard.writeText(text.value);toast('Copied, not sent.');}catch(e){toast('Select the text and copy manually.');}}),send);
          },'primary'),output);
      }
      function practiceTools(plan) {
        const output=h('div',{class:'stack'});let answer='',previous_question='';
        return disc('plan-practice-'+plan.id,'Practice a short conversation','Optional rehearsal',
          h('p',{text:'This is a fictional rehearsal, not a prediction of what this person will say. Only approved professional context and your practice answer are used.'}),
          field('Your introduction or answer',h('textarea',{'aria-label':'Your practice answer',rows:3,maxlength:3000,oninput:e=>answer=e.target.value})),
          btn('Practice with Link',async()=>{const result=await act(()=>api('POST','/api/connections/plans/'+plan.id+'/practice',{answer,previous_question}));
            if(result){previous_question=result.next_question.slice(0,500);output.append(h('div',{class:'panel stack'},h('p',{class:'notice',text:'Fictional rehearsal'}),h('p',{text:result.simulated_reply}),h('p',{text:result.feedback}),h('p',{text:result.next_question})));}}),output);
      }
      async function history(root) {
        const plans=await api('GET','/api/connections/plans');
        if(!plans.length)return;
        root.append(h('section',{class:'page stack'},h('h3',{text:'Your saved preparation'}),plans.slice(0,5).map(plan=>h('div',{class:'row spread'},
          h('span',{text:modes[plan.mode][0]+' · '+(plan.status==='confirmed'?'saved':'awaiting review')}),
          h('div',{class:'row'},btn('Resume plan',()=>{flow={inputs:plan.inputs,plan};render();}),btn('Delete plan',async()=>{if(confirm('Delete this plan? People and actions you already confirmed remain.')){await act(()=>api('DELETE','/api/connections/plans/'+plan.id));render();}},'quiet'))))));
      }
      async function personTools(root,person) {
        root.append(h('div',{class:'row'},btn('Help me prepare',()=>open({mode:'prepare',item_id:person.id})),
          btn('Find a reason to follow up',()=>open({mode:'follow_up',item_id:person.id})),
          btn('Ask for help or an opportunity',()=>open({mode:'opportunity',item_id:person.id}))));
        const plans=await api('GET','/api/connections/plans?item_id='+person.id);
        if(plans.length)root.append(disc('person-plans','Saved preparation','Resume without another AI call',plans.slice(0,4).map(plan=>btn(modes[plan.mode][0],()=>{flow={inputs:plan.inputs,plan};go('connect');},'quiet'))));
      }
      async function todayTools(page,compact=false) {
        if(!compact)page.append(h('div',{class:'row'},btn('I’m stuck — help me choose',()=>{flow=null;go('connect');}),btn('Something happened',()=>go('quicklog'),'quiet')));
        if(!compact)page.append(h('div',{class:'starting-prompts row'},btn('I don’t know anyone yet',()=>open({mode:'starting'}),'quiet'),btn('I just met someone',()=>open({mode:'met'}),'quiet'),btn('Help me reconnect',()=>open({mode:'reconnect'}),'quiet')));
        const [plans,candidates]=await Promise.all([api('GET','/api/connections/plans'),api('GET','/api/connections/follow-ups')]);
        const last=plans[0];
        if(last)page.append(disc('resume-connection-plan','Resume your connection plan',modes[last.mode][0],
          h('p',{text:last.payload.next_step}),btn('Continue',()=>{flow={inputs:last.inputs,plan:last};go('connect');})));
        if(candidates.length)page.append(disc('substantive-followup','A possible conversation to revisit',candidates[0].name,
          candidates.slice(0,3).map(c=>h('div',{class:'stack'},h('strong',{text:c.name}),h('p',{text:c.reason}),
            c.possible_commitments?h('p',{class:'muted small',text:'Unconfirmed: '+c.possible_commitments}):null,
            btn('Review and decide',()=>open({mode:'follow_up',item_id:c.item_id,recollection:[c.summary,c.possible_commitments ? 'Possible commitment (unconfirmed): '+c.possible_commitments : '',c.suggestions].filter(Boolean).join('\n')})),btn('Not relevant',async()=>{await act(()=>api('POST','/api/connections/follow-ups/'+c.id+'/dismiss'));render();},'quiet')))));
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
