"""Physical contracts for the illustrative Galactic intensity."""
import copy
from pathlib import Path
import tomllib
import unittest
import numpy as np
from render import emissivity, line_of_sight, Film

CFG=tomllib.loads((Path(__file__).parent/'config.toml').read_text())


class GalacticModelTests(unittest.TestCase):
    def small(self):
        c=copy.deepcopy(CFG)
        c['sky'].update(longitude_bins=181,latitude_bins=61,distance_steps=500)
        return c

    def test_nonnegative_and_disk_cutoff(self):
        g=CFG['galaxy']
        xyz=np.random.default_rng(1).uniform(-20,20,(3,1000))
        q=emissivity(*xyz,g)
        self.assertTrue(np.isfinite(q).all())
        self.assertTrue((q>=0).all())
        self.assertEqual(emissivity(17,0,0,g),0)

    def test_vertical_scale(self):
        g=CFG['galaxy']
        self.assertAlmostEqual(emissivity(8,0,g['gas_height_kpc'],g)/emissivity(8,0,0,g),np.exp(-1))

    def test_centre_longitude_and_plane(self):
        l,b,i=line_of_sight(self.small())
        equator=np.where(b==0)[0][0]
        self.assertGreater(i[equator,len(l)//2],i[equator,0])
        self.assertTrue(np.all(i[equator]>=i[0]))
        np.testing.assert_allclose(i,i[::-1],rtol=1e-12)

    def test_intensity_is_path_integral(self):
        # Homogeneous medium: intensity grows linearly with path length.
        from unittest.mock import patch
        c=self.small()
        with patch('render.emissivity',side_effect=lambda x,y,z,g:np.ones_like(x)):
            _,_,i=line_of_sight(c)
        np.testing.assert_allclose(i,c['sky']['distance_max_kpc'],rtol=1e-12)

    def test_distance_convergence(self):
        c=self.small(); _,_,a=line_of_sight(c)
        c['sky']['distance_steps']=1000; _,_,b=line_of_sight(c)
        self.assertLess(np.sum(abs(a-b))/np.sum(b),.003)

    def test_proton_collision_and_neutrino_endpoint(self):
        c=self.small()
        c['galaxy'].update(stars=1000,gas_points=5000,bulge_points=500)
        f=Film(c,640,360)
        for path,origin in zip(f.paths,f.origins):
            np.testing.assert_allclose(path(1),origin,atol=1e-12)
            np.testing.assert_allclose(origin+1*(f.sun-origin),f.sun,atol=1e-12)

    def test_surface_brightness_across_resolutions(self):
        c=self.small()
        c['galaxy'].update(stars=1000,gas_points=5000,bulge_points=500)
        f=Film(c,640,360)
        a=f.layer(f.gas_points,[1.,.6,.3],1.,0).mean(axis=(0,1))
        f.w,f.h,f.scale=1280,720,1280/c['video']['width']
        b=f.layer(f.gas_points,[1.,.6,.3],1.,0).mean(axis=(0,1))
        np.testing.assert_allclose(a,b,rtol=1e-5)


if __name__=='__main__':unittest.main()
