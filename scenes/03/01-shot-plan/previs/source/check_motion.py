#!/usr/bin/env python3
"""Checks for the current blocking and the three requested director controls."""
import copy
import json
import math
from pathlib import Path
from motion import validate,evaluate,camera,curve

ROOT=Path(__file__).resolve().parent
c=json.loads((ROOT/'scene.json').read_text());validate(c)
minimum=100; max_step=0; last=None
for f in range(round(c['duration']*c['fps'])):
    t=f/c['fps']; poses,pos=evaluate(c,t); eye,aim,lens=camera(c,t,poses,pos)
    assert all(math.isfinite(x) for x in eye+aim+[lens])
    minimum=min(minimum,math.dist(pos['mara'],pos['urban']))
    for n in c['characters']:
        assert -4.5<pos[n][0]<4.5,'Character left the quay'
        for extra in c['supporting']:
            assert math.dist(pos[n],pos[extra])>.72,(n,extra,t)
    if last: max_step=max(max_step,math.dist(last,eye))
    last=eye
assert minimum>1.0 and max_step<.15
end=evaluate(c,14)[0]; before=evaluate(c,12)[0]
assert all(math.dist(end[n]['position'],before[n]['position'])<1e-6 for n in c['characters'])
# Side swap preserves forward lead and exchanges only lateral placement.
v=copy.deepcopy(c)
v['characters']['mara']['lateral'],v['characters']['urban']['lateral']=v['characters']['urban']['lateral'],v['characters']['mara']['lateral']
assert evaluate(v,5)[1]['mara'][0]>evaluate(v,5)[1]['urban'][0]
# Shoulder interval is effective at its midpoint and identical to base outside.
v=copy.deepcopy(c);v['camera']['cues']=[dict(mode='shoulder',subject='mara',target='urban',start=3,end=5,offset=[.38,-1.05,.16],lens=32)]
pose,pos=evaluate(v,4); eye,aim,lens=camera(v,4,pose,pos)
assert math.dist(eye,pos['mara'])<2.5 and lens==32
pose,pos=evaluate(v,6);assert camera(v,6,pose,pos)==camera(c,6,pose,pos)
# Lean reaches its requested peak and settles without changing the base layout.
v=copy.deepcopy(c);v['actions'].append(dict(kind='lean',actor='mara',target='soldier_blue',start=9,peak=10,end=11,degrees=25,approach=.4))
assert abs(evaluate(v,10)[0]['mara']['lean']-math.radians(25))<1e-6
assert evaluate(v,8)[0]==evaluate(c,8)[0]
report=dict(valid=True,frames=round(c['duration']*c['fps']),minimum_lead_separation_metres=minimum,
    maximum_camera_step_metres=max_step,checks=['finite camera path','leads separated','leads remain on quay',
    'supporting cast clearance','stop settles','side swap','shoulder interval','lean target and peak'])
(ROOT/'qa/motion_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
