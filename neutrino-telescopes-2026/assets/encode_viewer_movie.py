"""Encode a real viewer capture for slides; no event arrays are published.

Uniform scale and letterbox preserve the WebGL image's aspect ratio. Titles
state the component and clock actually selected for each exported recording.
All layout, encoding and text parameters are in event_movie_layout.toml.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile
import tomllib
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',choices=['muon','cascade'],required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--config',type=Path,default=HERE/'event_movie_layout.toml')
    args=parser.parse_args(); cfg=tomllib.loads(args.config.read_text())
    v=cfg['video']; out=(args.out or HERE.parent/'media/events'/f'simulated_{args.kind}_response_en.mp4').resolve()
    if not args.input.is_file(): parser.error('The real browser capture must exist first')
    if out==args.input.resolve(): parser.error('Preserve the original capture; use a different output')
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='viewer-titles-') as tmp:
        # Portable caption artwork: this Mac's ffmpeg has no drawtext filter.
        labels=Image.new('RGBA',(v['width'],v['height']),(0,0,0,0))
        draw=ImageDraw.Draw(labels)
        color=lambda value:value.replace('0x','#')
        draw.rectangle([0,0,v['width'],v['header_px']],fill=color(v['background']))
        draw.rectangle([0,v['height']-v['footer_px'],v['width'],v['height']],fill=color(v['background']))
        draw.text((v['text_x'],v['title_y']),cfg[args.kind]['title'],font=ImageFont.truetype(v['font'],v['title_size']),fill=color(v['title_color']))
        draw.multiline_text((v['text_x'],v['height']-v['footer_px']+v['note_offset']),cfg[args.kind]['note'],font=ImageFont.truetype(v['font'],v['note_size']),fill=color(v['note_color']),spacing=v['note_line_spacing']-v['note_size'])
        overlay=Path(tmp)/'labels.png'; labels.save(overlay)
        height=v['height']-v['header_px']-v['footer_px']
        filter_=f"[0:v]fps={v['fps']},scale={v['width']}:{height}:force_original_aspect_ratio=decrease,pad={v['width']}:{v['height']}:(ow-iw)/2:{v['header_px']}+({height}-ih)/2:color={v['background']}[base];[base][1:v]overlay=0:0:shortest=1[v]"
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(args.input),'-loop','1','-i',str(overlay),'-an','-filter_complex',filter_,'-map','[v]','-c:v',v['codec'],'-preset',v['preset'],'-crf',str(v['crf']),'-pix_fmt',v['pixel_format'],'-movflags','+faststart',str(out)],check=True)
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(v['poster_time_s']),'-i',str(out),'-frames:v','1',str(out.with_suffix('.jpg'))],check=True)
    print(out)


if __name__=='__main__':main()
