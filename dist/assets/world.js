/* THE DIRECTORY: original motion and navigation. No third-party animation runtime.
   Shared principles: clip-path scene transitions (.65,0,.35,1),
   editorial staggered entrances (.16,1,.3,1), touch and keyboard first. */
(() => {
  'use strict';
  const EASE='cubic-bezier(.65,0,.35,1)', EXPO='cubic-bezier(.16,1,.3,1)';
  const reduce=matchMedia('(prefers-reduced-motion: reduce)');
  const chapters=['systems','research','music','about'];
  const palette={systems:[199,254,145],research:[166,184,255],music:[247,164,146],about:[224,218,204]};
  let active=null,busy=false,queuedKey=undefined,menuOpen=false,artClean=()=>{},homeRoot=null;
  const $=(sel,ctx=document)=>ctx.querySelector(sel);
  const $$=(sel,ctx=document)=>[...ctx.querySelectorAll(sel)];
  // Keep the final animation state before clearing the animation object.
  async function run(node,frames,options={}){
    if(!node||reduce.matches)return;
    const ani=node.animate(frames,{fill:'both',...options});
    try{await ani.finished}catch{return}
    for(const [k,v] of Object.entries(frames[frames.length-1])){
      if(!['offset','easing','composite'].includes(k))node.style[k]=v;
    }
    ani.cancel();
  }
  async function curtain(action){
    const wipe=$('[data-wipe]');
    if(reduce.matches||!wipe){action();return}
    wipe.style.visibility='visible';
    wipe.style.clipPath='inset(100% 0 0 0)';
    await run(wipe,[{clipPath:'inset(100% 0 0 0)'},{clipPath:'inset(0 0 0 0)'}],{duration:550,easing:EASE});
    action();
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
    await run(wipe,[{clipPath:'inset(0 0 0 0)'},{clipPath:'inset(0 0 100% 0)'}],{duration:630,easing:EASE});
    wipe.style.visibility='hidden';
    wipe.style.clipPath='inset(100% 0 0 0)';
  }
  function setRoomSync(key){
    const root=$('[data-world]');if(!root)return;
    const directory=$('[data-directory]',root),pager=$('[data-room-pager]',root);
    $$('.room',root).forEach(r=>{
      const on=r.dataset.room===key;
      r.classList.toggle('is-visible',on);r.inert=!on;r.setAttribute('aria-hidden',String(!on));
      if(on)r.scrollTop=0;
    });
    directory.inert=!!key;directory.setAttribute('aria-hidden',String(!!key));directory.style.display=key?'none':'';
    pager.classList.toggle('is-visible',!!key);pager.inert=!key;pager.setAttribute('aria-hidden',String(!key));
    $$('[data-pager]',pager).forEach(b=>{b.classList.toggle('is-active',b.dataset.pager===key);b.setAttribute('aria-current',String(b.dataset.pager===key))});
    active=key||null;
  }
  async function goto(key,{history=true,instant=false}={}){
    if(busy){queuedKey=key;return;}
    if(key===active||!$('[data-world]'))return;
    if(key&&!chapters.includes(key))return;
    busy=true;
    const update=()=>{
      setRoomSync(key);
      if(history){const base=$('[data-world]').dataset.base||'/';window.history.pushState({chapter:key},'',key?'#'+key:'#');}
    };
    if(instant){update()}else await curtain(update);
    const focus=key?$('.room.is-visible .room-top button'):$('.directory-link');
    if(focus)focus.focus({preventScroll:true});
    busy=false;
    if(queuedKey!==undefined){const next=queuedKey;queuedKey=undefined;if(next!==active)goto(next)}
  }
  function refresh(){
    const w=$('[data-world]');if(!w)return;
    artClean();artClean=()=>{};homeRoot=w;active=null;queuedKey=undefined;busy=false;
    const hash=location.hash.slice(1);
    setRoomSync(chapters.includes(hash)?hash:null);
    artClean=initializeArt(w);
  }
  window.initWorld=refresh;
  let menuAnimation=null;
  async function setMenu(open,{focus=true,instant=false}={}){
    const m=$('[data-world-map]'),toggle=$('[data-map-toggle]');if(!m)return;
    if(menuAnimation){
      // Start from the actual position when a rapid tap reverses the curtain.
      m.style.clipPath=getComputedStyle(m).clipPath;
      menuAnimation.cancel();menuAnimation=null;
    }
    const wasOpen=menuOpen;menuOpen=open;
    m.style.visibility='visible';
    toggle.setAttribute('aria-expanded',String(open));
    document.body.classList.toggle('map-open',open);
    if(open){m.inert=false;m.setAttribute('aria-hidden','false')}
    const from=m.style.clipPath|| (wasOpen?'inset(0 0 0 0)':'inset(0 0 100% 0)');
    const to=open?'inset(0 0 0 0)':'inset(0 0 100% 0)';
    if(!instant&&!reduce.matches){
      const anim=m.animate([{clipPath:from},{clipPath:to}],{duration:open?570:470,easing:EASE,fill:'both'});
      menuAnimation=anim;
      try{await anim.finished}catch{return}
      if(menuAnimation!==anim)return;
      menuAnimation=null;m.style.clipPath=to;anim.cancel();
    } else m.style.clipPath=to;
    if(!open){m.style.visibility='hidden';m.inert=true;m.setAttribute('aria-hidden','true');if(focus)toggle.focus({preventScroll:true})}
    else if(focus)$('nav a',m)?.focus({preventScroll:true});
  }
  const openMenu=()=>setMenu(true);
  const closeMenu=(options={})=>setMenu(false,options);
  document.addEventListener('click',e=>{
    const toggle=e.target.closest('[data-map-toggle]');if(toggle){menuOpen?closeMenu():openMenu();return}
    const clos=e.target.closest('[data-room-close]');if(clos){goto(null);return}
    const pager=e.target.closest('[data-pager]');if(pager){goto(pager.dataset.pager);return}
    const link=e.target.closest('[data-room-link],[data-map-dest]');if(!link)return;
    const key=link.dataset.roomLink||link.dataset.mapDest;
    if(!$('[data-world]')){if(menuOpen)closeMenu({focus:false,instant:true});return;}
    e.preventDefault();
    if(menuOpen){closeMenu({focus:false,instant:true})}
    goto(key);
  });
  document.addEventListener('pointerover',e=>{
    const link=e.target.closest('[data-preview]');if(!link)return;
    $$('.directory-link').forEach(n=>n.dataset.active=String(n===link));
    const art=$('[data-directory-art]');if(art)art.dataset.palette=link.dataset.preview;
  });
  document.addEventListener('focusin',e=>{
    const link=e.target.closest('[data-preview]');if(link){$$('.directory-link').forEach(n=>n.dataset.active=String(n===link));const art=$('[data-directory-art]');if(art)art.dataset.palette=link.dataset.preview}
  });
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){if(menuOpen){e.preventDefault();closeMenu()}else if(active){e.preventDefault();goto(null)}return}
    if(menuOpen&&e.key==='Tab'){
      const items=[$('[data-map-toggle]'),...$$('.map-destinations a')];const at=items.indexOf(document.activeElement);
      if(e.shiftKey&&at===0){e.preventDefault();items.at(-1).focus()}
      else if(!e.shiftKey&&at===items.length-1){e.preventDefault();items[0].focus()}
    }
    if(!menuOpen&&active&&(e.key==='ArrowLeft'||e.key==='ArrowRight')&&!/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)){
      e.preventDefault();let i=chapters.indexOf(active)+(e.key==='ArrowRight'?1:-1);
      goto(chapters[(i+chapters.length)%chapters]);
    }
  });
  // No chapter swipe navigation: phone swipes should scroll content normally.
  window.addEventListener('popstate',()=>{if($('[data-world]'))goto(chapters.includes(location.hash.slice(1))?location.hash.slice(1):null,{history:false,instant:true})});
  window.addEventListener('hashchange',()=>{if($('[data-world]')&&!location.hash.startsWith('#/'))goto(chapters.includes(location.hash.slice(1))?location.hash.slice(1):null,{history:false,instant:true})});
  /* An interference sculpture: radial engraved rings with independent phase and
     parallax. Frames are drawn, never captured from a reference site. */
  function initializeArt(root){
    const canvas=$('[data-directory-art]',root),music=$('[data-music-art]',root);
    if(!canvas)return ()=>{};
    const ctx=canvas.getContext('2d',{alpha:true});if(!ctx)return ()=>{};
    const mctx=music?.getContext('2d',{alpha:true});
    let running=true,frame=0,mouse={x:0,y:0},target={x:0,y:0},current=[199,254,145],ripple=null;
    const resize=(el)=>{
      if(!el)return null;
      const rect=el.getBoundingClientRect();
      const ratio=Math.min(devicePixelRatio||1,1.6);
      const w=Math.max(1,Math.round(rect.width*ratio)),h=Math.max(1,Math.round(rect.height*ratio));
      if(el.width!==w||el.height!==h){el.width=w;el.height=h}
      return {w,h,ratio};
    };
    function pointer(e){
      const r=canvas.getBoundingClientRect();target.x=(e.clientX-r.left)/Math.max(r.width,1)-.5;target.y=(e.clientY-r.top)/Math.max(r.height,1)-.5;
    }
    function tap(e){
      const r=canvas.getBoundingClientRect();ripple={x:(e.clientX-r.left)/r.width,y:(e.clientY-r.top)/r.height,t:performance.now()};
    }
    const dir=$('[data-directory]',root);
    dir?.addEventListener('pointermove',pointer,{passive:true});dir?.addEventListener('pointerdown',tap,{passive:true});
    function draw(t){
      const d=resize(canvas);if(!d)return;
      const {w,h}=d;ctx.clearRect(0,0,w,h);
      mouse.x+=(target.x-mouse.x)*.048;mouse.y+=(target.y-mouse.y)*.048;
      const col=palette[canvas.dataset.palette||'systems'];current=current.map((v,i)=>v+(col[i]-v)*.032);
      const [r,g,b]=current.map(Math.round);
      const cx=w*.60+mouse.x*w*.10,cy=h*.51+mouse.y*h*.075;
      ctx.save();ctx.translate(cx,cy);ctx.rotate(-.32+mouse.x*.23);
      /* etched torsion: high-density elliptical engraved bands */
      const lines=100;
      for(let i=lines;i>=0;i--){
        const f=i/lines,phase=t*.00018;
        const rx=w*(.06+.35*f),ry=h*(.065+.39*f);
        const skew=Math.sin(i*.095+phase)*.25;
        ctx.save();ctx.rotate(skew+Math.cos(phase+i*.03)*.075);
        ctx.beginPath();ctx.ellipse(Math.sin(i*.066+phase)*12*f,Math.cos(i*.058+phase)*10*f,rx,ry,0,0,Math.PI*2);
        ctx.strokeStyle=`rgba(${r},${g},${b},${Math.max(.035,.32-.23*f)})`;
        ctx.lineWidth=(i%10===0?1.35:.66)*d.ratio;
        ctx.stroke();ctx.restore();
      }
      /* irregular light seam crossing the etched volume */
      const grd=ctx.createLinearGradient(-w*.4,-h*.15,w*.4,h*.14);
      grd.addColorStop(0,`rgba(${r},${g},${b},0)`);grd.addColorStop(.45,`rgba(${r},${g},${b},.09)`);grd.addColorStop(.52,'rgba(245,248,233,.21)');grd.addColorStop(.6,`rgba(${r},${g},${b},.07)`);grd.addColorStop(1,`rgba(${r},${g},${b},0)`);
      ctx.fillStyle=grd;ctx.beginPath();ctx.ellipse(0,0,w*.38,h*.29,0,0,Math.PI*2);ctx.fill();
      ctx.restore();
      if(ripple){const age=Math.max(0,(t-ripple.t)/900);if(age>1)ripple=null;else{
        ctx.strokeStyle=`rgba(${r},${g},${b},${(1-age)*.7})`;ctx.lineWidth=(2-age)*d.ratio;
        ctx.beginPath();ctx.arc(ripple.x*w,ripple.y*h,age*Math.max(w,h)*.6,0,Math.PI*2);ctx.stroke();
      }}
    }
    function musicDraw(t){
      if(!music||!mctx)return;const d=resize(music);if(!d)return;
      const {w,h}=d;mctx.clearRect(0,0,w,h);
      mctx.strokeStyle='rgba(255,195,183,.17)';mctx.lineWidth=1*d.ratio;
      for(let i=0;i<12;i++){const y=(i+.6)*h/12;mctx.beginPath();mctx.moveTo(0,y);mctx.lineTo(w,y);mctx.stroke()}
      const keys=[2,5,7,3,9,10,4,2,8,1,5,7,10,6,3,2,5,8,4,9,6,3];
      const block=w/keys.length;
      keys.forEach((key,i)=>{
        const y=(key+.7)*h/12,x=i*block+(t*.03%(block*2));const len=block*(1.2+((i*7)%5)*.34);
        const grad=mctx.createLinearGradient(x,y,x+len,y);grad.addColorStop(0,'rgba(245,198,182,.03)');grad.addColorStop(.4,'rgba(252,196,177,.85)');grad.addColorStop(1,'rgba(252,196,177,.08)');
        mctx.fillStyle=grad;mctx.fillRect(x%w,y-3*d.ratio,len,6*d.ratio);
        mctx.fillStyle='rgba(255,234,220,.08)';mctx.fillRect((x+len*.7)%w,y+3*d.ratio,1*d.ratio,h/5);
      });
      const line=(t*.076)%w;
      mctx.strokeStyle='rgba(255,220,210,.8)';mctx.lineWidth=1.5*d.ratio;mctx.beginPath();mctx.moveTo(line,0);mctx.lineTo(line,h);mctx.stroke();
    }
    const tick=t=>{if(!running)return;frame++;if(!document.hidden&&frame%2===0){draw(t);musicDraw(t)}if(!reduce.matches)requestAnimationFrame(tick)};
    if(reduce.matches){draw(0);musicDraw(0)}else requestAnimationFrame(tick);
    return ()=>{running=false;dir?.removeEventListener('pointermove',pointer);dir?.removeEventListener('pointerdown',tap)};
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',refresh);else refresh();
})();
