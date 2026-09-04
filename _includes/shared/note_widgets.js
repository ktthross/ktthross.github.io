/* Shared helpers for the note-reconstruction widgets: the fit explorer, the
   synth player and the score player.

   This file is included *inside* each widget's IIFE, so every name below stays
   local to that widget. Two widgets can therefore sit on the same page without
   colliding, and each keeps its own CSS-variable prefix (--nfe-, --msp-, --scp-). */

const isBlack = n => n.includes("#");
const short = n => n.split("/")[0];

function hx(h){ h=h.replace("#",""); if(h.length===3)h=h.split("").map(c=>c+c).join(""); return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]; }
function lerpHex(a,b,f){ const pa=hx(a),pb=hx(b); return `rgb(${Math.round(pa[0]+(pb[0]-pa[0])*f)},${Math.round(pa[1]+(pb[1]-pa[1])*f)},${Math.round(pa[2]+(pb[2]-pa[2])*f)})`; }

/* Five-stop heat ramp read off --<prefix>-h0..h4 on the widget root. Values are
   read per call so a theme flip is picked up without rebuilding anything. */
function makeHeatColor(root, prefix){
  const vars = [0,1,2,3,4].map(i => `--${prefix}-h${i}`);
  return t => {
    const S = vars.map(v => getComputedStyle(root).getPropertyValue(v).trim());
    t = Math.max(0,Math.min(1,t)); const seg=t*4, i=Math.min(3,Math.floor(seg)), f=seg-i;
    return lerpHex(S[i],S[i+1],f);
  };
}

/* Picks which coefficients survive the current cutoff. mode is "abs" (relative
   |coef| threshold), "topn" (a percentage of the vector) or "energy" (smallest
   set capturing that share of total energy). Returns the selected indices plus
   the stats both widgets display. */
function computeCoeffSelection(c, mode, cut){
  const mags = c.map(Math.abs), maxMag = Math.max(...mags);
  const totalEnergy = mags.reduce((s,m)=>s+m*m,0);
  const order = c.map((v,i)=>i).sort((a,b)=>mags[b]-mags[a]);
  let selectedIdx = new Set(), threshDesc = "";
  if(mode==="abs"){ const frac=cut.abs/100, t=frac*frac*maxMag; c.forEach((v,i)=>{ if(Math.abs(v)>=t) selectedIdx.add(i); }); threshDesc=t.toFixed(4); }
  else if(mode==="topn"){ const n=Math.max(0,Math.round(cut.topn/100*c.length)); for(let i=0;i<n;i++) selectedIdx.add(order[i]); threshDesc=n+" / "+c.length; }
  else { const target=cut.energy/100*totalEnergy; let acc=0; for(const i of order){ if(acc>=target) break; acc+=mags[i]*mags[i]; selectedIdx.add(i); } threshDesc=cut.energy+"%"; }
  let capE=0; selectedIdx.forEach(i=>capE+=mags[i]*mags[i]);
  return { selectedIdx, maxMag, order, capPct: totalEnergy>0?(capE/totalEnergy*100):0, threshDesc };
}

/* Lays out one piano: white keys in order, each black key pinned to the gap
   after its nearest lower white neighbour. Fills keyEls by note key and calls
   wireKey(el, note) so each widget attaches its own interaction. */
function buildPianoKeys(container, keyEls, notes, byKey, wireKey){
  const whiteKeys = notes.filter(n => !isBlack(n.name)), nWhite = whiteKeys.length;
  const whiteIndexOfKey = {}; whiteKeys.forEach((n,i)=>whiteIndexOfKey[n.key]=i);
  whiteKeys.forEach(n => {
    const el = document.createElement("div"); el.className="wkey"; el.dataset.key=n.key;
    const lab = document.createElement("span"); lab.className="klabel"; lab.textContent=short(n.name);
    el.appendChild(lab); container.appendChild(el); keyEls[n.key]=el;
    wireKey(el, n);
  });
  notes.filter(n => isBlack(n.name)).forEach(n => {
    let bw = n.key-1; while(bw>=1 && isBlack(byKey[bw].name)) bw--;
    const el = document.createElement("div"); el.className="bkey"; el.dataset.key=n.key;
    el.style.left = ((whiteIndexOfKey[bw]+1)/nWhite*100)+"%";
    container.appendChild(el); keyEls[n.key]=el;
    wireKey(el, n);
  });
}
