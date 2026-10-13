"""Galactic emission film: a schematic disk and a reproducible LOS integral.

Rendering follows the additive point clouds and bloom used by DN's dvnanima
films. Particle trajectories are teaching choreography, not transport output.
The sky is computed independently from the explicit emissivity in config.toml.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
from pathlib import Path
import subprocess
import tomllib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.interpolate import CubicSpline

HERE = Path(__file__).resolve().parent
MEDIA = HERE.parent.parent / "media" / "galactic"


def smooth(a, b, t):
    x = np.clip((t-a)/(b-a), 0, 1)
    return x*x*(3-2*x)


def emissivity(x, y, z, g):
    """Arbitrary emissivity units; lengths in kpc. Nonnegative, thin disk."""
    r = np.hypot(x, y)
    phase = g['arms']*(np.arctan2(y, x)-np.log(np.maximum(r, 0.4))/
                       np.tan(np.deg2rad(g['pitch_deg']))-g['arm_phase'])
    arms = 1+g['arm_contrast']*np.cos(phase)
    return (np.exp(-r/g['gas_scale_kpc']-r/g['cr_scale_kpc']) *
            np.exp(-np.abs(z)/g['gas_height_kpc'])*arms*(r<g['radius_kpc']))


def line_of_sight(cfg):
    """I(l,b) ∝ integral q ds, for an observer at (R_sun,0,0).

    There is no inverse-square factor in the specific intensity integral.
    Longitude is positive towards +y, zero towards the Galactic centre.
    """
    s, g = cfg['sky'], cfg['galaxy']
    lon = np.linspace(180, -180, s['longitude_bins'])
    lat = np.linspace(s['latitude_limit_deg'], -s['latitude_limit_deg'], s['latitude_bins'])
    ll, bb = np.meshgrid(np.deg2rad(lon), np.deg2rad(lat))
    ux, uy, uz = -np.cos(bb)*np.cos(ll), np.cos(bb)*np.sin(ll), np.sin(bb)
    ds = s['distance_max_kpc']/s['distance_steps']
    out = np.zeros_like(ll)
    for d in (np.arange(s['distance_steps'])+0.5)*ds:
        out += emissivity(g['sun_kpc']+d*ux, d*uy, d*uz, g)*ds
    return lon, lat, out


class Film:
    def __init__(self, cfg, width, height):
        self.c, self.w, self.h = cfg, width, height
        self.scale = width/cfg['video']['width']
        self.rng = np.random.default_rng(cfg['galaxy']['seed'])
        self.sun = np.array([cfg['galaxy']['sun_kpc'], 0., 0.])
        yaw, el = np.deg2rad([cfg['camera']['yaw_deg'], cfg['camera']['elevation_deg']])
        self.right = np.array([np.cos(yaw), np.sin(yaw), 0])
        self.up = np.array([-np.sin(yaw)*np.sin(el), np.cos(yaw)*np.sin(el), np.cos(el)])
        self.back = self.galaxy()
        self.paths, self.origins = self.events()
        self.lon, self.lat, self.intensity = line_of_sight(cfg)
        self.sky = self.sky_image()

    @lru_cache(None)
    def font(self, size, bold=False):
        return ImageFont.truetype(self.c['style']['bold_font' if bold else 'font'], max(1, round(size*self.scale)))

    def text(self, im, text, xy, size, color=None, anchor='lm', bold=False):
        ImageDraw.Draw(im).text((xy[0]*self.w, xy[1]*self.h), text,
            font=self.font(size, bold), fill=color or tuple(self.c['style']['text']), anchor=anchor,
            stroke_width=max(1,round(self.scale)), stroke_fill=tuple(self.c['style']['background']))

    def project(self, p):
        p = np.asarray(p)
        k = self.w/self.c['camera']['span_kpc']
        return np.stack([self.w*0.5+k*(p@self.right), self.h*self.c['camera']['centre_y']-k*(p@self.up)], axis=-1)

    def points(self, n, gas=False):
        g = self.c['galaxy']; rng = self.rng
        radial_scale=g['gas_scale_kpc'] if gas else 3.3
        r = rng.gamma(2, radial_scale, n)
        inner=0.0 if gas else 0.7
        outside=(r<inner)|(r>g['radius_kpc'])
        while outside.any():
            r[outside]=rng.gamma(2,radial_scale,sum(outside))
            outside=(r<inner)|(r>g['radius_kpc'])
        phi = rng.uniform(-np.pi, np.pi, n)
        spiral = np.log(np.maximum(r,.4))/np.tan(np.deg2rad(g['pitch_deg']))+g['arm_phase']
        if gas:
            # Exact angular rejection sampling from the gas arm factor.
            pending=np.ones(n,dtype=bool)
            while pending.any():
                inds=np.where(pending)[0]
                proposed=rng.uniform(-np.pi,np.pi,len(inds))
                accept=(1+g['arm_contrast']*np.cos(g['arms']*(proposed-spiral[inds])))/(1+g['arm_contrast'])
                keep=rng.random(len(inds))<accept
                phi[inds[keep]]=proposed[keep]; pending[inds[keep]]=False
            z=rng.laplace(0,g['gas_height_kpc'],n)
        else:
            selected = rng.random(n)<0.62
            phi[selected] = spiral[selected]+rng.integers(0,g['arms'],sum(selected))*2*np.pi/g['arms']+rng.normal(0,0.19,sum(selected))
            z=rng.normal(0,0.23,n)
        return np.column_stack([r*np.cos(phi), r*np.sin(phi), z])

    def layer(self, p, colors, gain, blur):
        # Additive bilinear point rendering at half resolution, as in dvnanima.
        ww, hh = self.w//2, self.h//2
        xy = self.project(p)/2
        x,y = xy.T; ix,iy=np.floor(x).astype(int),np.floor(y).astype(int)
        fx,fy=x-ix,y-iy
        buf = np.zeros((hh,ww,3),np.float32)
        # Preserve surface brightness when the projected pixel area changes.
        gain *= (self.w/self.c['style']['splat_reference_width'])**2
        colors = np.broadcast_to(np.asarray(colors),(len(p),3))*gain
        for dx,dy,v in ((0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)):
            xx,yy=ix+dx,iy+dy; ok=(xx>=0)&(xx<ww)&(yy>=0)&(yy<hh)
            for ch in range(3):
                buf[:,:,ch]+=np.bincount(yy[ok]*ww+xx[ok],weights=colors[ok,ch]*v[ok],minlength=ww*hh).reshape(hh,ww)
        return gaussian_filter(buf,(blur*self.scale,blur*self.scale,0))

    def galaxy(self):
        g=self.c['galaxy']; rng=self.rng
        stars=self.points(g['stars']); gas=self.points(g['gas_points'],True)
        self.gas_points=gas
        rr=np.linalg.norm(stars[:,:2],axis=1)
        cold=np.array([0.28,0.48,0.85]); warm=np.array([1.,0.65,0.32])
        mix=np.exp(-rr/5)[:,None]
        colors=warm*mix+cold*(1-mix)
        bulge=rng.normal(0,[1.5,0.65,0.4],(g['bulge_points'],3))
        hdr=self.layer(stars,colors,0.065,0.45)+self.layer(bulge,[1.,0.62,0.3],0.035,1.2)
        hdr+=self.layer(gas,[0.27,0.22,0.6],0.065,2.3)
        for sigma,gain in ((3,0.45),(12,0.5)):
            hdr+=gaussian_filter(hdr,(sigma*self.scale,sigma*self.scale,0))*gain
        rgb=1-np.exp(-hdr)
        base=np.asarray(self.c['style']['background'])/255
        rgb=base+(1-base)*rgb
        image=Image.fromarray((255*np.clip(rgb,0,1)).astype('uint8')).resize((self.w,self.h),Image.Resampling.LANCZOS)
        # Sparse quiet field of background stars, with a seeded fixed camera.
        d=ImageDraw.Draw(image)
        for x,y,a in zip(rng.uniform(0,self.w,280),rng.uniform(.17*self.h,.85*self.h,280),rng.integers(20,65,280)):
            d.point((x,y),fill=(int(a*.65),int(a*.8),int(a)))
        return image

    def events(self):
        c=self.c['particles']; rng=self.rng
        # Toy event locations sampled from the same q used in the sky integral.
        candidates=self.gas_points
        r=np.linalg.norm(candidates[:,:2],axis=1)
        # Gas was sampled from n_gas; CR weighting gives event density q.
        prob=np.exp(-r/self.c['galaxy']['cr_scale_kpc']); prob/=prob.sum()
        origins=candidates[rng.choice(len(candidates),c['events'],replace=False,p=prob)]
        paths=[]
        for p in origins:
            steps=rng.normal(0,[.48,.48,.08],(12,3))
            walk=np.cumsum(steps,axis=0); walk=walk-walk[-1]+p
            paths.append(CubicSpline(np.linspace(0,1,len(walk)),walk))
        return paths,origins

    def glow(self, im, strokes, dots):
        lay=Image.new('RGB',(self.w,self.h)); d=ImageDraw.Draw(lay)
        for xy,col,width in strokes:
            d.line([tuple(p) for p in xy],fill=col,width=max(1,round(width*self.scale)))
        for p,col,r in dots:
            x,y=p; r*=self.scale
            d.ellipse((x-r,y-r,x+r,y+r),fill=col)
        arr=np.asarray(im,dtype=float)
        for blur,gain in ((0,1),(4*self.scale,.65),(13*self.scale,.45)):
            stamp=lay if blur==0 else lay.filter(ImageFilter.GaussianBlur(blur))
            arr+=np.asarray(stamp)*gain
        return Image.fromarray(np.uint8(np.clip(arr,0,255)))

    def sky_image(self):
        # Asinh stretch with a single fixed reference for every movie frame.
        v=np.arcsinh(self.intensity/(self.intensity.max()*.07))/np.arcsinh(1/.07)
        stops=np.array([0,.12,.35,.65,1])
        cols=np.array([[2,4,10],[6,15,38],[13,65,112],[33,157,205],[180,246,255]])
        rgb=np.stack([np.interp(v,stops,cols[:,i]) for i in range(3)],axis=-1)
        return Image.fromarray(np.uint8(rgb))

    def map_frame(self, t):
        im=Image.new('RGB',(self.w,self.h),tuple(self.c['style']['background']))
        # A latitude crop rather than an all-sky projection: no unlabelled poles.
        x,y,w,h=.07,.30,.86,.39
        bounds=(round(x*self.w),round(y*self.h),round(w*self.w),round(h*self.h))
        sky=self.sky.resize(bounds[2:],Image.Resampling.LANCZOS)
        a=smooth(32,36,t)
        reveal=smooth(33,40,t)
        mask=Image.new('L',sky.size); md=ImageDraw.Draw(mask)
        mid=sky.width/2; half=sky.width/2*reveal
        md.rectangle((mid-half,0,mid+half,sky.height),fill=round(255*a))
        im.paste(sky,bounds[:2],mask)
        d=ImageDraw.Draw(im)
        grid=tuple(self.c['style']['muted']); dim=(29,49,68)
        for lat in (-30,-15,0,15,30):
            yy=(y+h*(30-lat)/60)*self.h
            d.line((x*self.w,yy,(x+w)*self.w,yy),fill=dim,width=1)
            self.text(im,f'{lat:+d}°' if lat else '0°',(x-.016,yy/self.h),23,grid,anchor='rm')
        for lon in (180,90,0,-90,-180):
            xx=x+w*(180-lon)/360
            self.text(im,f'{lon:d}°',(xx,y+h+.035),25,grid,anchor='mm')
        self.text(im,self.c['text']['map'],(.07,.235),32,bold=True)
        self.text(im,self.c['text']['longitude'],(.5,.78),28,grid,anchor='mm')
        self.text(im,self.c['text']['latitude'],(.07,.27),23,grid)
        self.text(im,self.c['text']['map_note'],(.5,.845),28,anchor='mm')
        self.text(im,self.c['text']['map_limit'],(.5,.93),23,grid,anchor='mm')
        return im

    def frame(self,t):
        stage=0 if t<8 else 1 if t<18 else 2 if t<32 else 3
        st,tx,p=self.c['style'],self.c['text'],self.c['particles']
        im=self.back.copy(); strokes=[]; dots=[]
        # Dim stellar light as the particle paths become the subject.
        dim=0.85-0.20*smooth(6,10,t)
        im=Image.blend(Image.new('RGB',im.size,tuple(st['background'])),im,dim)
        alpha=1-smooth(31.5,35,t)
        if alpha>0:
            for i,(path,origin) in enumerate(zip(self.paths,self.origins)):
                tc=p['first_collision_s']+(p['last_collision_s']-p['first_collision_s'])*i/(p['events']-1)
                q=(t-(tc-p['proton_lead_s']))/p['proton_lead_s']
                if 0<q<1:
                    points=path(np.linspace(max(0,q-.32),q,70))
                    strokes.append((self.project(points),tuple(int(x*.62*alpha) for x in st['proton']),3))
                    dots.append((self.project(path(q)),tuple(int(x*alpha) for x in st['proton']),4))
                if 0<=t-tc<.8:
                    age=(t-tc)/.8
                    col=tuple(int(x*(1-age)*alpha) for x in [255,241,205])
                    dots.append((self.project(origin),col,5+12*age))
                u=(t-tc)/p['flight_s']
                if 0<=u<=1:
                    # Display the conditional subset heading to the Solar System.
                    a=max(0,u-p['trail_s']/p['flight_s'])
                    trail=origin+np.linspace(a,u,22)[:,None]*(self.sun-origin)
                    strokes.append((self.project(trail),tuple(int(x*.7*alpha) for x in st['neutrino']),3))
                    dots.append((self.project(trail[-1]),tuple(int(x*alpha) for x in st['neutrino']),3))
            sunxy=self.project(self.sun)
            dots.append((sunxy,tuple(st['text']),4))
            im=self.glow(im,strokes,dots)
            d=ImageDraw.Draw(im); r=11*self.scale
            d.ellipse((*tuple(sunxy-r),*tuple(sunxy+r)),outline=tuple(st['text']),width=max(1,round(self.scale)))
            self.text(im,tx['sun'],(sunxy[0]/self.w+.02,sunxy[1]/self.h-.025),28)
            centre=self.project([0,0,0])
            self.text(im,tx['centre'],(centre[0]/self.w-.02,centre[1]/self.h+.10),25,tuple(st['muted']),anchor='mm')
            # Colour keys appear only when their process is active.
            self.text(im,tx['proton'],(.07,.82),28,tuple(st['proton']))
            self.text(im,tx['gas'],(.39,.82),28,tuple(st['gas']))
            if t>=p['first_collision_s']:self.text(im,tx['neutrino'],(.72,.82),28,tuple(st['neutrino']))
            self.text(im,tx['selected'] if stage>=2 else tx['schematic'],(.5,.935),23,tuple(st['muted']),anchor='mm')
        blend=smooth(32,35,t)
        if blend>0:im=Image.blend(im,self.map_frame(t),blend)
        self.text(im,tx['titles'][stage],(.045,.07),st['title_px'],bold=True)
        self.text(im,tx['subtitles'][stage],(.045,.135),st['subtitle_px'],tuple(st['muted']))
        # Quiet timeline, no branded title cards or workflow labels.
        d=ImageDraw.Draw(im)
        for i,(a,b) in enumerate(((0,8),(8,18),(18,32),(32,48))):
            x0=.045+i*.058
            d.line((x0*self.w,.185*self.h,(x0+.043)*self.w,.185*self.h),fill=tuple(st['neutrino'] if i==stage else (34,51,69)),width=max(2,round(3*self.scale)))
        return im


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--width',type=int,default=None)
    ap.add_argument('--fps',type=int,default=None)
    ap.add_argument('--stills',action='store_true')
    ap.add_argument('--out',type=Path,default=MEDIA/'legacy/milky_way_neutrinos_legacy_en.mp4')
    args=ap.parse_args()
    cfg=tomllib.loads((HERE/'config.toml').read_text())
    w=args.width or cfg['video']['width']; h=round(w*cfg['video']['height']/cfg['video']['width'])
    fps=args.fps or cfg['video']['fps']; f=Film(cfg,w,h)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    f.frame(cfg['video']['poster_s']).save(args.out.with_suffix('.jpg'),quality=95)
    if args.stills:
        for t in (4,11,17,25,33,40,47):f.frame(t).save(args.out.parent/f'frame-{t:02d}.jpg',quality=94)
        return
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{w}x{h}',
         '-framerate',str(fps),'-i','-','-an','-c:v','libx264','-preset','medium','-crf',str(cfg['video']['crf']),
         '-pix_fmt','yuv420p','-movflags','+faststart',str(args.out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(round(cfg['video']['duration_s']*fps)):
            proc.stdin.write(f.frame(i/fps).tobytes())
            if i%(fps*4)==0:print(f'{i/fps:.0f} / {cfg["video"]["duration_s"]} s',flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError('Video encoding failed')
    print(args.out)


if __name__=='__main__':main()
