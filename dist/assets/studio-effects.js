/* Kinetic type / coupling a purposeful strip to scroll velocity.
   Original implementation of a general motion-design principle, without Lenis or scroll-jacking. */
(()=>{
 'use strict';
 const strip=document.querySelector('.kinetic-strip');
 const track=document.querySelector('[data-kinetic-track]');
 if(!strip||!track)return;
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
 let x=0,velocity=0,lastY=window.scrollY,last=performance.now(),active=true,raf=0;
 window.addEventListener('scroll',()=>{
   const dy=window.scrollY-lastY;lastY=window.scrollY;
   velocity=Math.max(-32,Math.min(32,velocity+dy*.42));
 },{passive:true});
 function frame(now){
   raf=0;
   if(!active||reduced.matches)return;
   const dt=Math.min(.07,(now-last)/1000||.016);last=now;
   velocity*=Math.exp(-dt*4.4);
   x+=(18+velocity*4.3)*dt;
   const width=track.scrollWidth/3;
   if(width>0){x=(x+width*2)%width;track.style.transform=`translate3d(${-x}px,0,0) skewX(${Math.max(-5,Math.min(5,velocity*.14)).toFixed(2)}deg)`;}
   raf=requestAnimationFrame(frame);
 }
 const observer=new IntersectionObserver(entries=>{
   active=entries[0].isIntersecting;
   if(active&&!raf){last=performance.now();raf=requestAnimationFrame(frame);}
   else if(!active&&raf){cancelAnimationFrame(raf);raf=0;}
 },{threshold:0});observer.observe(strip);
 if(!reduced.matches){raf=requestAnimationFrame(frame);}
 // Explicitly avoid intercepting wheel/touch input: native scroll remains accessible.
})();
