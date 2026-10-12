/* Public synthetic timing model. Numeric defaults are supplied by physics.toml.
 * UMD export: browser NHReconstructionModel or Node require('./model.js'). */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.NHReconstructionModel = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';
  const rad = x => x * Math.PI / 180;
  const deg = x => x * 180 / Math.PI;
  const clone = x => JSON.parse(JSON.stringify(x));
  const sum = a => a.reduce((x,y) => x+y,0);
  const dot = (a,b) => sum(a.map((v,i) => v*b[i]));
  const clamp = (x,a,b) => Math.max(a,Math.min(b,x));
  function direction(theta,phi) {
    const t=rad(theta),p=rad(phi);
    return [Math.sin(t)*Math.cos(p),Math.sin(t)*Math.sin(p),Math.cos(t)];
  }
  function predict(positions,theta,phi,settings,t0=0) {
    const p=settings.physics,anchor=settings.detector.crossing_point_m,u=direction(theta,phi);
    if (!(p.beta>0 && p.beta<=1 && p.beta*p.n_phase>1 && p.c_m_per_ns>0 && p.n_group>=1)) throw Error('Invalid Cherenkov medium');
    const cos=1/(p.beta*p.n_phase),sin=Math.sqrt(1-cos*cos);
    return positions.map(r => {
      const d=r.map((v,i)=>v-anchor[i]),ell=dot(d,u);
      const rho=Math.sqrt(sum(d.map((v,i)=>(v-ell*u[i])**2)));
      const s=ell-rho*cos/sin,D=rho/sin;
      return t0+s/(p.beta*p.c_m_per_ns)+p.n_group*D/p.c_m_per_ns;
    });
  }
  function sufficient(event) {
    if (!(event.sigma_ns>0 && Number.isFinite(event.sigma_ns))) throw Error('Positive timing width required');
    if (event.photon_times_ns.length!==event.positions_m.length) throw Error('Geometry/hit mismatch');
    const counts=event.photon_times_ns.map(a=>a.length),means=event.photon_times_ns.map(a=>a.length?sum(a)/a.length:0);
    if (!sum(counts) || counts.some((n,i)=>n!==event.counts[i])) throw Error('Observed photon counts mismatch or empty event');
    let within=0;
    event.photon_times_ns.forEach((a,i)=>a.forEach(t=>{
      if (!Number.isFinite(t)) throw Error('Nonfinite observed hit');
      within+=(t-means[i])**2;
    }));
    return {counts,means,within,total:sum(counts)};
  }
  function evaluatePrepared(event,theta,phi,settings,stats) {
    const base=predict(event.positions_m,theta,phi,settings);
    const t0=sum(base.map((v,i)=>stats.counts[i]*(stats.means[i]-v)))/stats.total;
    const residual=base.map((v,i)=>stats.means[i]-v-t0);
    const score=(stats.within+sum(residual.map((v,i)=>stats.counts[i]*v*v)))/(2*event.sigma_ns**2);
    return {score,t0_ns:t0,residuals_ns:residual.map((r,i)=>stats.counts[i]?r:null),
      predicted_times_ns:base.map(v=>v+t0),hit_modules:stats.counts.filter(n=>n>0).length,observed_pe:stats.total};
  }
  function evaluate(event,theta,phi,settings) { return evaluatePrepared(event,theta,phi,settings,sufficient(event)); }
  function grid(event,settings,stats=sufficient(event)) {
    const f=settings.fit,theta=[],phi=[],scores=[];
    for(let i=0;i<f.grid_theta_count;i++) theta.push(f.theta_bounds_deg[0]+i*(f.theta_bounds_deg[1]-f.theta_bounds_deg[0])/(f.grid_theta_count-1));
    for(let i=0;i<f.grid_phi_count;i++) phi.push(f.phi_bounds_deg[0]+i*(f.phi_bounds_deg[1]-f.phi_bounds_deg[0])/f.grid_phi_count);
    theta.forEach(t=>scores.push(phi.map(p=>evaluatePrepared(event,t,p,settings,stats).score)));
    return {theta_deg:theta,phi_deg:phi,score:scores};
  }
  function fit(event,settings,options={}) {
    const stats=sufficient(event),f=settings.fit;
    if(stats.counts.filter(n=>n>0).length<f.minimum_hit_modules) throw Error('Insufficient hit modules');
    const map=grid(event,settings,stats),candidates=[];
    map.theta_deg.forEach((t,i)=>map.phi_deg.forEach((p,j)=>candidates.push({theta_deg:t,phi_deg:p,score:map.score[i][j]})));
    candidates.sort((a,b)=>a.score-b.score);
    const config=options.search || settings.browser_fit;
    if(!config) throw Error('External browser search settings required');
    const span=f.phi_bounds_deg[1]-f.phi_bounds_deg[0];
    const wrap=p=>f.phi_bounds_deg[0]+((p-f.phi_bounds_deg[0])%span+span)%span;
    const histories=[]; let best=null;
    for(const start of candidates.slice(0,f.multistarts)) {
      let current={...start,...evaluatePrepared(event,start.theta_deg,start.phi_deg,settings,stats)};
      const history=[{theta_deg:current.theta_deg,phi_deg:current.phi_deg,score:current.score,t0_ns:current.t0_ns}];
      let stepT=(f.theta_bounds_deg[1]-f.theta_bounds_deg[0])/(f.grid_theta_count-1);
      let stepP=span/f.grid_phi_count;
      let converged=false,iterations=0;
      for(let iteration=0;iteration<config.max_iterations;iteration++) {
        iterations=iteration+1;
        let chosen=current;
        for(const [dt,dp] of config.search_offsets) {
          const theta=clamp(current.theta_deg+dt*stepT,...f.theta_bounds_deg),phi=wrap(current.phi_deg+dp*stepP);
          const value=evaluatePrepared(event,theta,phi,settings,stats);
          if(value.score<chosen.score) chosen={theta_deg:theta,phi_deg:phi,...value};
        }
        if(chosen===current) {stepT*=config.step_shrink;stepP*=config.step_shrink;}
        else {current=chosen;history.push({theta_deg:current.theta_deg,phi_deg:current.phi_deg,score:current.score,t0_ns:current.t0_ns});}
        if(Math.max(stepT,stepP)<config.stop_step_deg){converged=true;break;}
      }
      histories.push(history);
      if(!best || current.score<best.score) best={...current,history,success:converged,iterations};
    }
    map.delta_score=map.score.map(row=>row.map(s=>Math.max(0,s-best.score)));
    return {...best,direction:direction(best.theta_deg,best.phi_deg),all_histories:histories,sky_map:map};
  }
  /* Algorithmic constants below define the PRNG, not scene/physics preferences.
   * Reproducibility is within JS; NumPy deliberately has a different PRNG. */
  function randomGenerator(seed) {
    let state=seed>>>0;
    const uniform=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return (state+.5)/4294967296;};
    const normal=()=>Math.sqrt(-2*Math.log(uniform()))*Math.cos(2*Math.PI*uniform());
    const poisson=mean=>{const limit=Math.exp(-mean);let p=1,k=0;do{k++;p*=uniform();}while(p>limit);return k-1;};
    return {uniform,normal,poisson};
  }
  function generate(settings,seed=settings.generation.seed) {
    const g=settings.generation,d=settings.detector,rng=randomGenerator(seed),positions=[];
    for(let i=0;i<d.strings;i++) {
      const a=2*Math.PI*i/d.strings+rad(d.azimuth_offset_deg);
      d.heights_m.forEach(z=>positions.push([d.radius_m*Math.cos(a),d.radius_m*Math.sin(a),z]));
    }
    const predicted=predict(positions,g.theta_deg,g.phi_deg,settings,g.t0_ns),u=direction(g.theta_deg,g.phi_deg);
    const sin=Math.sqrt(1-(1/(settings.physics.beta*settings.physics.n_phase))**2);
    const weights=positions.map(r=>{const delta=r.map((v,i)=>v-d.crossing_point_m[i]),ell=dot(delta,u);
      const D=Math.sqrt(sum(delta.map((v,i)=>(v-ell*u[i])**2)))/sin;
      return Math.exp(-D/g.attenuation_length_m)/(D*D+g.distance_floor_m**2);});
    const total=sum(weights),enabled=positions.map((_,i)=>!g.disabled_strings.includes(Math.floor(i/d.heights_m.length)));
    const expected=weights.map((w,i)=>enabled[i]?w/total*g.expected_total_pe:0),times=[];
    expected.forEach((mean,i)=>{
      const photons=[]; const count=rng.poisson(mean);
      for(let k=0;k<count;k++) {
        let t=predicted[i]+g.sigma_ns*rng.normal();
        if(rng.uniform()<g.scattered_fraction) t-=g.scattering_delay_ns*Math.log(rng.uniform());
        photons.push(t);
      }
      const dark=enabled[i]?rng.poisson(g.dark_mean_pe_per_module):0;
      for(let k=0;k<dark;k++) photons.push(g.dark_window_ns[0]+rng.uniform()*(g.dark_window_ns[1]-g.dark_window_ns[0]));
      times.push(photons.sort((a,b)=>a-b));
    });
    return {positions_m:positions,counts:times.map(t=>t.length),photon_times_ns:times,sigma_ns:g.sigma_ns,
      expected_source_counts:expected,enabled,seed,truth:{theta_deg:g.theta_deg,phi_deg:g.phi_deg,t0_ns:g.t0_ns,direction:u}};
  }
  function angularSeparation(a,b) {return deg(Math.acos(clamp(dot(direction(a.theta_deg,a.phi_deg),direction(b.theta_deg,b.phi_deg)),-1,1)));}
  return {clone,direction,predict,sufficient,evaluate,fit,grid,generate,randomGenerator,angularSeparation};
});
