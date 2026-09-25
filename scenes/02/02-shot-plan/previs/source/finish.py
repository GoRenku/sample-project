import json, pathlib, argparse, subprocess
R=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser(); p.add_argument('--frames-dir',required=True); p.add_argument('--output',required=True); p.add_argument('--project-root',required=True); a=p.parse_args(); c=json.loads((R/'scene.json').read_text()); dst=pathlib.Path(a.output)
if dst.exists():raise SystemExit('Refusing to overwrite completed movie: '+str(dst))
tmp=dst.with_suffix('.encoding.mp4')
audio=pathlib.Path(a.project_root)/c['audio']['projectRelativePath']
delay=round(c['audio']['offsetSeconds']*44100)
subprocess.run(['ffmpeg','-v','error','-n','-framerate',str(c['fps']),'-start_number','1','-i',str(pathlib.Path(a.frames_dir)/'%04d.png'),'-i',str(audio),'-filter_complex',f'[1:a]aresample=44100,adelay={delay}S:all=1,apad,atrim=duration={c["duration"]}[a]','-map','0:v','-map','[a]','-t',str(c['duration']),'-c:v','libx264','-crf','19','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(tmp)],check=True)
subprocess.run(['ffprobe','-v','error','-show_entries','stream=nb_frames,r_frame_rate,width,height,duration','-of','json',str(tmp)],check=True); tmp.rename(dst)
