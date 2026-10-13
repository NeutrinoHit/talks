"""Copy original paper figures and convert PDF artwork to SVG.

Source identities and checksums are in figures.json. Input archives are optional
downloads; only selected scientific figures enter lecture media.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--output',type=Path,default=HERE.parent.parent/'media')
    p.add_argument('--download',action='store_true')
    args=p.parse_args()
    items=json.loads((HERE/'figures.json').read_text())
    for paper in sorted({x['paper'] for x in items}):
        folder=args.cache/paper
        if not folder.exists():
            if not args.download:raise FileNotFoundError(f'{folder}: supply the source cache or --download')
            args.cache.mkdir(parents=True,exist_ok=True)
            archive=args.cache/f'{paper}.tar'
            urllib.request.urlretrieve(f'https://arxiv.org/src/{paper}',archive)
            folder.mkdir(exist_ok=True)
            with tarfile.open(archive) as t:t.extractall(folder,filter='data')
    for item in items:
        src=args.cache/item['paper']/item['source']
        if hashlib.sha256(src.read_bytes()).hexdigest()!=item['source_sha256']:
            raise ValueError(f'Source checksum changed: {src}')
        dst=args.output/item['output'];dst.parent.mkdir(parents=True,exist_ok=True)
        if src.suffix=='.pdf':subprocess.run(['pdftocairo','-svg',str(src),str(dst)],check=True)
        else:shutil.copy2(src,dst)
    print(f'{len(items)} original figures prepared')


if __name__=='__main__':main()
