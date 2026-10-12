"""Local-only viewer server with bounded, no-overwrite movie saving.

The optional viewer button POSTs only its encoded movie, never event arrays.
This server binds 127.0.0.1, checks Origin and MIME, and writes safe filenames
under the configured ignored local output directory, outside the public site.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import re
import tomllib
from urllib.parse import unquote,urlsplit

HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[2]


class Receiver(SimpleHTTPRequestHandler):
    def answer(self,status,payload):
        data=json.dumps(payload).encode()
        self.send_response(status); self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_POST(self):
        port=self.server.server_address[1]
        if self.headers.get('Origin') not in (f'http://127.0.0.1:{port}',f'http://localhost:{port}'):
            self.answer(403,{'error':'Same-origin local recording required'}); return
        path=unquote(urlsplit(self.path).path)
        match=re.fullmatch(r'/recordings/([A-Za-z0-9_-]+\.(mp4|webm))',path)
        mime=self.headers.get('Content-Type','').split(';')[0]
        if not match or mime not in ('video/mp4','video/webm'):
            self.answer(400,{'error':'Expected a safe MP4/WebM recording filename'}); return
        if (mime=='video/mp4') != (match[2]=='mp4'):
            self.answer(400,{'error':'Movie type and extension differ'}); return
        try: size=int(self.headers.get('Content-Length','0'))
        except ValueError: size=0
        if not 0<size<=self.server.upload_limit:
            self.answer(413,{'error':'Invalid or oversized recording'}); return
        destination=self.server.recordings/match[1]
        pending=destination.with_name(destination.name+'.pending')
        try:
            if destination.exists(): raise FileExistsError(destination)
            with pending.open('xb') as out:
                remaining=size
                while remaining:
                    data=self.rfile.read(min(remaining,self.server.read_chunk))
                    if not data: raise ValueError('Incomplete recording')
                    out.write(data); remaining-=len(data)
            if destination.exists(): raise FileExistsError(destination)
            pending.rename(destination)
        except FileExistsError:
            self.answer(409,{'error':'Recording already exists; preserve or move it first'}); return
        except (OSError,ValueError) as error:
            self.answer(400,{'error':str(error)}); return
        self.answer(201,{'saved_as':destination.name})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=HERE/'viewer_recording.toml')
    parser.add_argument('--port',type=int)
    args=parser.parse_args(); cfg=tomllib.loads(args.config.read_text())
    root=(WORKSPACE/cfg['paths']['local_output']).resolve()
    public_roots=(HERE.parent.resolve(),HERE.parents[1]/'_site')
    if not root.is_dir() or any(root.is_relative_to(public) for public in public_roots): parser.error('Prepare local viewers outside the public lecture first')
    records=root/'recordings'; records.mkdir(exist_ok=True)
    handler=partial(Receiver,directory=str(root))
    server=ThreadingHTTPServer(('127.0.0.1',args.port or cfg['recording']['port']),handler)
    server.recordings=records
    server.upload_limit=cfg['recording']['maximum_upload_mb']*1024**2
    server.read_chunk=1024**2
    print(f'Local recording server: http://127.0.0.1:{server.server_address[1]}/muon.html?local_save=1',flush=True)
    server.serve_forever()


if __name__=='__main__': main()
