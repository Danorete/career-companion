/* Local snapshot workflows. Imported text is rendered with DOM text nodes, never HTML. */
(() => {
  'use strict';
  window.LinkSources={create({h,btn,field,select,api,act,S,go,render,workflows}){
    let mode='connections',people=[],revealPanel=false;
    let connections={text:'',preview:null,choices:new Map(),search:'',page:0};
    let messages={text:'',kind:'csv',rows:null,selected:new Set(),note:'',retain:false,person:''};
    let calendar={text:'',preview:null,person:''};
    const modes=[['connections','01','Your people','Start with a LinkedIn connection export.','network-people'],['messages','02','Your conversations','Bring only the moments worth remembering.','network-moments'],['calendar','03','Your next meeting','Prepare before you meet. Capture what happened afterward.','network-meetings']];
    const status=(text)=>h('p',{class:'notice',role:'status',text});
    const image=name=>h('img',{src:'/static/'+name+'.svg',alt:'',width:560,height:320,loading:'lazy',class:'network-art'});
    function namedSelect(label,options,value,onchange){const control=select(options,value,onchange);control.setAttribute('aria-label',label);return field(label,control);}
    const choosePerson=(value,set)=>namedSelect('Person (optional)',[['','Choose later / unassigned'],...people.map(p=>[p.id,p.name])],value,v=>set(v));
    function upload(label,accept,change){
      return field(label,h('input',{type:'file',accept,'aria-label':label,onchange:async e=>{
        const file=e.target.files[0];if(!file)return;
        if(file.size>290000){e.target.value='';alert('Choose a file smaller than 290 KB. Split larger exports, retaining their CSV header.');return;}
        try{const text=await file.text();if(text.includes('\u0000'))throw Error('Choose a UTF-8 text export, not a ZIP or PDF.');await change(text,file.name);}catch(err){alert(err.message);}
      }}));
    }
    function connectionPanel(root){
      root.append(h('h2',{text:'Bring your connections into focus.'}),h('p',{text:'Import the English Connections.csv from LinkedIn’s official data export. Review names and companies, then choose who belongs here. Emails are ignored.'}),
        h('a',{href:'https://www.linkedin.com/help/linkedin/answer/a1339364',target:'_blank',rel:'noopener noreferrer',class:'btn quiet',text:'How to download your LinkedIn data ↗'}),
        upload('Choose Connections.csv','.csv,text/csv',async text=>{
          connections={text,preview:null,choices:new Map(),search:'',page:0};
          const preview=await act(()=>api('POST','/api/network/connections/preview',{text}));if(!preview)return;
          connections.preview=preview;paint();
        }));
      if(!connections.preview)return;
      root.append(status(connections.preview.notice));
      const listing=h('div',{class:'network-review'}),summary=h('p',{role:'status',class:'muted small'});
      const search=h('input',{type:'search',value:connections.search,'aria-label':'Search imported connections',placeholder:'Find a name, role or company…',oninput:e=>{connections.search=e.target.value;connections.page=0;draw();}});
      const count=()=>summary.textContent=connections.choices.size+' chosen · '+connections.preview.count+' in this file. Matching names are suggestions, not proof of identity.';
      function draw(){
        const q=connections.search.toLocaleLowerCase();const rows=connections.preview.rows.filter(r=>[r.name,r.org,r.position].join(' ').toLocaleLowerCase().includes(q));
        const offset=connections.page*25;listing.replaceChildren();
        rows.slice(offset,offset+25).forEach(r=>{
          const choice=connections.choices.get(r.row)||{choice:'skip',target_id:null};
          const opts=[['skip','Skip this person'],...(!r.already_imported?[['add',r.matches.length?'Add as a separate person':'Add new person'],...r.matches.map(p=>['match:'+p.id,'Fill blank fields: '+p.name+(p.org?' · '+p.org:'')])]:[])];
          const value=choice.choice==='fill_missing'?'match:'+choice.target_id:choice.choice;
          listing.append(h('article',{class:'network-person'},h('div',{class:'grow'},h('h3',{text:r.name}),h('p',{class:'muted small',text:[r.position,r.org].filter(Boolean).join(' · ')||'No role or company supplied'}),
            r.already_imported?h('span',{class:'chip',text:'Already imported'}):r.matches.length?h('p',{class:'small',text:r.matches.map(p=>p.reason).join(' · ')}):null),
            namedSelect('Import choice for '+r.name,opts,value,v=>{
              if(v==='skip')connections.choices.delete(r.row);else connections.choices.set(r.row,{choice:v.startsWith('match:')?'fill_missing':'add',target_id:v.startsWith('match:')?Number(v.slice(6)):null});count();
            })));
        });
        if(!rows.length)listing.append(h('p',{text:'No matches in this file.'}));
        listing.append(h('div',{class:'row spread'},btn('Previous',()=>{connections.page=Math.max(0,connections.page-1);draw();},'quiet'),h('span',{class:'muted small',text:rows.length?`${offset+1}–${Math.min(offset+25,rows.length)} of ${rows.length}`:'0 results'}),btn('Next',()=>{if(offset+25<rows.length){connections.page++;draw();}},'quiet')));count();
      }
      root.append(h('div',{class:'row'},search,btn('Choose unmatched new contacts',()=>{connections.preview.rows.filter(r=>!r.matches.length&&!r.already_imported).forEach(r=>connections.choices.set(r.row,{choice:'add',target_id:null}));draw();},'quiet'),btn('Clear choices',()=>{connections.choices.clear();draw();},'quiet')),summary,listing,
        h('p',{class:'muted small',text:'Filling blanks preserves existing names, organizations, notes and context. Exported role and connection date stay labeled as a snapshot; they do not create conversations, closeness scores or tasks.'}),
        btn('Confirm selected connections',async e=>{
          if(!connections.choices.size){alert('Choose at least one person first.');return;}
          const button=e.currentTarget;button.disabled=true;
          const out=await act(()=>api('POST','/api/network/connections/confirm',{text:connections.text,decisions:[...connections.choices].map(([row,d])=>({row,...d}))}));
          if(!out){button.disabled=false;return;}
          connections={text:'',preview:null,choices:new Map(),search:'',page:0};people=await api('GET','/api/people');paint();
          panel.prepend(status(`${out.added} ${out.added===1?'person':'people'} added · ${out.updated} reviewed ${out.updated===1?'update':'updates'} · ${out.skipped} skipped. Choose a small group to focus on; a full directory isn’t a to-do list.`));
          panel.append(btn('Choose someone to focus on',()=>{S.selectedPerson=out.person_ids[0]||null;go('people');},'primary'));
        },'primary'));draw();
    }
    function messagePanel(root){
      root.append(h('h2',{text:'Keep the useful part of a conversation.'}),h('p',{text:'Choose a LinkedIn messages.csv or a text excerpt. Nothing is selected by default. Review the participants yourself; names alone never assign messages to a person.'}),
        upload('Choose messages CSV or text excerpt','.csv,.txt,text/csv,text/plain',async(text,name)=>{messages={text,kind:name.toLowerCase().endsWith('.csv')?'csv':'text',rows:null,selected:new Set(),note:'',retain:false,person:''};const result=await act(()=>api('POST','/api/network/messages/preview',{text,kind:messages.kind}));if(result){messages.rows=result.rows;paint();}}));
      if(messages.rows===null){
        const paste=h('textarea',{rows:4,maxlength:12000,'aria-label':'Paste one conversation excerpt',value:messages.text,oninput:e=>messages.text=e.target.value});
        root.append(field('Or paste one excerpt',paste),btn('Review pasted excerpt',async()=>{messages.kind='text';const result=await act(()=>api('POST','/api/network/messages/preview',{text:messages.text,kind:'text'}));if(result){messages.rows=result.rows;paint();}},'quiet'));return;
      }
      let query='',page=0;
      const rows=h('div',{class:'message-import-list'}),selection=h('p',{role:'status',class:'muted small'});
      const draw=()=>{
        const found=messages.rows.filter(r=>[r.sender,r.recipients,r.content].join(' ').toLowerCase().includes(query));const offset=page*20;rows.replaceChildren();
        found.slice(offset,offset+20).forEach(r=>rows.append(h('label',{class:'message-import-row'},h('input',{type:'checkbox',checked:messages.selected.has(r.row),'aria-label':'Include message '+(r.row+1),onchange:e=>{e.target.checked?messages.selected.add(r.row):messages.selected.delete(r.row);selection.textContent=messages.selected.size+' messages selected. Only selected text can be retained.';}}),
          h('span',{},h('strong',{text:r.sender}),h('span',{class:'muted small',text:' → '+r.recipients+' · '+(r.date||'Date not supplied')}),h('p',{class:'import-excerpt',text:r.content})))));
        rows.append(h('div',{class:'row spread'},btn('Previous messages',()=>{page=Math.max(0,page-1);draw();},'quiet'),h('span',{class:'muted small',text:`${found.length} matching messages`}),btn('Next messages',()=>{if(offset+20<found.length){page++;draw();}},'quiet')));selection.textContent=messages.selected.size+' messages selected. Only selected text can be retained.';
      };
      root.append(field('Search participants or text',h('input',{type:'search','aria-label':'Search conversation messages',oninput:e=>{query=e.target.value.toLowerCase();page=0;draw();}})),selection,rows,
        choosePerson(messages.person,v=>messages.person=v),field('Your recap (required)',h('textarea',{rows:3,maxlength:8000,value:messages.note,'aria-label':'Your conversation recap',placeholder:'What happened? What are you unsure about?',oninput:e=>messages.note=e.target.value})),
        h('label',{class:'check'},h('input',{type:'checkbox',checked:messages.retain,onchange:e=>messages.retain=e.target.checked}),'Keep the selected original messages on this Mac'),
        h('p',{class:'muted small',text:'Unchecked: only your recap is saved. The original file and unselected messages are not stored. Message dates are shown as source dates; the conversation date stays unknown until you choose it. No promises become tasks.'}),
        btn('Save selected conversation',async e=>{
          if(!messages.selected.size||!messages.note.trim()){alert('Choose at least one message and write a short recap.');return;}
          const button=e.currentTarget;button.disabled=true;
          const out=await act(()=>api('POST','/api/network/messages/confirm',{text:messages.text,kind:messages.kind,selected:[...messages.selected],person_id:messages.person?Number(messages.person):null,note:messages.note,retain:messages.retain}));
          if(!out){button.disabled=false;return;}
          messages={text:'',kind:'csv',rows:null,selected:new Set(),note:'',retain:false,person:''};paint();panel.prepend(status(out.already_imported?'These selected messages were already imported; no duplicate was added.':'Recap saved. Review it in Quick log or the person’s Conversations tab.'));
        },'primary'));draw();
    }
    function readableWhen(value){return value.replace(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})?(Z)?$/,(_,y,m,d,hh,mm,ss,z)=>`${y}-${m}-${d} · ${hh}:${mm}${z?' UTC':''}`).replace(/^(\d{4})(\d{2})(\d{2})$/,'$1-$2-$3 · all day');}
    // ---- connected calendar (decision D39): read-only, people found are suggestions until kept ----
    let cal={info:null,found:null,msg:'',confirm:false};
    const sourceState=()=>S.calendar&&S.calendar.connected?'Google Calendar connected (read-only)':'No accounts connected';
    const dev=()=>S.mode==='dev';
    const when=iso=>{const d=new Date(iso);return isNaN(d)?iso:d.toLocaleString(undefined,{weekday:'short',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});};
    async function calendarRefresh(box){
      const [info,found]=await Promise.all([api('GET','/api/connectors/calendar'),api('GET','/api/encounters')]);
      cal.info=info;cal.found=found;S.calendar=info;const label=document.getElementById('source-connection-state');if(label)label.textContent=sourceState();calendarDraw(box);
    }
    function calendarDraw(box){
      const info=cal.info;if(!info)return;box.replaceChildren();
      box.append(h('h2',{text:'Connect your calendar'}),h('p',{text:'Link looks through your Google Calendar for people you have met or are about to meet, so you don’t have to type them in. You decide who to keep.'}),
        h('div',{class:'stack'},h('p',{class:'small'},h('strong',{text:'Link reads: '}),'event titles, start and end times, and the names and email addresses of people invited.'),
          h('p',{class:'small'},h('strong',{text:'Link never reads: '}),'event descriptions, places, notes or your email.'),
          h('p',{class:'small'},h('strong',{text:'Link never: '}),'adds, changes or deletes an event, or sends anything to anyone. You can disconnect any time.')));
      if(cal.msg)box.append(status(cal.msg));
      if(!info.available){box.append(h('p',{class:'muted small',text:dev()?'Calendar sign-in is not configured. Set COMPANION_GOOGLE_CLIENT_ID (see the README), then restart.':'Calendar connection isn’t switched on in this version yet. You can still choose a calendar file below.'}));return;}
      if(!info.connected){
        box.append(btn(info.demo?'Try with a sample calendar':'Connect Google Calendar',async()=>{
          const out=await act(()=>api('POST','/api/connectors/calendar/start',{}));if(!out)return;
          if(out.url){window.location.assign(out.url);return;}
          cal.msg='Sample calendar connected. Nothing is real here and nothing leaves this computer.';await calendarRefresh(box);
        },'primary'));return;
      }
      const row=h('div',{class:'row'});
      row.append(btn('Check my calendar',async()=>{
        const out=await act(()=>api('POST','/api/connectors/calendar/sync',{}));if(!out)return;
        cal.msg=out.found?('Found '+out.found+(out.found===1?' new person':' new people')+' in '+out.events_read+' events.'):'No new people found in '+out.events_read+' events. Link looks for meetings with someone else, or titles like “coffee chat”.';
        await calendarRefresh(box);
      },'primary'),btn('Disconnect…',()=>{cal.confirm=!cal.confirm;calendarDraw(box);},'quiet'));
      box.append(h('p',{class:'muted small',text:'Connected'+(info.demo?' (sample calendar)':'')+(info.last_sync?' · last checked '+when(info.last_sync):' · not checked yet')}),row);
      if(cal.confirm)box.append(h('div',{class:'notice stack'},h('p',{text:'Disconnecting stops Link from reading your calendar. People you already kept stay in Link.'}),
        h('div',{class:'row'},btn('Disconnect and keep what Link found',async()=>{if(await act(()=>api('DELETE','/api/connectors/calendar?remove_data=false')))afterDisconnect(box);}),
          btn('Disconnect and remove what came from my calendar',async()=>{if(await act(()=>api('DELETE','/api/connectors/calendar?remove_data=true')))afterDisconnect(box);}),
          btn('Cancel',()=>{cal.confirm=false;calendarDraw(box);},'quiet'))));
      box.append(h('h3',{text:'People found'}));
      if(!cal.found.length){box.append(h('p',{class:'muted',text:'Nobody is waiting for you. Choose “Check my calendar” after you add a meeting.'}));return;}
      box.append(h('p',{class:'muted small',text:'These are suggestions from invitations, not conversations. Keeping someone saves a person only. Afterward, add a note about what happened.'}));
      cal.found.forEach(c=>{
        let name=c.name,link='';
        const nameInput=h('input',{type:'text',value:name,maxlength:120,'aria-label':'Name for '+c.address,oninput:e=>name=e.target.value});
        const same=c.matches.length?select([['','Save as a new person'],...c.matches.map(m=>[m.id,'Same person as '+m.name+' ('+m.why.toLowerCase()+')'])],'',v=>link=v):null;
        const done=async(fn)=>{const out=await act(fn);if(out){cal.msg=out.name?('Saved '+out.name+'.'):'Done.';await calendarRefresh(box);}};
        box.append(h('article',{class:'meeting-import-card stack'},h('span',{class:'eyebrow',text:when(c.starts_at)}),h('h3',{text:c.title||'Meeting'}),
          h('p',{class:'muted small',text:c.reason+(c.name_guessed?' We guessed the name from the email address. Fix it if it’s wrong.':'')}),
          field('Name',nameInput),same?field('Is this someone you already have?',same):null,
          h('div',{class:'row'},btn('Keep',()=>done(()=>api('POST','/api/encounters/'+c.id+'/keep',link?{person_id:Number(link)}:{name})),'primary'),
            btn('Not now',()=>done(()=>api('POST','/api/encounters/'+c.id+'/dismiss',{scope:'event'})),'quiet'),
            btn('Never suggest this person',()=>done(()=>api('POST','/api/encounters/'+c.id+'/dismiss',{scope:'person'})),'quiet'))));
      });
    }
    async function afterDisconnect(box){cal.confirm=false;cal.msg='Disconnected.';await calendarRefresh(box);}
    // ---- connected email (decision D48): headers only, read-only; people found are suggestions until kept ----
    let mail={info:null,found:null,msg:'',confirm:false};
    async function mailRefresh(box){
      const [info,found]=await Promise.all([api('GET','/api/connectors/email'),api('GET','/api/email-contacts')]);
      mail.info=info;mail.found=info.connected?found:[];S.calendar=Object.assign({},S.calendar,{email:info});mailDraw(box);
    }
    function mailDraw(box){
      const info=mail.info;if(!info)return;box.replaceChildren();
      box.append(h('h2',{text:'Connect your email'}),h('p',{text:'Link looks at who you have written to and who wrote back, so people you already talk to can be added without typing. You decide who to keep.'}),
        h('div',{class:'stack'},h('p',{class:'small'},h('strong',{text:'Link reads: '}),'the names, email addresses and dates on your newest messages. Nothing else.'),
          h('p',{class:'small'},h('strong',{text:'Link never reads: '}),'what a message says, its subject, or any attachment.'),
          h('p',{class:'small'},h('strong',{text:'Link never: '}),'sends, deletes or changes an email. You can disconnect any time.')));
      if(mail.msg)box.append(status(mail.msg));
      if(!info.available){box.append(h('p',{class:'muted small',text:dev()?'Email sign-in needs the Google client from the README with the Gmail API turned on.':'Email connection isn’t switched on in this version yet.'}));return;}
      if(!info.connected){
        box.append(btn(info.demo?'Try with a sample mailbox':'Connect Gmail',async()=>{
          const out=await act(()=>api('POST','/api/connectors/email/start',{}));if(!out)return;
          if(out.url){window.location.assign(out.url);return;}
          mail.msg='Sample mailbox connected. Nothing is real here and nothing leaves this computer.';await mailRefresh(box);
        },'primary'));return;
      }
      const row=h('div',{class:'row'});
      row.append(btn('Check my email',async()=>{
        const out=await act(()=>api('POST','/api/connectors/email/sync',{}));if(!out)return;
        mail.msg=out.found?('Found '+out.found+(out.found===1?' new person':' new people')+'.'):'No new people found. Link only suggests someone after you wrote and they wrote back.';
        await mailRefresh(box);
      },'primary'),btn('Disconnect…',()=>{mail.confirm=!mail.confirm;mailDraw(box);},'quiet'));
      box.append(h('p',{class:'muted small',text:'Connected'+(info.demo?' (sample mailbox)':'')+(info.last_sync?' · last checked '+when(info.last_sync):' · not checked yet')}),row);
      if(mail.confirm)box.append(h('div',{class:'notice stack'},h('p',{text:'Disconnecting stops Link from reading your email. People you already kept stay in Link.'}),
        h('div',{class:'row'},btn('Disconnect and keep what Link found',async()=>{if(await act(()=>api('DELETE','/api/connectors/email?remove_data=false')))mailAfter(box);}),
          btn('Disconnect and remove what came from my email',async()=>{if(await act(()=>api('DELETE','/api/connectors/email?remove_data=true')))mailAfter(box);}),
          btn('Cancel',()=>{mail.confirm=false;mailDraw(box);},'quiet'))));
      box.append(h('h3',{text:'People you email'}));
      if(!mail.found.length){box.append(h('p',{class:'muted',text:'Nobody is waiting for you.'}));return;}
      mail.found.forEach(c=>{
        let name=c.name||c.address.split('@')[0],link='';
        const nameInput=h('input',{type:'text',value:name,maxlength:120,'aria-label':'Name for '+c.address,oninput:e=>name=e.target.value});
        const same=c.matches.length?select([['','Save as a new person'],...c.matches.map(m=>[m.id,'Same person as '+m.name+' ('+m.why.toLowerCase()+')'])],'',v=>link=v):null;
        const done=async(fn)=>{const out=await act(fn);if(out){mail.msg=out.name?('Saved '+out.name+'.'):'Done.';await mailRefresh(box);}};
        box.append(h('article',{class:'meeting-import-card stack'},h('span',{class:'eyebrow',text:'Last '+(c.last_direction==='sent'?'you wrote · ':'they wrote · ')+when(c.last_at)}),h('h3',{text:c.address}),
          h('p',{class:'muted small',text:'You have written each other. Keeping saves a person only, not any message.'}),
          field('Name',nameInput),same?field('Is this someone you already have?',same):null,
          h('div',{class:'row'},btn('Keep',()=>done(()=>api('POST','/api/email-contacts/'+c.id+'/keep',link?{person_id:Number(link)}:{name})),'primary'),
            btn('Not now',()=>done(()=>api('POST','/api/email-contacts/'+c.id+'/dismiss',{scope:'later'})),'quiet'),
            btn('Never suggest this person',()=>done(()=>api('POST','/api/email-contacts/'+c.id+'/dismiss',{scope:'never'})),'quiet'))));
      });
    }
    async function mailAfter(box){mail.confirm=false;mail.msg='Disconnected.';await mailRefresh(box);}
    function mailConnect(root){
      const box=h('section',{class:'connect-card stack','aria-label':'Email connection'});root.append(box);
      if(mail.info)mailDraw(box);else box.append(h('h2',{text:'Connect your email'}),h('p',{class:'muted',role:'status',text:'Loading…'}));
      mailRefresh(box).catch(()=>{box.replaceChildren(h('h2',{text:'Connect your email'}),h('p',{class:'notice bad',role:'alert',text:'Couldn’t load the email connection. Restart Link and try again.'}));});
    }
    function calendarConnect(root){
      const box=h('section',{class:'connect-card stack','aria-label':'Calendar connection'});root.append(box);
      if(cal.info)calendarDraw(box);else box.append(h('h2',{text:'Connect your calendar'}),h('p',{class:'muted',role:'status',text:'Loading…'}));
      calendarRefresh(box).catch(()=>{box.replaceChildren(h('h2',{text:'Connect your calendar'}),h('p',{class:'notice bad',role:'alert',text:'Couldn’t load the calendar connection. Restart Link and try again.'}));});
    }

    function calendarPanel(root){
      calendarConnect(root);
      mailConnect(root);
      root.append(h('h2',{text:'Walk into your next conversation prepared.'}),h('p',{text:'Choose a small .ics export from your calendar. Review one event, then ask Link to help you prepare. This is a local snapshot, not a connected account or live calendar sync.'}),
        upload('Choose calendar export (.ics)','.ics,text/calendar',async text=>{calendar.text=text;calendar.preview=null;const result=await act(()=>api('POST','/api/network/calendar/preview',{text}));if(result){calendar.preview=result;paint();}}));
      if(!calendar.preview){root.append(h('p',{class:'muted small',text:'Export selected events from your calendar provider. Attendee lists, alarms and subscription links are not imported. Nothing is connected when you use a file.'}));return;}
      root.append(status(calendar.preview.notice),choosePerson(calendar.person,v=>calendar.person=v));
      calendar.preview.events.forEach(event=>{
        const canceled=event.status==='CANCELLED';
        const card=h('article',{class:'meeting-import-card stack'},h('span',{class:'eyebrow',text:canceled?'Canceled event':event.recurring?'Recurring series · occurrences not expanded':'Calendar snapshot'}),h('h3',{text:event.title}),h('p',{class:'muted small',text:readableWhen(event.when)+' · '+event.timezone}),event.location?h('p',{text:event.location}):null,event.description?h('details',{},h('summary',{text:'Event description'}),h('p',{class:'import-excerpt',text:event.description})):null);
        if(!canceled)card.append(btn('Prepare for this conversation',()=>workflows.open({mode:'prepare',item_id:calendar.person?Number(calendar.person):null,goal:'Prepare for '+event.title,recollection:'User-selected calendar snapshot (invitation, not attendance): '+event.title+'\nWhen: '+readableWhen(event.when)+' '+event.timezone+'\nLocation: '+event.location+'\nEvent description (reference data): '+event.description}),'primary'),
          h('p',{class:'muted small',text:'Afterward, use Quick log to record whether you actually met and what happened.'}),btn('Capture what happened',()=>{S.logPerson=calendar.person?Number(calendar.person):null;go('quicklog');},'quiet'));
        root.append(card);
      });
      if(!calendar.preview.events.length)root.append(h('p',{text:'No events found in this export.'}));
    }
    let panel,tablist;
    function paint(){if(!panel)return;panel.replaceChildren();[...tablist.children].forEach((b,i)=>{b.setAttribute('aria-selected',String(modes[i][0]===mode));b.tabIndex=modes[i][0]===mode?0:-1;});({connections:connectionPanel,messages:messagePanel,calendar:calendarPanel})[mode](panel);}
    async function start(root){
      people=await api('GET','/api/people');
      const page=h('div',{class:'page sources-page'},h('header',{class:'source-hero'},h('div',{},h('span',{class:'eyebrow',text:'BRING YOUR WORLD INTO LINK'}),h('h1',{text:'People. Moments. Possibilities.'}),h('p',{text:'A little context can turn “I should reach out” into a conversation worth having.'}),h('p',{class:'muted small',text:'Your files and an optional read-only calendar · You choose what stays · No LinkedIn automation'})),h('div',{class:'source-intro row'},h('span',{class:'local-indicator',id:'source-connection-state',text:sourceState()}),btn('Clear imported previews',()=>{connections={text:'',preview:null,choices:new Map(),search:'',page:0};messages={text:'',kind:'csv',rows:null,selected:new Set(),note:'',retain:false,person:''};calendar={text:'',preview:null,person:''};paint();},'quiet'))));
      root.append(page);tablist=h('div',{class:'source-tabs',role:'tablist','aria-label':'Choose a context source'});
      const live=!!(S.calendar&&S.calendar.available)&&S.mode!=='dev';  // the developer version keeps the original tab wording
      modes.forEach(([id,num,title0,subtitle0,art],i)=>{const title=id==='calendar'&&live?'Calendar and email':title0,subtitle=id==='calendar'&&live?'Connect Google Calendar and Gmail to find people you meet and write to, or choose a calendar file.':subtitle0;const button=btn('',()=>{mode=id;paint();},'source-card');button.setAttribute('role','tab');button.id='source-tab-'+id;button.setAttribute('aria-controls','source-panel');button.append(image(art),h('span',{class:'source-card-copy'},h('span',{class:'eyebrow',text:num+' / '+(id==='connections'?'LINKEDIN':id==='messages'?'SELECTED EXCERPTS':live?'CONNECT':'CALENDAR FILE')}),h('strong',{text:title}),h('span',{text:subtitle})));button.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const index=e.key==='Home'?0:e.key==='End'?2:(i+(e.key==='ArrowRight'?1:-1)+3)%3;mode=modes[index][0];paint();tablist.children[index].focus();});tablist.append(button);});
      panel=h('section',{id:'source-panel',class:'source-panel stack',role:'tabpanel','aria-label':'Import review'});page.append(tablist,panel,h('aside',{class:'source-boundary'},h('h3',{text:'Your relationship is more than an export.'}),h('p',{text:'Job titles and connection dates can help you find someone. They cannot tell Link how well you know them. Choose someone, add one thing you remember, and build context gradually.'}),btn('I’m starting without connections',()=>workflows.open({mode:'starting'}),'quiet')));paint();
      if(revealPanel){
        revealPanel=false;
        requestAnimationFrame(()=>{if(!panel.isConnected)return;panel.scrollIntoView({block:'start',behavior:'instant'});const control=panel.querySelector('input,textarea,button');control?.focus({preventScroll:true});});
      }
    }
    function open(kind){
      if(kind&&modes.some(m=>m[0]===kind)){mode=kind;revealPanel=true;}
      go('sources');
    }
    return {start,open};
  }};
})();
