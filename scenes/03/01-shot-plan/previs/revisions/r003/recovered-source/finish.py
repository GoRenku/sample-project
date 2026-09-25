#!/usr/bin/env python3
"""Encode a clean guidance MP4, an annotated review MP4, subtitles and contact sheet."""
import argparse
import json
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('render_folder',type=Path,nargs='?',default=ROOT/'renders/v001')
args=p.parse_args(); folder=args.render_folder.resolve()
cfg=json.loads((folder/'config.snapshot.json').read_text()); w,h=cfg['resolution']; fps=cfg['fps']
frames=sorted((folder/'frames').glob('frame_*.png'))
assert len(frames)==round(fps*cfg['duration']),f'Expected {fps*cfg["duration"]} frames, found {len(frames)}'
font_path='/System/Library/Fonts/Supplemental/Arial.ttf'
def font(n): return ImageFont.truetype(font_path,n)
small,normal,big=font(14),font(17),font(21)
def run(cmd): subprocess.run(cmd,check=True)
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(fps),'-start_number','1',
     '-i',str(folder/'frames/frame_%04d.png'),'-c:v','libx264','-crf','17','-pix_fmt','yuv420p',
     '-movflags','+faststart',str(folder/'harbor_clean.mp4')])

def clock(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
srt='\n\n'.join(f'{i}\n{clock(d["start"])} --> {clock(d["end"])}\n{d["speaker"]}: {d["text"]}' for i,d in enumerate(cfg['dialogue'],1))+'\n'
(folder/'dialogue.srt').write_text(srt)

proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24',
    '-video_size',f'{w}x{h+124}','-framerate',str(fps),'-i','-','-c:v','libx264','-crf','18',
    '-pix_fmt','yuv420p','-movflags','+faststart',str(folder/'harbor_review.mp4')],stdin=subprocess.PIPE)
samples=[]
for i,path in enumerate(frames):
    t=i/fps; im=Image.new('RGB',(w,h+124),'#17222B'); d=ImageDraw.Draw(im)
    d.text((18,10),f'HARBOR  /  BLOCKING {folder.name.upper()}',font=normal,fill='#E9E8DF')
    d.text((w-205,10),f'{t:05.2f}s  |  FRAME {i+1:03}',font=normal,fill='#D8E0E2')
    x=18
    for key,label in [('mara','MARA'),('urban','URBAN'),('refugee_teal','NETS'),('monk_violet','SHRINE'),('soldier_blue','BLUE SOLDIER')]:
        c={**cfg['characters'],**cfg['supporting']}[key]
        d.rectangle((x,38,x+12,50),fill='#'+c['color']);d.text((x+19,35),label,font=small,fill='#E7EBEA')
        x+=115 if key!='monk_violet' else 125
    with Image.open(path) as frame: im.paste(frame,(0,60))
    beat=next(b['label'] for b in cfg['beats'] if b['start']<=t<b['end'])
    d.text((18,h+68),beat,font=small,fill='#B3C5CB')
    dialogue=next((c for c in cfg['dialogue'] if c['start']<=t<c['end']),None)
    if dialogue:
        text=dialogue['speaker'].upper()+': '+dialogue['text']
        d.text((18,h+91),text,font=big,fill='#F6F1DE')
    else: d.text((18,h+91),'[ observation / breathing space ]',font=normal,fill='#7D969F')
    proc.stdin.write(im.tobytes())
    if i in (0,60,120,180,240,336): samples.append((t,im.copy()))
proc.stdin.close(); assert proc.wait()==0
sheet=Image.new('RGB',(960,3*350),'#17222B')
for i,(t,im) in enumerate(samples):
    im.thumbnail((480,350));sheet.paste(im,((i%2)*480,(i//2)*350))
sheet.save(folder/'contact_sheet.jpg',quality=94)
probe=subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries',
    'stream=width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',str(folder/'harbor_clean.mp4')],text=True)
info=json.loads(probe);assert abs(float(info['format']['duration'])-cfg['duration'])<.001
assert int(info['streams'][0]['nb_read_frames'])==len(frames)
(folder/'video_validation.json').write_text(json.dumps(info,indent=2)+'\n')
print('Encoded and verified',len(frames),'frames;',cfg['duration'],'seconds:',folder)
