/* Intentionally no third-party runtime: charts are small, synthetic and fully client-side. */
function initPortfolioExhibits() {
  'use strict';
  const root = document.querySelector('[data-exhibit="trend"]');
  if (root) initTrend(root);
  const rag = document.querySelector('[data-exhibit="rag"]');
  if (rag) initRag(rag);

  function initTrend(root) {
    root.innerHTML = `
      <div class="exhibit-top"><span class="exhibit-kicker">LAB 001 / TREND RELATIONSHIPS</span><span class="exhibit-badge">SYNTHETIC DATA · OLS ONLY</span></div>
      <div class="trend-grid">
        <div class="trend-plot"><svg viewBox="0 0 640 320" role="img" aria-label="Synthetic observations, global line fit, and optionally segmented line fits" id="trend-chart"></svg>
          <div class="trend-legend"><span>OBSERVATIONS</span><span class="legend-global">GLOBAL FIT</span><span class="legend-segment">TWO SEGMENTS</span></div>
          <p class="trend-caption">The split point is fixed at t = 0.55. The fit is computed with ordinary least squares; this is an explanatory toy, not thesis software.</p>
        </div>
        <div class="trend-controls">
          <div class="control-group"><label for="trend-noise">Observation noise <output id="noise-out">0.55</output></label><input type="range" id="trend-noise" min="0" max="1.8" step="0.05" value="0.55" /></div>
          <div class="control-group"><label for="trend-shift">Structural break <output id="shift-out">2.8</output></label><input type="range" id="trend-shift" min="-3" max="5" step="0.2" value="2.8" /></div>
          <div class="control-group"><label for="trend-tolerance">Residual tolerance <output id="tolerance-out">1.0</output></label><input type="range" id="trend-tolerance" min="0.2" max="3" step="0.1" value="1" /></div>
          <label class="check-row"><input type="checkbox" id="trend-segment" checked/> Show two-segment fit</label>
          <div class="trend-stats"><div class="trend-stat"><span>GLOBAL IN TOLERANCE</span><strong id="global-coverage">—</strong></div><div class="trend-stat"><span>SEGMENTED IN TOLERANCE</span><strong id="seg-coverage">—</strong></div></div>
          <p class="trend-caption" id="trend-insight" aria-live="polite">Choose a setting to compare fit residuals.</p>
        </div>
      </div>`;
    const chart = root.querySelector('#trend-chart');
    const noise = root.querySelector('#trend-noise');
    const shift = root.querySelector('#trend-shift');
    const tol = root.querySelector('#trend-tolerance');
    const segmented = root.querySelector('#trend-segment');
    const NS = 'http://www.w3.org/2000/svg';
    function element(tag, props = {}, parent = chart) {
      const el = document.createElementNS(NS, tag);
      Object.entries(props).forEach(([key, value]) => el.setAttribute(key, String(value)));
      parent.appendChild(el); return el;
    }
    function fit(points) {
      const n = points.length, mx=points.reduce((s,p)=>s+p[0],0)/n, my=points.reduce((s,p)=>s+p[1],0)/n;
      const v=points.reduce((s,p)=>s+(p[0]-mx)**2,0);
      const m=v ? points.reduce((s,p)=>s+(p[0]-mx)*(p[1]-my),0)/v : 0;
      return x => my + m*(x-mx);
    }
    function render() {
      const no = +noise.value, sh = +shift.value, threshold = +tol.value;
      root.querySelector('#noise-out').textContent=no.toFixed(2);
      root.querySelector('#shift-out').textContent=sh.toFixed(1);
      root.querySelector('#tolerance-out').textContent=threshold.toFixed(1);
      let seed=271828;
      const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
      const points=Array.from({length:100},(_,i)=>{const x=i/99;const e=((random()+random()+random())-1.5)*2.6*no;return [x,1.4+5*x+(x>=.55?sh:0)+e];});
      const globalFit=fit(points), leftFit=fit(points.filter(p=>p[0]<.55)),rightFit=fit(points.filter(p=>p[0]>=.55));
      const segFit=x=>x<.55?leftFit(x):rightFit(x);
      const percent=f=>Math.round(100*points.filter(p=>Math.abs(p[1]-f(p[0]))<=threshold).length/points.length);
      const g=percent(globalFit),s=percent(segFit);
      root.querySelector('#global-coverage').textContent=g+'%';
      root.querySelector('#seg-coverage').textContent=s+'%';
      root.querySelector('#trend-insight').textContent=segmented.checked
        ? `Under this invented residual test, splitting at the known breakpoint changes coverage by ${s-g>=0?'+':''}${s-g} percentage points. This does not validate an inferred changepoint.`
        : 'Segmented fit is hidden, but its coverage is still reported for comparison.';
      while(chart.firstChild)chart.removeChild(chart.firstChild);
      const xmin=34,xmax=618,ymin=17,ymax=278;
      const yvalues=[...points.map(p=>p[1]),globalFit(0),globalFit(1),leftFit(0),leftFit(.55),rightFit(.55),rightFit(1)];
      const ylo=Math.min(...yvalues)-.9,yhi=Math.max(...yvalues)+.9;
      const xx=x=>xmin+(xmax-xmin)*x, yy=y=>ymax-(y-ylo)/(yhi-ylo)*(ymax-ymin);
      for(let i=0;i<=5;i++){
        const x=xx(i/5),y=ymax-(ymax-ymin)*i/5;
        element('line',{x1:x,x2:x,y1:ymin,y2:ymax,stroke:'#35535a','stroke-width':.7});
        element('line',{x1:xmin,x2:xmax,y1:y,y2:y,stroke:'#35535a','stroke-width':.7});
      }
      element('line',{x1:xx(.55),x2:xx(.55),y1:ymin,y2:ymax,stroke:'#d5ed9a','stroke-dasharray':'3 6','stroke-width':1.2,opacity:.7});
      points.forEach(p=>element('circle',{cx:xx(p[0]),cy:yy(p[1]),r:2.6,fill:'#d5eea0',opacity:.85}));
      const path=(f,a,b,stroke,dash='')=>element('path',{d:`M ${xx(a).toFixed(1)} ${yy(f(a)).toFixed(1)} L ${xx(b).toFixed(1)} ${yy(f(b)).toFixed(1)}`,fill:'none',stroke,'stroke-width':3,'stroke-dasharray':dash});
      path(globalFit,0,1,'#8da1ff','7 5');
      if(segmented.checked){path(leftFit,0,.55,'#ebbc80');path(rightFit,.55,1,'#ebbc80');}
      const xaxis=element('text',{x:xx(.5),y:307,fill:'#a9c2bd','text-anchor':'middle','font-size':11,'font-family':'monospace'});xaxis.textContent='NORMALIZED TIME / t';
      const marker=element('text',{x:xx(.55)+6,y:13,fill:'#d5eea0','font-size':9,'font-family':'monospace'});marker.textContent='KNOWN SPLIT';
    }
    [noise,shift,tol,segmented].forEach(input=>input.addEventListener('input',render));render();
  }

  function initRag(root) {
    const cases = [
      {label:'Grounded answer',question:'When does the fictional library renovation begin?',source:'Sample memo [library-renovation#0]: “Renovation work begins on May 12.”',answer:'Renovation work begins on May 12. [library-renovation#0]',steps:[['Retrieve','The memo is found in the controlled corpus.','PASS'],['Draft','Answer quotes the retrieved sentence verbatim.','PASS'],['Validate','Citation exists and contains the answer.','PASS'],['Resolve','Return the cited answer.','ANSWER']]},
      {label:'Correction path',question:'What is the sample garden’s annual funding allocation?',source:'Sample memo [riverside-garden#2]: “The annual allocation is $18,000.”',answer:'The annual allocation is $18,000. [riverside-garden#2]',steps:[['Retrieve','Supporting passage is available.','PASS'],['Draft','Initial response paraphrases instead of quoting.','FLAG'],['Validate','Verbatim grounding check rejects draft.','RETRY'],['Correct once','Revised answer quotes the exact sentence.','PASS'],['Resolve','Return corrected cited text.','ANSWER']]},
      {label:'Abstention',question:'Who was the fictional museum’s building contractor?',source:'No retrieved sample passage names a contractor.',answer:'Insufficient supporting evidence — abstain.',steps:[['Retrieve','No passage supports the requested fact.','FLAG'],['Draft','No defensible citation is available.','FLAG'],['Validate','Answer cannot pass grounding.','FLAG'],['Resolve','Do not invent a contractor name.','ABSTAIN']]}
    ];
    root.innerHTML=`<div class="exhibit-top"><span class="exhibit-kicker">TRACE EXPLORER / EDUCATIONAL EXAMPLES</span><span class="exhibit-badge">NOT EXPORTED RUN LOGS</span></div><div class="trace-controls" role="group" aria-label="Choose a hypothetical trace">${cases.map((c,i)=>`<button class="trace-choice" type="button" data-case="${i}" aria-pressed="${i===0}">${String(i+1).padStart(2,'0')} / ${c.label}</button>`).join('')}</div><div class="trace-content"><div class="trace-surface"><span class="trace-label">QUESTION</span><h3 id="rag-question"></h3><div class="trace-label">RETRIEVED EVIDENCE</div><div class="trace-evidence" id="rag-source"></div><p class="trace-label" style="margin-top:25px">FINAL OUTPUT</p><p id="rag-answer"></p></div><div class="trace-steps"><div class="trace-label">EXECUTION PATH</div><div class="trace-list" id="rag-steps"></div></div></div><p class="trace-footnote">All text in this exhibit is invented to explain behavior; repository measurements are documented separately in the article. The real implementation and guardrail tests can be inspected in GitHub.</p>`;
    function show(i){const c=cases[i];root.querySelectorAll('[data-case]').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.case===i)));
      root.querySelector('#rag-question').textContent=c.question;root.querySelector('#rag-source').textContent=c.source;root.querySelector('#rag-answer').textContent=c.answer;
      root.querySelector('#rag-steps').replaceChildren(...c.steps.map((s,j)=>{const row=document.createElement('div');row.className='trace-step'; const num=document.createElement('span');num.textContent=String(j+1).padStart(2,'0');const info=document.createElement('div');const title=document.createElement('strong');title.textContent=s[0];const detail=document.createElement('p');detail.textContent=s[1];info.append(title,detail);const badge=document.createElement('b');badge.textContent=s[2];if(['FLAG','RETRY','ABSTAIN'].includes(s[2]))badge.className='flag';row.append(num,info,badge);return row;}));
    }
    root.querySelectorAll('[data-case]').forEach(button=>button.addEventListener('click',()=>show(+button.dataset.case)));show(0);
  }
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initPortfolioExhibits);
else initPortfolioExhibits();


