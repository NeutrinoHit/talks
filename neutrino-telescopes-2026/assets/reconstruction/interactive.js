/* Fixed-camera timing exercise; all preferences/copy come from data.json.
 * Uses actual observed photon lists and a truth-independent profiled fit. */
(function() {
  'use strict';
  const base=new URL('.',document.currentScript.src);
  const M=window.NHReconstructionModel;
  async function initialize(root) {
    const response=await fetch(new URL('data.json',base));
    if(!response.ok) throw Error('Cannot load synthetic model');
    const data=await response.json(),ui=data.ui,C=ui.canvas,L=ui.layout,T=ui.copy,math=ui.math,D=data.drawing,S=data.style;
    const canvas=root.querySelector('canvas'),ctx=canvas.getContext('2d'),controls={};
    root.querySelectorAll('[data-control]').forEach(node=>controls[node.dataset.control]=node);
    const buttons=[...root.querySelectorAll('button')],labels=[...root.querySelectorAll('[data-control-label]')];
    const status=root.querySelector('[data-fit-status]'),numeric=root.querySelector('[data-numeric-status]'),truthStatus=root.querySelector('[data-truth-status]');
    let event=M.clone(data.event),settings=M.clone(data.settings),seed=event.seed,revealed=false,busy=false,fitResult=null,gridImage=null,animation=0,mathTimer=0,drawFrame=0;
    let histogramYMax=D.residual_y_max;
    let angles=[...D.wrong_direction_deg];
    const W=canvas.width,H=canvas.height;
    const rect=r=>[r[0]*W,r[1]*H,r[2]*W,r[3]*H];
    const fill=(key,args={})=>Object.entries(args).reduce((text,[k,v])=>text.replaceAll('{'+k+'}',v),math[key]);
    const pendingMath=new Map();
    const removeMath=node=>{
      if(window.MathJax?.typesetClear) window.MathJax.typesetClear([node]);
      if(window.MathJax?.Hub?.getAllJax) window.MathJax.Hub.getAllJax(node).forEach(jax=>jax.Remove());
    };
    const clearMath=node=>{
      pendingMath.delete(node);node.dataset.mathEpoch=String(Number(node.dataset.mathEpoch||0)+1);
      delete node.dataset.requestedFormula;delete node.dataset.formula;
      removeMath(node);node.replaceChildren();
    };
    const applyMath=(node,tex)=>{
      if(node.dataset.requestedFormula===tex) return;
      node.dataset.requestedFormula=tex;pendingMath.set(node,tex);
    };
    let typesetting=false;
    async function typeset() {
      mathTimer=0;
      if(typesetting) {mathTimer=setTimeout(typeset,L.math_debounce_ms);return;}
      const mj=window.MathJax;
      if(!mj?.typesetPromise&&!mj?.Hub?.Queue) {mathTimer=setTimeout(typeset,L.math_debounce_ms);return;}
      if(!pendingMath.size)return;
      // Typeset away from the visible layout. Keep the old LaTeX artwork
      // until its replacement is ready; raw TeX never moves a range input.
      const work=[...pendingMath].map(([node,tex])=>{
        pendingMath.delete(node);
        const stage=document.createElement('span');
        stage.style.cssText=`position:absolute;left:${L.math_stage_left_px}px;top:0;visibility:hidden;pointer-events:none;white-space:nowrap;`;
        stage.style.fontSize=getComputedStyle(node).fontSize;
        stage.textContent='\\('+tex+'\\)';root.append(stage);
        return {node,tex,stage,epoch:node.dataset.mathEpoch};
      });
      const nodes=work.map(w=>w.stage);
      typesetting=true;
      try {
        if(mj.typesetPromise){await mj.startup.promise;await mj.typesetPromise(nodes);}
        else await new Promise(resolve=>mj.Hub.Queue(...nodes.map(node=>['Typeset',mj.Hub,node]),resolve));
        work.forEach(({node,tex,stage,epoch})=>{
          if(node.dataset.mathEpoch===epoch&&node.dataset.requestedFormula!==undefined){
            removeMath(node);node.replaceChildren(...stage.childNodes);node.dataset.formula=tex;
          }else removeMath(stage);
        });
      } finally {work.forEach(w=>w.stage.remove());typesetting=false;if(pendingMath.size)queueMath();}
    }
    const queueMath=()=>{if(!mathTimer)mathTimer=setTimeout(typeset,L.math_debounce_ms);};
    function lock(locked) {
      busy=locked;buttons.forEach(b=>b.disabled=locked);Object.values(controls).forEach(c=>c.disabled=locked);
    }
    function updateControlLabels() {
      const precision=ui.controls;
      const values={theta:angles[0].toFixed(precision.status_precision),phi:angles[1].toFixed(precision.status_precision),budget:controls.budget.value,sigma:Number(controls.sigma.value).toFixed(precision.status_precision),group:Number(controls.group.value).toFixed(precision.group_index_precision)};
      labels.forEach(node=>applyMath(node,fill({theta:'theta_control',phi:'phi_control',budget:'budget_control',sigma:'sigma_control',group:'group_control'}[node.dataset.controlLabel],{value:values[node.dataset.controlLabel]})));
      queueMath();
    }
    root.querySelectorAll('[data-plot-label]').forEach(node=>{
      const key=node.dataset.plotLabel;
      if(node.dataset.math==='true') applyMath(node,fill(key,{length:D.scale_m}));
      else node.textContent=T[key];
    });
    const a=data.camera.azimuth_deg*Math.PI/180,e=data.camera.elevation_deg*Math.PI/180;
    const right=[-Math.sin(a),Math.cos(a),0],up=[-Math.sin(e)*Math.cos(a),-Math.sin(e)*Math.sin(a),Math.cos(e)];
    const [sx,sy,sw,sh]=rect(C.scene),scale=Math.min(sw,sh)/data.camera.span_m;
    function project(point) {
      const delta=point.map((v,i)=>v-settings.detector.crossing_point_m[i]);
      return [sx+sw/2+delta.reduce((s,v,i)=>s+v*right[i],0)*scale,sy+sh/2-delta.reduce((s,v,i)=>s+v*up[i],0)*scale];
    }
    const color=(palette,u)=>'rgb('+palette[Math.round(Math.max(0,Math.min(1,u))*(palette.length-1))].join(',')+')';
    function circle(x,y,r,fill,stroke) {
      ctx.beginPath();ctx.arc(x,y,r,0,2*Math.PI);
      if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=D.line_width_px;ctx.stroke();}
    }
    function line(a,b,color,width=D.line_width_px) {
      ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();
    }
    function arrow(theta,phi,color,dashed=false) {
      const u=M.direction(theta,phi),p=settings.detector.crossing_point_m;
      const from=project(p.map((v,i)=>v-u[i]*data.camera.track_half_length_m)),to=project(p.map((v,i)=>v+u[i]*data.camera.track_half_length_m));
      ctx.save();if(dashed)ctx.setLineDash(C.line_dash);line(from,to,color,D.track_width_px);ctx.restore();
      const dx=to[0]-from[0],dy=to[1]-from[1],norm=Math.hypot(dx,dy),size=D.arrow_head_px;
      if(!norm)return;
      const ux=dx/norm,uy=dy/norm;
      ctx.beginPath();ctx.moveTo(...to);ctx.lineTo(to[0]-ux*size-uy*size/2,to[1]-uy*size+ux*size/2);ctx.lineTo(to[0]-ux*size+uy*size/2,to[1]-uy*size-ux*size/2);ctx.closePath();ctx.fillStyle=color;ctx.fill();
    }
    function makeGridImage() {
      const map=fitResult.sky_map,[, ,w,h]=rect(C.sky),cw=Math.round(w),ch=Math.round(h);
      const off=document.createElement('canvas');off.width=cw;off.height=ch;
      const dc=off.getContext('2d'),image=dc.createImageData(cw,ch),ny=map.theta_deg.length,nx=map.phi_deg.length;
      const low=D.sky_log_range[0],high=D.sky_log_range[1];
      const field=map.delta_score.map(row=>row.map(v=>Math.log10(1+v)));
      for(let y=0;y<ch;y++) for(let x=0;x<cw;x++) {
        const gx=x/(cw-1)*nx,gy=y/(ch-1)*(ny-1),i=Math.min(ny-2,Math.floor(gy)),j=Math.floor(gx)%nx,fx=gx-Math.floor(gx),fy=gy-i;
        const value=(1-fy)*((1-fx)*field[i][j]+fx*field[i][(j+1)%nx])+fy*((1-fx)*field[i+1][j]+fx*field[i+1][(j+1)%nx]);
        const rgb=data.palettes.sky[Math.round(Math.max(0,Math.min(1,(value-low)/(high-low)))*(data.palettes.sky.length-1))];
        const index=(y*cw+x)*4;image.data.set([...rgb,255],index);
      }
      dc.putImageData(image,0,0);gridImage=off;
    }
    function text(text,x,y,align='left',color=S.muted) {ctx.fillStyle=color;ctx.textAlign=align;ctx.fillText(String(text),x,y);}
    function histogram(predicted) {
      const lo=D.residual_range_ns[0],hi=D.residual_range_ns[1],bins=Array(D.residual_bins).fill(0);let outside=0;
      event.photon_times_ns.forEach((hits,i)=>hits.forEach(t=>{
        const v=t-predicted[i];
        if(v<lo||v>hi)outside++;else bins[Math.min(bins.length-1,Math.floor((v-lo)/(hi-lo)*bins.length))]++;
      }));
      return {bins,outside};
    }
    function scheduleDraw() {
      if(drawFrame)return;
      drawFrame=requestAnimationFrame(()=>{drawFrame=0;draw();});
    }
    function draw() {
      const [theta,phi]=angles,value=M.evaluate(event,theta,phi,settings);
      const legend=root.querySelector('[data-plot-label="scene_legend"]'),legendText=T.scene_legend+(revealed?' · '+T.truth_note:'');
      if(legend.textContent!==legendText)legend.textContent=legendText;
      ctx.fillStyle=S.background;ctx.fillRect(0,0,W,H);ctx.font=C.font_px+'px '+C.font_family;ctx.textBaseline='middle';
      for(const box of [C.scene,C.sky,C.residual]){const [x,y,w,h]=rect(box);ctx.fillStyle=S.panel;ctx.fillRect(x,y,w,h);ctx.strokeStyle=S.grid;ctx.lineWidth=D.line_width_px;ctx.strokeRect(x,y,w,h);}
      const points=event.positions_m.map(project),heights=settings.detector.heights_m.length;
      for(let s=0;s<settings.detector.strings;s++)line(points[s*heights],points[(s+1)*heights-1],S.grid);
      const centre=project(settings.detector.crossing_point_m);line([centre[0]-C.crossing_radius_px,centre[1]],[centre[0]+C.crossing_radius_px,centre[1]],S.crossing);line([centre[0],centre[1]-C.crossing_radius_px],[centre[0],centre[1]+C.crossing_radius_px],S.crossing);
      const hitTimes=event.photon_times_ns.flat(),tmin=Math.min(...hitTimes),tmax=Math.max(...hitTimes);
      const timeColor=t=>color(data.palettes.time,(t-tmin)/(tmax-tmin));
      arrow(theta,phi,S.trial);
      if(revealed)arrow(event.truth.theta_deg,event.truth.phi_deg,S.truth,true);
      points.forEach(([x,y],i)=>{
        const count=event.counts[i];if(!count){circle(x,y,D.om_base_radius_px,S.grid);return;}
        const radius=D.om_base_radius_px+D.om_count_scale_px*Math.sqrt(count);
        circle(x,y,radius+D.om_ring_offset_px,null,timeColor(value.predicted_times_ns[i]));
        circle(x,y,radius,timeColor(event.photon_times_ns[i].reduce((s,t)=>s+t,0)/count));
      });
      const sc=C.scale_position;line([sc[0]*W,sc[1]*H],[sc[0]*W+D.scale_m*scale,sc[1]*H],S.muted);
      let [x,y,w,h]=rect(C.time_colorbar);
      for(let i=0;i<w;i++){ctx.fillStyle=color(data.palettes.time,i/w);ctx.fillRect(x+i,y,1,h);}
      text(tmin.toFixed(ui.controls.tick_precision),x,y-C.tick_offset*H);
      text(tmax.toFixed(ui.controls.tick_precision),x+w,y-C.tick_offset*H,'right');
      [x,y,w,h]=rect(C.sky);if(gridImage)ctx.drawImage(gridImage,x,y,w,h);
      const marker=(t,p,col,truth=false)=>{
        const xx=x+((p+180)%360+360)%360/360*w,yy=y+t/180*h,r=D.sky_marker_radius_px;
        if(truth){line([xx-r,yy],[xx+r,yy],col);line([xx,yy-r],[xx,yy+r],col);}else circle(xx,yy,r,null,col);
      };
      marker(theta,phi,S.trial);if(revealed)marker(event.truth.theta_deg,event.truth.phi_deg,S.truth,true);
      C.sky_tick_degrees.forEach(p=>text(p,x+(p+180)/360*w,y+h+C.tick_offset*H,'center'));
      C.theta_tick_degrees.forEach(t=>text(t,x-C.tick_left_offset*W,y+t/180*h,'right'));
      const cb=rect(C.sky_colorbar);
      for(let i=0;i<cb[3];i++){ctx.fillStyle=color(data.palettes.sky,i/cb[3]);ctx.fillRect(cb[0],cb[1]+i,cb[2],1);}
      D.sky_log_range.forEach((n,i)=>text(n,cb[0]+C.color_tick_x_offset*W,cb[1]+i*cb[3]));
      const lo=D.residual_range_ns[0],hi=D.residual_range_ns[1],{bins,outside}=histogram(value.predicted_times_ns);
      [x,y,w,h]=rect(C.residual);const ymax=histogramYMax;
      bins.forEach((n,i)=>{if(n){ctx.fillStyle=S.trial;const bh=Math.min(n/ymax,1)*h;ctx.fillRect(x+i*w/bins.length,y+h-bh,w/bins.length,bh);}});
      line([x-lo/(hi-lo)*w,y],[x-lo/(hi-lo)*w,y+h],S.muted);
      C.residual_tick_ns.forEach(v=>text(v,x+(v-lo)/(hi-lo)*w,y+h+C.tick_offset*H,'center'));
      text(ymax,x-C.histogram_tick_x_offset*W,y,'right');text(0,x-C.histogram_tick_x_offset*W,y+h,'right');
      if(outside)text(T.offscale.replace('{count}',outside),x,y+C.overflow_y_offset*H);
      const overheight=bins.filter(n=>n>ymax).length;
      if(overheight)text(T.overheight.replace('{count}',overheight),x,y+C.overflow_y_offset*H+(outside?C.font_px:0));
      const precision=ui.controls.status_precision;
      applyMath(numeric,fill('status',{count:value.observed_pe,modules:value.hit_modules,score:value.score.toFixed(precision),offset:value.t0_ns.toFixed(precision)}));
      if(revealed)applyMath(truthStatus,fill('truth_error',{error:M.angularSeparation({theta_deg:theta,phi_deg:phi},event.truth).toFixed(ui.controls.angle_precision)}));
      else if(truthStatus.dataset.requestedFormula!==undefined)clearMath(truthStatus);
      queueMath();
    }
    async function rebuild() {
      lock(true);status.textContent=T.working;
      await new Promise(resolve=>requestAnimationFrame(resolve));
      try{
        fitResult=M.fit(event,settings);makeGridImage();
        histogramYMax=Math.ceil(Math.max(D.residual_y_max,...histogram(fitResult.predicted_times_ns).bins)*C.histogram_headroom);
        status.textContent=fitResult.success?T.trial:T.unconverged;draw();
      }
      finally{lock(false);}
    }
    Object.values(controls).forEach(c=>c.addEventListener('keydown',ev=>ev.stopPropagation()));
    // Never let Reveal's drag/touch navigation intercept a native slider.
    Object.values(controls).forEach(c=>['pointerdown','pointermove','touchstart','touchmove'].forEach(type=>c.addEventListener(type,ev=>ev.stopPropagation(),{passive:true})));
    ['theta','phi'].forEach(key=>controls[key].addEventListener('input',()=>{cancelAnimationFrame(animation);angles=[Number(controls.theta.value),Number(controls.phi.value)];status.textContent=T.trial;updateControlLabels();scheduleDraw();}));
    ['budget','sigma'].forEach(key=>controls[key].addEventListener('input',updateControlLabels));
    controls.group.title=T.medium_hint;
    controls.group.addEventListener('input',updateControlLabels);
    controls.group.addEventListener('change',async()=>{settings.physics.n_group=Number(controls.group.value);await rebuild();});
    canvas.addEventListener('pointerdown',ev=>{
      if(busy)return;const b=canvas.getBoundingClientRect(),x=(ev.clientX-b.left)/b.width,y=(ev.clientY-b.top)/b.height,r=C.sky;
      if(x<r[0]||x>r[0]+r[2]||y<r[1]||y>r[1]+r[3])return;
      angles=[(y-r[1])/r[3]*180,(x-r[0])/r[2]*360-180];controls.phi.value=angles[1];controls.theta.value=angles[0];status.textContent=T.trial;updateControlLabels();scheduleDraw();
    });
    root.addEventListener('click',async ev=>{
      const button=ev.target.closest('button[data-action]');if(!button||busy)return;
      try{
        if(button.dataset.action==='reveal'){revealed=!revealed;button.textContent=revealed?T.hide:T.reveal;draw();}
        if(button.dataset.action==='reset'){
          clearMath(numeric);clearMath(truthStatus);
          cancelAnimationFrame(animation);event=M.clone(data.event);settings=M.clone(data.settings);seed=event.seed;revealed=false;
          angles=[...D.wrong_direction_deg];controls.theta.value=angles[0];controls.phi.value=angles[1];controls.group.value=settings.physics.n_group;controls.budget.value=settings.generation.expected_total_pe;controls.sigma.value=event.sigma_ns;
          root.querySelector('[data-action="reveal"]').textContent=T.reveal;updateControlLabels();await rebuild();
        }
        if(button.dataset.action==='new_event'){
          clearMath(numeric);clearMath(truthStatus);
          const generation=M.clone(data.settings);seed+=ui.controls.seed_increment;
          generation.generation.expected_total_pe=Number(controls.budget.value);generation.generation.sigma_ns=Number(controls.sigma.value);
          if(ui.controls.randomize_new_direction){const rng=M.randomGenerator(seed);generation.generation.theta_deg=Math.acos(2*rng.uniform()-1)*180/Math.PI;generation.generation.phi_deg=360*rng.uniform()-180;}
          event=M.generate(generation,seed);settings=M.clone(generation);settings.physics.n_group=Number(controls.group.value);revealed=false;
          root.querySelector('[data-action="reveal"]').textContent=T.reveal;angles=[...D.wrong_direction_deg];controls.theta.value=angles[0];controls.phi.value=angles[1];updateControlLabels();await rebuild();
        }
        if(button.dataset.action==='fit'){
          await rebuild();lock(true);const history=fitResult.history,start=performance.now();
          const step=()=>{
            try {
              // rAF's frame timestamp can precede an event-handler start.
              // Use the current monotonic clock and clamp both endpoints.
              const fraction=Math.max(0,Math.min(1,(performance.now()-start)/ui.controls.fit_animation_ms)),index=Math.min(history.length-1,Math.floor(fraction*history.length)),state=history[index];
              angles=[state.theta_deg,state.phi_deg];controls.theta.value=angles[0];controls.phi.value=angles[1];updateControlLabels();draw();
              if(fraction<1)animation=requestAnimationFrame(step);else{status.textContent=fitResult.success?T.fitted:T.unconverged;lock(false);}
            }catch(error){lock(false);status.textContent=T.error+error.message;}
          };
          animation=requestAnimationFrame(step);
        }
      }catch(error){lock(false);status.textContent=T.error+error.message;}
    });
    updateControlLabels();await rebuild();queueMath();
  }
  const start=()=>document.querySelectorAll('[data-reconstruction]').forEach(root=>initialize(root).catch(error=>{root.querySelector('[data-fit-status]').textContent=error.message;console.error(error);}));
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
