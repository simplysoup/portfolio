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
    window.setMusicSceneActive?.(key==='music');
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
    const shortcut=e.target.closest('[data-showcase-link]');
    if(shortcut){if(menuOpen)closeMenu({focus:false,instant:true});return;}
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
    let running=true,frame=0,animationFrame=0,mouse={x:0,y:0},target={x:0,y:0},current=[199,254,145],ripple=null;
    let musicActive=false,musicPhase=0,musicLast=0;
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
    /* Piano roll / stable, seamless, viewport-relative timeline.
       The former x%width wrapping introduced abrupt jumps and gradients painted
       outside their bars. Notes now repeat on a single musical cycle; the view
       scrolls through that cycle without discontinuities or hidden-canvas paints. */
    const musicEvents=Array.from({length:40},(_,i)=>({
      beat:i*.72+(i%6===3?.18:0),
      row:[3,7,10,8,5,12,4,9,6,11,3,14,7,5,2,10][i%16],
      duration:[.44,1.12,.72,.57,1.4,.85][i%6],
      strength:.62+(i%5)*.085
    }));
    const cycle=musicEvents.length*.72;
    function musicDraw(t){
      if(!musicActive||!music||!mctx)return;
      const rect=music.getBoundingClientRect();
      if(rect.width<8||rect.height<8)return;
      const d=resize(music);if(!d)return;
      const W=d.w/d.ratio,H=d.h/d.ratio;
      mctx.setTransform(d.ratio,0,0,d.ratio,0,0);
      mctx.clearRect(0,0,W,H);
      const keyW=Math.max(33,Math.min(54,W*.09));
      const top=29,bottom=24,rows=16,rowH=(H-top-bottom)/rows;
      const pxPerBeat=Math.max(42,Math.min(86,W*.11));
      const total=cycle*pxPerBeat;
      const scroll=musicPhase*pxPerBeat;
      mctx.fillStyle='#241820';mctx.fillRect(0,0,W,H);
      // A quiet piano keyboard and horizontal staff, independent of timeline.
      for(let r=0;r<rows;r++){
        const y=top+r*rowH;
        mctx.fillStyle=r%2===0?'rgba(255,222,215,.047)':'rgba(255,222,215,.018)';
        mctx.fillRect(keyW,y,W-keyW,rowH);
        mctx.fillStyle=r%5===2?'#665059':'#d5bcb7';
        mctx.globalAlpha=r%5===2?.95:.62;
        mctx.fillRect(0,y,keyW-3,rowH-1);
        mctx.globalAlpha=1;
        mctx.strokeStyle='rgba(255,210,205,.13)';mctx.lineWidth=.7;
        mctx.beginPath();mctx.moveTo(keyW,y+.5);mctx.lineTo(W,y+.5);mctx.stroke();
      }
      mctx.fillStyle='rgba(255,226,220,.7)';mctx.font='10px monospace';
      mctx.fillText('C5',5,top+4*rowH+.7*rowH);
      mctx.fillText('C4',5,top+11*rowH+.7*rowH);
      mctx.save();mctx.beginPath();mctx.rect(keyW,top,W-keyW,H-top-bottom);mctx.clip();
      const firstBar=Math.floor(scroll/(4*pxPerBeat))-1;
      for(let b=firstBar;b<firstBar+Math.ceil(W/(4*pxPerBeat))+3;b++){
        const x=keyW+b*4*pxPerBeat-scroll;
        mctx.strokeStyle='rgba(255,224,218,.22)';mctx.lineWidth=1;
        mctx.beginPath();mctx.moveTo(x,top);mctx.lineTo(x,H-bottom);mctx.stroke();
      }
      // Draw the same score at neighboring cycle offsets. No modulo at the edge.
      const startCycle=Math.floor(scroll/total)-1;
      for(let c=startCycle;c<startCycle+4;c++){
        for(const n of musicEvents){
          const x=keyW+c*total+n.beat*pxPerBeat-scroll;
          const width=n.duration*pxPerBeat;
          if(x+width<keyW||x>W)continue;
          const y=top+n.row*rowH+rowH*.17,h=rowH*.66;
          mctx.fillStyle=`rgba(245,168,159,${n.strength})`;
          mctx.fillRect(x,y,Math.max(3,width-2),h);
          mctx.fillStyle='rgba(255,235,219,.48)';
          mctx.fillRect(x,y,Math.max(3,width-2),Math.min(1.4,h*.14));
        }
      }
      mctx.restore();
      // Fixed read-head; subtle illumination only when an event crosses.
      const playX=keyW+(W-keyW)*.48;
      const glow=mctx.createLinearGradient(playX-16,0,playX+16,0);
      glow.addColorStop(0,'rgba(255,208,185,0)');glow.addColorStop(.5,'rgba(255,225,194,.13)');glow.addColorStop(1,'rgba(255,208,185,0)');
      mctx.fillStyle=glow;mctx.fillRect(playX,top,18,H-top-bottom);
      mctx.strokeStyle='rgba(255,238,214,.82)';mctx.lineWidth=1.25;
      mctx.beginPath();mctx.moveTo(playX,top);mctx.lineTo(playX,H-bottom);mctx.stroke();
    }
    function setMusicActive(on){
      if(on===musicActive)return;
      musicActive=on;musicLast=performance.now();
      if(on)musicDraw(musicLast);
    }
    window.setMusicSceneActive=setMusicActive;
    const tick=t=>{
      if(!running)return;
      frame++;
      if(!document.hidden){
        if(frame%2===0&&active===null)draw(t);
        if(musicActive){
          const delta=Math.min(80,Math.max(0,t-musicLast));
          musicLast=t;
          if(frame%2===0){musicPhase=(musicPhase+delta*.00043)%cycle;musicDraw(t)}
        }
      }else musicLast=t;
      if(!reduce.matches)animationFrame=requestAnimationFrame(tick);
    };
    if(active==='music')setMusicActive(true);
    if(reduce.matches){draw(0);if(musicActive)musicDraw(0)}
    else animationFrame=requestAnimationFrame(tick);
    return ()=>{
      running=false;cancelAnimationFrame(animationFrame);
      if(window.setMusicSceneActive===setMusicActive)delete window.setMusicSceneActive;
      dir?.removeEventListener('pointermove',pointer);
      dir?.removeEventListener('pointerdown',tap);
    };
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',refresh);else refresh();
})();
