#!/usr/bin/env python3
"""Build and optionally render a revision using the installed Blender CLI."""
import argparse
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--config',type=Path,default=ROOT/'scene.json')
p.add_argument('--out',type=Path,required=True,help='New revision folder, e.g. renders/v002')
p.add_argument('--build-only',action='store_true')
args=p.parse_args();out=args.out.resolve()
if out.exists() and any(out.iterdir()):raise SystemExit('Use an empty output folder to preserve prior takes: '+str(out))
cmd=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--python',str(ROOT/'build_previs.py'),
     '--','--config',str(args.config.resolve()),'--out',str(out)]
if not args.build_only:cmd.append('--render')
subprocess.run(cmd,check=True)
if not args.build_only:subprocess.run([sys.executable,str(ROOT/'finish.py'),str(out)],check=True)
