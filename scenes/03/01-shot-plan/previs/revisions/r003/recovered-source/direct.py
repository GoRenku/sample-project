#!/usr/bin/env python3
"""Small directing interface. Never rewrites the Blender or motion scripts."""
import argparse
import datetime
import json
from pathlib import Path
from motion import validate

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--config',type=Path,default=ROOT/'scene.json')
p.add_argument('--output',type=Path,help='Save a variant instead of changing the input')
sub=p.add_subparsers(dest='command',required=True)
sub.add_parser('inspect')
s=sub.add_parser('retime'); s.add_argument('duration',type=float,help='New duration; scales movement, cues and dialogue together')
s=sub.add_parser('set'); s.add_argument('path'); s.add_argument('value',help='JSON value; quote lists and strings')
s=sub.add_parser('swap-sides'); s.add_argument('first'); s.add_argument('second')
s=sub.add_parser('camera'); s.add_argument('--start',type=float,required=True); s.add_argument('--end',type=float,required=True)
s.add_argument('--subject',required=True); s.add_argument('--target',required=True)
s.add_argument('--offset',type=float,nargs=3,default=[-.55,-1.6,.05]); s.add_argument('--lens',type=float,default=30)
s.add_argument('--blend',type=float,default=.45); s.add_argument('--id',default='director_camera')
s=sub.add_parser('action'); s.add_argument('--kind',choices=['look','lean','turn','talk'],required=True)
for key in ('actor','target'): s.add_argument('--'+key,required=True)
for key in ('start','end'): s.add_argument('--'+key,type=float,required=True)
s.add_argument('--peak',type=float); s.add_argument('--degrees',type=float,default=22)
s.add_argument('--approach',type=float,default=0); s.add_argument('--id',default='director_action')
s=sub.add_parser('remove'); s.add_argument('id')
args=p.parse_args(); cfg=json.loads(args.config.read_text())
if args.command=='inspect':
    print(json.dumps(cfg,indent=2)); raise SystemExit()
if args.command=='set':
    keys=args.path.split('.'); obj=cfg
    for key in keys[:-1]: obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    key=int(keys[-1]) if isinstance(obj,list) else keys[-1]
    if not isinstance(obj,list) and key not in obj: raise SystemExit('Unknown setting: '+args.path)
    obj[key]=json.loads(args.value)
elif args.command=='retime':
    if args.duration<=0: raise SystemExit('Duration must be positive')
    factor=args.duration/cfg['duration']; cfg['duration']=args.duration
    for point in cfg['walk']['path']: point[0]*=factor
    for c in cfg['characters'].values():
        for field in ('lateral','ahead'):
            if isinstance(c[field],list):
                for point in c[field]: point[0]*=factor
    for cue in cfg['actions']+cfg['camera']['cues']+cfg['beats']+cfg['dialogue']:
        for key in ('start','end','peak','fade_in','fade_out'):
            if key in cue: cue[key]*=factor
elif args.command=='swap-sides':
    a,b=cfg['characters'][args.first],cfg['characters'][args.second]
    a['lateral'],b['lateral']=b['lateral'],a['lateral']
elif args.command=='camera':
    cue=dict(id=args.id,mode='shoulder',start=args.start,end=args.end,subject=args.subject,target=args.target,
             offset=args.offset,lens=args.lens,fade_in=args.blend,fade_out=args.blend)
    cfg['camera']['cues']=[c for c in cfg['camera']['cues'] if c.get('id')!=args.id]+[cue]
elif args.command=='action':
    cue={k:getattr(args,k) for k in ('id','kind','actor','target','start','end')}
    if args.peak is not None: cue['peak']=args.peak
    if args.kind=='lean': cue.update(degrees=args.degrees,approach=args.approach)
    cfg['actions']=[c for c in cfg['actions'] if c.get('id')!=args.id]+[cue]
elif args.command=='remove':
    for cues in (cfg['actions'],cfg['camera']['cues']): cues[:]=[c for c in cues if c.get('id')!=args.id]
validate(cfg)
dest=args.output or args.config
dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists():
    history=ROOT/'history'; history.mkdir(exist_ok=True)
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    (history/(dest.stem+'-'+stamp+'.json')).write_text(dest.read_text())
dest.write_text(json.dumps(cfg,indent=2)+'\n')
print('Saved',dest)
