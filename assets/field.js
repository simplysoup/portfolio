/* Atelier field / original generative artwork. No reference-site source or assets.
 * A motion study combining a slowly evolving polar point cloud with spring
 * following, impulse waves and touch input. 2D canvas, offscreen pause, no network.
 */
(function(){
  'use strict';
  const TAU = Math.PI*2;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  let cleanup=()=>{};
  function initializeField(){
    cleanup();
    const hero=document.querySelector('[data-hero-scene]');
    const canvas=hero?.querySelector('[data-field-study]');
    if(!canvas)return;
    const plate=canvas.closest('.artwork-plate');
    const ctx=canvas.getContext('2d',{alpha:true});
    if(!ctx)return;
    const media=window.matchMedia('(prefers-reduced-motion: reduce)');
    const coarse=window.matchMedia('(pointer: coarse)').matches;
    const state={x:.5,y:.5,vx:0,vy:0,tx:.5,ty:.5,energy:0,active:false,pressed:false,touch:false};
    const impulses=[];
    let side=0,raf=0,frame=0,last=0,time=0,visible=true,destroyed=false,ro,io;
    canvas.dataset.ready='1';
    canvas.dataset.pointerActive='false';
    canvas.dataset.mode=media.matches?'reduced':'idle';
    // Fix maximum pixel count for mobile GPU memory and slower screens.
    function resize(){
      const rect=plate.getBoundingClientRect();
      side=Math.max(1,Math.round(rect.width));
      const dpr=Math.min(window.devicePixelRatio||1,coarse?1.5:2);
      canvas.width=Math.round(side*dpr);
      canvas.height=Math.round(side*dpr);
      ctx.setTransform(dpr,0,0,dpr,0,0);
      draw();
    }
    function spring(axis,target,velocity,dt){
      // Critically damped-ish follower with timestep-independent integration.
      const force=(target-axis)*72-velocity*17;
      velocity+=force*dt;
      axis+=velocity*dt;
      return [axis,velocity];
    }
    function disturb(x,y,power=1){
      // CSS ring is a second channel of visual feedback. On touch screens,
      // it confirms immediately that the action registered, independently of
      // the lower-contrast procedural point-field drawing.
      if(!media.matches){
        const ring=document.createElement('span');ring.className='field-impact';
        ring.style.left=`${(x*100).toFixed(2)}%`;ring.style.top=`${(y*100).toFixed(2)}%`;
        plate.appendChild(ring);setTimeout(()=>ring.remove(),1000);
      }
      impulses.push({x,y,born:time,power});
      while(impulses.length>4)impulses.shift();
      state.energy=Math.max(state.energy,.95*power);
      schedule();
    }
    function draw(){
      if(!side)return;
      const w=side, h=side, cx=w/2,cy=h/2,scale=w/640;
      ctx.clearRect(0,0,w,h);
      const mx=state.x*w,my=state.y*h;
      const coarseDetail=(coarse&&w<520);
      const count=coarseDetail?36:48;
      // Soft illumination tracks the active wave without altering static layout.
      const shine=ctx.createRadialGradient(cx+Math.sin(time*.17)*w*.045,cy+Math.cos(time*.21)*w*.038,w*.04,cx,cy,w*.46);
      shine.addColorStop(0,'rgba(74,112,138,.11)');shine.addColorStop(.6,'rgba(37,68,95,.045)');shine.addColorStop(1,'rgba(20,36,48,0)');
      ctx.fillStyle=shine;ctx.beginPath();ctx.arc(cx,cy,w*.49,0,TAU);ctx.fill();
      let ambient=0;
      for(let ring=0;ring<count;ring++){
        const q=ring/(count-1), radius=(50+445*q)*scale;
        const points=Math.round((coarseDetail?56:68)+q*(coarseDetail?20:55));
        const shift=time*.11;
        const baseWobble=1.0+.035*Math.sin(shift+ring*.18);
        for(let j=0;j<points;j++){
          const angle=TAU*j/points,ca=Math.cos(angle),sa=Math.sin(angle);
          const angular=16*Math.sin(angle*3+ring*.082+time*.16)+6*Math.cos(angle*7-ring*.105-time*.11)+10*Math.sin(angle*2+ring*.046+time*.08);
          const r=(radius+angular*scale)*baseWobble;
          let x=cx+r*ca*1.025, y=cy+r*sa*.92;
          // Lagrangian warp: near the pointer, points bend through a local field.
          const dx=x-mx,dy=y-my;
          const falloff=Math.exp(-(dx*dx+dy*dy)/(2*Math.pow(118*scale,2)));
          const pressure=falloff*(state.energy*.37+(state.active?.29:0));
          x+=dx*pressure;y+=dy*pressure;
          // A propagating wave from each touch/tap, decaying in time and space.
          let kick=0;
          for(const wave of impulses){
            const age=time-wave.born;if(age>2.2)continue;
            const distance=Math.hypot(x-wave.x*w,y-wave.y*h);
            const front=age*w*.65;
            kick+=Math.sin((distance-front)/(17*scale))*Math.exp(-Math.pow((distance-front)/(64*scale),2))*Math.exp(-age*.8)*wave.power*23*scale;
          }
          x+=ca*kick;y+=sa*kick;
          // Slow global drift makes the field feel alive even without mouse input.
          const drift=(Math.sin(time*.43+q*9+angle*4.3)+Math.cos(time*.22+angle*6-q*11))*1.5*scale;
          x+=drift*ca;y+=drift*sa;
          const shimmer=.77+.23*Math.sin(angle*4.5+q*9-time*.63);
          const opacity=(.11+q*.22+pressure*.4)*shimmer;
          if(ring%10===0){ctx.fillStyle=`rgba(217,239,139,${(opacity+.09).toFixed(3)})`}
          else if(ring%4===0){ctx.fillStyle=`rgba(128,152,255,${(opacity+.035).toFixed(3)})`}
          else{ctx.fillStyle=`rgba(198,219,226,${opacity.toFixed(3)})`}
          const d=(ring%10===0?1.9:1.1)*scale+(pressure*.85*scale);
          ctx.fillRect(x,y,Math.max(.65,d),Math.max(.65,d));
          ambient+=opacity;
        }
      }
      // Draw visible traveling wavefronts. An earlier version displaced dots,
      // but the change was too subtle to read on a small touchscreen.
      for(const wave of impulses){
        const age=time-wave.born;
        if(age<=0 || age>1.7)continue;
        const radius=age*w*.54;
        const opacity=Math.pow(1-age/1.7,1.6)*.45*wave.power;
        ctx.beginPath();ctx.arc(wave.x*w,wave.y*h,radius,0,TAU);
        ctx.strokeStyle=`rgba(217,239,139,${opacity.toFixed(3)})`;
        ctx.lineWidth=Math.max(.9,2.25*scale)*(1+age*.25);ctx.stroke();
      }
      // Three tiny focal points; the viewer's eye has a stable anchor.
      ctx.shadowColor='rgba(217,239,139,.65)';ctx.shadowBlur=9*scale;
      ctx.fillStyle='#D9EF8B';ctx.beginPath();ctx.arc(cx,cy,Math.max(1.2,2*scale),0,TAU);ctx.fill();
      ctx.shadowBlur=0;
      canvas.dataset.frame=String(++frame);
      canvas.dataset.energy=state.energy.toFixed(3);
    }
    function step(now){
      raf=0;
      if(destroyed||!canvas.isConnected||!visible||document.hidden||media.matches)return;
      // 30fps on coarse pointers, 60fps otherwise; dt capped after tab switches.
      const minMs=coarse?31:15;
      if(last&&now-last<minMs){raf=requestAnimationFrame(step);return;}
      const dt=Math.min(.05,(now-(last||now-16))/1000);last=now;time+=dt;
      [state.x,state.vx]=spring(state.x,state.tx,state.vx,dt);
      [state.y,state.vy]=spring(state.y,state.ty,state.vy,dt);
      state.energy=Math.max(0,state.energy-dt*.45);
      for(let i=impulses.length-1;i>=0;i--)if(time-impulses[i].born>2.2)impulses.splice(i,1);
      draw();raf=requestAnimationFrame(step);
    }
    function schedule(){if(!raf&&visible&&!document.hidden&&!media.matches)raf=requestAnimationFrame(step)}
    function updatePosition(e){
      const rect=plate.getBoundingClientRect();
      state.tx=clamp((e.clientX-rect.left)/Math.max(1,rect.width),.12,.88);
      state.ty=clamp((e.clientY-rect.top)/Math.max(1,rect.height),.12,.88);
      state.active=true;
      canvas.dataset.pointerActive='true';
      canvas.dataset.mode=e.pointerType==='touch'?'touch':'pointer';
      schedule();
    }
    function mouseMove(e){
      if(media.matches||e.pointerType==='touch')return;
      updatePosition(e);
    }
    function touchDown(e){
      if(media.matches)return;
      updatePosition(e);
      state.touch=e.pointerType==='touch';state.pressed=true;
      disturb(state.tx,state.ty,1.3);
      canvas.dataset.touchCount=String((+canvas.dataset.touchCount||0)+1);
    }
    function touchMove(e){if(media.matches)return;if(e.pointerType==='touch'&&state.pressed)updatePosition(e)}
    function touchUp(){state.pressed=false;state.touch=false;state.active=false;state.tx=.5;state.ty=.5;canvas.dataset.pointerActive='false';canvas.dataset.mode='idle'}
    function keyActivate(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();if(media.matches)return;disturb(.5,.5,1.5);canvas.dataset.mode='keyboard'}}
    function buttonActivate(){if(media.matches)return;disturb(.5,.5,1.5);canvas.dataset.mode='button'}
    const button=plate.querySelector('[data-field-pulse]');
    hero.addEventListener('pointermove',mouseMove,{passive:true});
    plate.addEventListener('pointerdown',touchDown,{passive:true});
    plate.addEventListener('pointermove',touchMove,{passive:true});
    plate.addEventListener('pointerup',touchUp,{passive:true});
    plate.addEventListener('pointercancel',touchUp,{passive:true});
    hero.addEventListener('pointerleave',touchUp,{passive:true});
    if(button)button.addEventListener('click',buttonActivate);
    if('ResizeObserver' in window){ro=new ResizeObserver(resize);ro.observe(plate)}else window.addEventListener('resize',resize);
    if('IntersectionObserver' in window){io=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible){last=0;schedule()}else if(raf){cancelAnimationFrame(raf);raf=0}},{threshold:0});io.observe(hero)}
    const onVisibility=()=>{if(document.hidden){cancelAnimationFrame(raf);raf=0}else{last=0;schedule()}};
    document.addEventListener('visibilitychange',onVisibility);
    const onMotion=()=>{canvas.dataset.mode=media.matches?'reduced':'idle';if(media.matches){cancelAnimationFrame(raf);raf=0;time=0;state.energy=0;impulses.length=0;draw()}else schedule()};
    media.addEventListener?.('change',onMotion);
    resize();schedule();
    cleanup=()=>{
      destroyed=true;cancelAnimationFrame(raf);ro?.disconnect();io?.disconnect();
      hero.removeEventListener('pointermove',mouseMove);
      hero.removeEventListener('pointerleave',touchUp);
      plate.removeEventListener('pointerdown',touchDown);
      plate.removeEventListener('pointermove',touchMove);
      plate.removeEventListener('pointerup',touchUp);
      plate.removeEventListener('pointercancel',touchUp);
      button?.removeEventListener('click',buttonActivate);
      document.removeEventListener('visibilitychange',onVisibility);
      media.removeEventListener?.('change',onMotion);
    };
  }
  window.initializeField=initializeField;
  window.destroyField=()=>cleanup();
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initializeField);
  else initializeField();
})();
