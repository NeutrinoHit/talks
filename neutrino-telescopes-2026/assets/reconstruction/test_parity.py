"""Node/Python numerical parity; no browser, private input or render."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tomllib
import unittest
import numpy as np

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[3]/'dvnanima'/'neutrino_reconstruction'
spec=importlib.util.spec_from_file_location('teaching_model',SOURCE/'model.py')
model=importlib.util.module_from_spec(spec); spec.loader.exec_module(model)


class BrowserParityTests(unittest.TestCase):
    def setUp(self):
        self.settings=model.load_settings()
        with (HERE/'ui.toml').open('rb') as f: self.settings['browser_fit']=tomllib.load(f)['browser_fit']
        self.event=model.generate(self.settings)

    def js(self,body,extra=None):
        script="const M=require('./model.js');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const d=JSON.parse(input);"+body+"});"
        data={'settings':self.settings,'event':self.event,**(extra or {})}
        result=subprocess.run(['node','-e',script],input=json.dumps(data),text=True,capture_output=True,cwd=HERE,check=True)
        return json.loads(result.stdout)

    def test_initial_event_is_exactly_the_movie_event(self):
        public=json.loads((HERE/'data.json').read_text())
        self.assertEqual(public['event'],self.event)
        movie_path=SOURCE/'out'/'synthetic_event.json'
        if movie_path.exists():
            self.assertEqual(public['event'],json.loads(movie_path.read_text())['event'])

    def test_prediction_and_profiled_score(self):
        for theta,phi in [(112,-72),(67,24),(0,170),(180,-180)]:
            result=self.js('console.log(JSON.stringify({prediction:M.predict(d.event.positions_m,d.theta,d.phi,d.settings),value:M.evaluate(d.event,d.theta,d.phi,d.settings)}));',{'theta':theta,'phi':phi})
            np.testing.assert_allclose(result['prediction'],model.predict(self.event['positions_m'],theta,phi,self.settings),atol=1e-10)
            expected=model.evaluate(self.event,theta,phi,self.settings)
            self.assertAlmostEqual(result['value']['score'],expected['score'],places=6)
            self.assertAlmostEqual(result['value']['t0_ns'],expected['t0_ns'],places=10)

    def test_fit_matches_python_and_never_uses_truth(self):
        result=self.js("const fit=M.fit(d.event,d.settings);delete d.event.truth;const other=M.fit(d.event,d.settings);d.event.truth={theta_deg:'fake',phi_deg:999999};const corrupt=M.fit(d.event,d.settings);console.log(JSON.stringify({fit,other,corrupt}));")
        self.assertEqual(result['fit'],result['other']);self.assertEqual(result['fit'],result['corrupt'])
        expected=model.fit(self.event,self.settings);got=result['fit']
        self.assertTrue(got['success'])
        self.assertLess(model.angular_separation_deg(got['theta_deg'],got['phi_deg'],expected['theta_deg'],expected['phi_deg']),1e-4)
        self.assertAlmostEqual(got['score'],expected['score'],places=6)
        for step in got['history']:
            self.assertAlmostEqual(step['score'],model.evaluate(self.event,step['theta_deg'],step['phi_deg'],self.settings)['score'],places=6)

    def test_new_events_are_sampled_reproducibly_and_fittable(self):
        result=self.js('const a=M.generate(d.settings,123),b=M.generate(d.settings,123),c=M.generate(d.settings,124);const fitted=M.fit(a,d.settings);console.log(JSON.stringify({same:JSON.stringify(a)===JSON.stringify(b),different:JSON.stringify(a)!==JSON.stringify(c),counts:a.counts,times:a.photon_times_ns,truth:a.truth,fit:fitted}));')
        self.assertTrue(result['same']);self.assertTrue(result['different'])
        self.assertEqual(result['counts'],[len(a) for a in result['times']])
        self.assertLess(model.angular_separation_deg(result['fit']['theta_deg'],result['fit']['phi_deg'],result['truth']['theta_deg'],result['truth']['phi_deg']),1)

    def test_time_shift_and_wrong_medium(self):
        result=self.js('const a=M.evaluate(d.event,80,30,d.settings);const e=M.clone(d.event);e.photon_times_ns=e.photon_times_ns.map(row=>row.map(t=>t+100));const b=M.evaluate(e,80,30,d.settings);const wrong=M.clone(d.settings);wrong.physics.n_group+=.05;console.log(JSON.stringify({a,b,wrong:M.fit(d.event,wrong)}));')
        self.assertAlmostEqual(result['a']['score'],result['b']['score'],places=7)
        self.assertAlmostEqual(result['b']['t0_ns']-result['a']['t0_ns'],100,places=10)
        correct=model.fit(self.event,self.settings)
        self.assertGreater(result['wrong']['score'],correct['score'])

    def test_failure_is_not_reported_as_converged(self):
        result=self.js("const s=M.clone(d.settings);s.browser_fit.max_iterations=1;const limit=M.fit(d.event,s);const empty=M.clone(d.event);empty.counts=empty.counts.map(()=>0);empty.photon_times_ns=empty.photon_times_ns.map(()=>[]);let failed=false;try{M.fit(empty,d.settings);}catch(e){failed=true;}console.log(JSON.stringify({converged:limit.success,failed}));")
        self.assertFalse(result['converged']);self.assertTrue(result['failed'])


if __name__=='__main__':unittest.main()
