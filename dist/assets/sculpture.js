/* FORM STUDY / 001 — an original lightweight 3D ribbon.
   A parametric fold rendered with a small WebGL2 vertex/fragment shader.
   No ray marching, external assets, borrowed shaders, or hover-only controls.
   Cubic spring following is independent of the masked text / page easing.
*/
(()=>{
  'use strict';
  const VS=`#version 300 es
  precision highp float;
  in vec2 aUV;
  uniform float uTime;
  uniform vec2 uAngle;
  uniform float uImpulse;
  out vec3 vWorld;
  out vec2 vUV;
  const float PI=3.14159265359;
  mat3 rx(float a){float c=cos(a),s=sin(a);return mat3(1.,0.,0.,0.,c,-s,0.,s,c);}
  mat3 ry(float a){float c=cos(a),s=sin(a);return mat3(c,0.,s,0.,1.,0.,-s,0.,c);}
  void main(){
    float u=aUV.x*2.*PI, v=aUV.y*2.-1.;
    float t=uTime*.30;
    float twist=2.9*u+t;
    float flap=v*.50*cos(twist);
    float breathing=1.+.025*sin(u*3.-uTime*.65);
    float wave=uImpulse*.15*sin(u*8.-uTime*7.)*exp(-abs(v)*.7);
    float r=(1.05+flap+wave)*breathing;
    vec3 p=vec3(r*cos(u), .72*sin(u)+v*.53*sin(twist)+.12*cos(4.*u+t),
      .7*r*sin(u)+.20*sin(u*3.+t*.67));
    p=ry(.24+uAngle.x)*rx(-.24+uAngle.y)*p;
    vWorld=p;vUV=aUV;
    gl_Position=vec4(p.x*.61,p.y*.66,p.z*.18,1.);
  }`;
  const FS=`#version 300 es
  precision highp float;
  in vec3 vWorld;
  in vec2 vUV;
  uniform float uTime;
  uniform float uImpulse;
  out vec4 fragColor;
  float hash(vec2 x){return fract(sin(dot(x,vec2(127.1,311.7)))*43758.5453);}
  void main(){
    vec3 n=normalize(cross(dFdx(vWorld),dFdy(vWorld)));
    if(!gl_FrontFacing)n=-n;
    vec3 light=normalize(vec3(-.65,.82,1.12));
    float d=dot(n,light)*.5+.5;
    float shade=smoothstep(.08,.94,d);
    float edge=pow(1.-abs(n.z),2.1);
    float satin=.5+.5*sin(vUV.x*72.+vUV.y*18.);
    vec3 shadow=vec3(.21,.19,.48);       // indigo ink
    vec3 mid=vec3(.62,.59,.92);          // lilac
    vec3 cream=vec3(.98,.82,.67);        // warm pearl
    vec3 ember=vec3(1.,.40,.28);        // vermilion edge
    vec3 c=mix(shadow,mid,shade);
    c=mix(c,cream,smoothstep(.47,.92,shade)*.78);
    c=mix(c,ember,clamp(edge*.82 + uImpulse*.17,0.,.6));
    float highlights=pow(max(0.,dot(reflect(-light,n),vec3(0.,0.,1.))),19.);
    c+=highlights*vec3(.22,.25,.20);
    c*=.94+.06*satin;
    // A fine ink stipple: physical print texture, not a pixelated cartoon.
    float grain=hash(floor(gl_FragCoord.xy*.65)+fract(uTime*.07)*19.);
    float ink=.96+.04*step(.20,grain);
    c*=ink;
    fragColor=vec4(c,1.);
  }`;
  let dispose=()=>{};
  function initialize(){
    dispose();
    const canvas=document.querySelector('[data-signal-sculpture]');
    if(!canvas)return;
    const plate=canvas.closest('[data-sculpture-interaction]');
    const reduce=matchMedia('(prefers-reduced-motion: reduce)');
    const controller=new AbortController();
    const {signal}=controller;
    let gl=null,uniforms=null,indexCount=0,ctx=null;
    let active=true,frameId=0,lastDraw=0,first=true;
    let target={x:0,y:0},smoothed={x:0,y:0},energy=0,dragging=false,interactionCount=0;
    const metadata={mode:'idle',interactions:0,renderer:'fallback'};
    function compile(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
    try{
      gl=canvas.getContext('webgl2',{alpha:true,antialias:true,depth:true,powerPreference:'low-power',preserveDrawingBuffer:true});
      if(!gl)throw Error('WebGL2 unavailable');
      const prog=gl.createProgram();gl.attachShader(prog,compile(gl.VERTEX_SHADER,VS));gl.attachShader(prog,compile(gl.FRAGMENT_SHADER,FS));gl.linkProgram(prog);
      if(!gl.getProgramParameter(prog,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(prog));
      gl.useProgram(prog);
      const nx=172,ny=38,vertices=[],indices=[];
      for(let i=0;i<=nx;i++)for(let j=0;j<=ny;j++)vertices.push(i/nx,j/ny);
      for(let i=0;i<nx;i++)for(let j=0;j<ny;j++){
        const k=i*(ny+1)+j,l=k+ny+1;
        indices.push(k,l,k+1,k+1,l,l+1);
      }
      const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(vertices),gl.STATIC_DRAW);
      const attr=gl.getAttribLocation(prog,'aUV');gl.enableVertexAttribArray(attr);gl.vertexAttribPointer(attr,2,gl.FLOAT,false,0,0);
      const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(indices),gl.STATIC_DRAW);
      indexCount=indices.length;
      uniforms=Object.fromEntries(['uTime','uAngle','uImpulse'].map(k=>[k,gl.getUniformLocation(prog,k)]));
      gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.clearColor(0,0,0,0);
      metadata.renderer='webgl2';
    }catch(e){
      console.info('[Form study] lightweight 2D fallback:',e.message);
      gl=null;
      ctx=canvas.getContext('2d');
    }
    const sizeCanvas=()=>{
      const r=canvas.getBoundingClientRect();
      const dpr=Math.min(devicePixelRatio||1,1.35);
      const w=Math.max(1,Math.round(r.width*dpr)),h=Math.max(1,Math.round(r.height*dpr));
      if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
      if(gl)gl.viewport(0,0,w,h);
    };
    function drawFallback(t){
      if(!ctx)return;
      const w=canvas.width,h=canvas.height,s=Math.min(w,h);
      ctx.clearRect(0,0,w,h);ctx.save();ctx.translate(w*.5,h*.49);ctx.rotate(smoothed.x*.28 + energy*.11);
      const n=64;
      for(let i=n;i>=1;i--){
        const f=i/n,stretch=1.6-f*.75;
        ctx.beginPath();
        for(let j=0;j<=220;j++){
          let u=j/220*Math.PI*2;
          let twist=3*u+t*.3;
          let rad=(.22+.23*f)*(1+.3*Math.cos(twist)) + energy*.033*Math.sin(u*9-t*6)*Math.sin(f*Math.PI);
          let x=s*(rad*Math.cos(u)+.08*Math.sin(u*3+t*.4));
          let y=s*(rad*Math.sin(u)*.75 + .11*Math.sin(twist)*stretch) + smoothed.y*s*.055;
          if(j===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
        }
        ctx.closePath();
        let tone=i/n;
        ctx.strokeStyle=`hsla(${265+tone*80-energy*30},${65+tone*16}%,${66+tone*14+energy*2}%,${.16+tone*.65})`;
        ctx.lineWidth=1+2*tone;ctx.stroke();
      }
      ctx.restore();
    }
    let elapsed=0;
    function tick(now){
      if(!active)return;
      frameId=requestAnimationFrame(tick);
      if(document.hidden)return;
      // 30 fps cap to protect phones from decorative work.
      if(!first && now-lastDraw<32)return;
      let dt=Math.min((now-lastDraw)/1000||.033,.09);lastDraw=now;first=false;
      if(!reduce.matches)elapsed+=dt;
      const spring=1-Math.exp(-dt*5);
      smoothed.x+=(target.x-smoothed.x)*spring;
      smoothed.y+=(target.y-smoothed.y)*spring;
      energy*=Math.exp(-dt*1.7);
      sizeCanvas();
      if(gl){
        gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
        gl.uniform1f(uniforms.uTime,reduce.matches?0:elapsed);
        gl.uniform2f(uniforms.uAngle,smoothed.x,smoothed.y);
        gl.uniform1f(uniforms.uImpulse,reduce.matches?0:energy);
        gl.drawElements(gl.TRIANGLES,indexCount,gl.UNSIGNED_SHORT,0);
      }else drawFallback(reduce.matches?0:elapsed);
      canvas.dataset.rendered='true';canvas.dataset.renderer=metadata.renderer;plate.classList.add('is-rendered');
      canvas.dataset.interactions=String(interactionCount);
    }
    function relative(e){const r=plate.getBoundingClientRect();return {x:Math.max(-1,Math.min(1,(e.clientX-r.left)/r.width*2-1)),y:Math.max(-1,Math.min(1,1-(e.clientY-r.top)/r.height*2))};}
    function point(e){if(e.pointerType==='touch'&&!dragging)return;const p=relative(e);target.x=p.x*.92;target.y=p.y*.64;metadata.mode=e.pointerType==='touch'?'touch':'pointer';canvas.dataset.mode=metadata.mode;}
    function press(e){const p=relative(e);target.x=p.x*.92;target.y=p.y*.64;dragging=true;energy=1.65;interactionCount++;canvas.dataset.interactions=String(interactionCount);canvas.dataset.mode='touch';plate.classList.add('is-activated');
      const mark=document.createElement('span');mark.className='sculpture-ripple';mark.style.left=(p.x*.5+.5)*100+'%';mark.style.top=(.5-p.y*.5)*100+'%';mark.setAttribute('aria-hidden','true');plate.append(mark);setTimeout(()=>mark.remove(),1100);
    }
    plate.addEventListener('pointerdown',press,{signal,passive:true});
    plate.addEventListener('pointermove',point,{signal,passive:true});
    plate.addEventListener('pointerup',()=>dragging=false,{signal,passive:true});
    plate.addEventListener('pointercancel',()=>dragging=false,{signal,passive:true});
    plate.addEventListener('pointerleave',()=>{dragging=false;target.x=0;target.y=0;},{signal,passive:true});
    const button=plate.querySelector('[data-field-pulse]');
    if(button)button.addEventListener('click',e=>{
      e.stopPropagation();const b=plate.getBoundingClientRect();press({clientX:b.left+b.width*.54,clientY:b.top+b.height*.45});dragging=false;
    },{signal});
    plate.tabIndex=0;plate.setAttribute('role','group');plate.setAttribute('aria-label','Interactive generative ribbon. Tap, drag, or press Enter to move it.');
    plate.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target===plate){e.preventDefault();const b=plate.getBoundingClientRect();press({clientX:b.left+b.width*.5,clientY:b.top+b.height*.5});dragging=false;}},{signal});
    const observer=new IntersectionObserver(entries=>{
      const shouldBeActive=entries.some(e=>e.isIntersecting);
      if(shouldBeActive&&!active){active=true;first=true;frameId=requestAnimationFrame(tick);}
      else if(!shouldBeActive&&active){active=false;cancelAnimationFrame(frameId);}
    },{threshold:0});
    observer.observe(plate);
    canvas.dataset.mode=reduce.matches?'reduced':'idle';
    frameId=requestAnimationFrame(tick);
    dispose=()=>{active=false;cancelAnimationFrame(frameId);controller.abort();observer.disconnect();};
  }
  window.initSculpture=initialize;
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initialize,{once:true});
  else initialize();
})();
