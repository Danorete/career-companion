/* Local, deterministic guidance. No model calls, form submission or data writes. */
(() => {
  'use strict';
  const key='cc.linkGuide', $=s=>document.querySelector(s);
  const read=()=>{try{return JSON.parse(localStorage.getItem(key))||{};}catch{return {};}};
  let state=read(), card, target, frame;
  const steps=[
    {title:'A colleague, one click away.',text:'I’m Link. Click my avatar to open our conversation. You can tuck me away whenever you want more room.',selector:'#dock-pill',event:'dock'},
    {title:'Start with a person.',text:'Click People. This is where a brief encounter can grow into an ongoing connection.',selector:'#side a[href="#people"]',route:'people'},
    {title:'Context grows over time.',text:'You don’t need a complete profile. A name and where you met are enough. Open someone to revisit your conversations or choose a next step.',selector:'#main .page',manual:true},
    {title:'Keep the moment, while it’s fresh.',text:'Click Quick log. Capture a few fragments after a conversation, even when you don’t remember every detail.',selector:'#side a[href="#quicklog"]',route:'quicklog'},
    {title:'Try a rough recollection.',text:'Type a few words into the log. Your unfinished draft stays on this Mac. Only Save quick log adds it to your history; Link can help organize it afterward.',selector:'#main textarea',event:'input'},
    {title:'Your pace. Your connections.',text:'That’s the loop: capture a moment, revisit a person, choose one thoughtful next step. Your note is still here to finish or discard. Find this walkthrough again in Settings & data.',selector:'#main .page',manual:true}
  ];
  function node(tag,text,cls){const e=document.createElement(tag);if(text)e.textContent=text;if(cls)e.className=cls;return e;}
  function save(){try{localStorage.setItem(key,JSON.stringify(state));}catch{}}
  function clear(){if(target)target.classList.remove('guide-target');target=null;if(card)card.remove();card=null;}
  function pause(){state.active=false;save();clear();launcher.textContent='Resume tour';launcher.hidden=false;launcher.focus();}
  function finish(){state={done:true,active:false,step:0};save();clear();launcher.textContent='Meet Link';launcher.hidden=false;launcher.focus();}
  function advance(){state.step++;if(state.step>=steps.length){finish();return;}save();draw();}
  function draw(){
    clear();if(!state.active)return;
    const step=steps[state.step]||steps[0];target=$(step.selector);
    if(target)target.classList.add('guide-target');
    card=node('section',null,'link-guide');card.setAttribute('role','region');card.setAttribute('aria-live','polite');card.setAttribute('aria-label','Link guided walkthrough');
    const avatar=$('#orb svg');if(avatar){const copy=avatar.cloneNode(true);copy.classList.add('guide-avatar');card.append(copy);}
    card.append(node('span','LINK · YOUR GUIDE','guide-eyebrow'),node('p',`${state.step+1} / ${steps.length}`,'guide-progress'));
    const title=node('h2',step.title);card.append(title,node('p',step.text));
    const actions=node('div',null,'guide-actions');
    const button=(text,fn)=>{const b=node('button',text,'btn quiet');b.type='button';b.onclick=fn;actions.append(b);return b;};
    button('Pause',pause);button('Skip tour',finish);
    button(step.manual?(state.step===steps.length-1?'Finish tour':'Got it, next'):'Skip this step',advance);
    card.append(actions);document.body.append(card);launcher.hidden=true;
    // Non-modal: highlighted controls and the rest of the workspace remain usable.
    position();
  }
  function position(){if(!card)return;const r=target?.getBoundingClientRect();const w=Math.min(370,innerWidth-32);card.style.width=w+'px';
    let left=innerWidth-w-28,top=innerHeight-card.offsetHeight-115;
    if(r&&r.width&&r.height){left=r.right+18;top=r.top;if(left+w>innerWidth-16)left=Math.max(16,r.left-w-18);}
    card.style.left=Math.max(16,Math.min(left,innerWidth-w-16))+'px';card.style.top=Math.max(16,Math.min(top,innerHeight-card.offsetHeight-16))+'px';
  }
  const launcher=node('button','Meet Link','guide-launcher');launcher.type='button';launcher.setAttribute('aria-label','Meet Link: guided walkthrough');launcher.onclick=()=>window.LinkGuide.start();document.body.append(launcher);
  if(state.step&&!state.done)launcher.textContent='Resume tour';
  window.LinkGuide={start(){state={step:state.done?0:(state.step||0),active:true,done:false};save();if(state.step===0&&$('#dock').getAttribute('aria-hidden')==='false')$('#dock-collapse').click();draw();card.querySelector('button').focus();}};
  window.addEventListener('link:dockchange',e=>{if(state.active&&steps[state.step]?.event==='dock'&&e.detail.open)setTimeout(advance,100);});
  window.addEventListener('hashchange',()=>setTimeout(()=>{if(!state.active)return;const step=steps[state.step];if(step?.route===location.hash.slice(1))advance();else draw();},100));
  document.addEventListener('input',e=>{if(state.active&&steps[state.step]?.event==='input'&&e.target.matches('#main textarea')&&e.target.value.trim())advance();});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&state.active){e.preventDefault();pause();}});
  const observer=new MutationObserver(()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{if(state.active)draw();});});
  observer.observe($('#main'),{childList:true,subtree:true});observer.observe($('#side'),{childList:true,subtree:true});
  window.addEventListener('resize',position);document.addEventListener('scroll',position,true);
  // A reload pauses the tour rather than interrupting the next session.
  state.active=false;save();
})();
