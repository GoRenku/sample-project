"""Deterministic, Blender-independent blocking. Seconds, metres, radians.

World +Y is down the quay; +X is a walker's right (toward the water).
The same evaluator drives baked Blender animation and director QA.
"""
import math


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x*x*(3-2*x)


def curve(keys, t):
    """Shape-preserving cubic interpolation: no overshoot or stops at every key."""
    if t <= keys[0][0]: return keys[0][1]
    if t >= keys[-1][0]: return keys[-1][1]
    slopes = [(b[1]-a[1])/(b[0]-a[0]) for a,b in zip(keys,keys[1:])]
    tangents = [slopes[0]]
    for i in range(1,len(keys)-1):
        a,b = slopes[i-1],slopes[i]
        h0,h1 = keys[i][0]-keys[i-1][0],keys[i+1][0]-keys[i][0]
        w0,w1 = 2*h1+h0,h1+2*h0
        tangents.append((w0+w1)/(w0/a+w1/b) if a*b>0 else 0.0)
    tangents.append(slopes[-1])
    for i,(a,b) in enumerate(zip(keys,keys[1:])):
        if a[0] <= t <= b[0]:
            h=b[0]-a[0]; u=(t-a[0])/h
            return ((2*u**3-3*u*u+1)*a[1]+(u**3-2*u*u+u)*h*tangents[i]
                    +(-2*u**3+3*u*u)*b[1]+(u**3-u*u)*h*tangents[i+1])


def value(v,t):
    return curve(v,t) if isinstance(v,list) else v


def envelope(c,t):
    if t<c['start'] or t>c['end']: return 0.0
    if 'peak' in c:
        p=c['peak']
        return smooth((t-c['start'])/(p-c['start'])) if t<=p else smooth((c['end']-t)/(c['end']-p))
    fi,fo=c.get('fade_in',.5),c.get('fade_out',.5)
    return min(smooth((t-c['start'])/fi) if fi else 1,
               smooth((c['end']-t)/fo) if fo else 1)


def angle_mix(a,b,w):
    return a+math.atan2(math.sin(b-a),math.cos(b-a))*w


def local_offset(offset,yaw):
    x,y,z=offset; c,s=math.cos(yaw),math.sin(yaw)
    return (c*x-s*y,s*x+c*y,z)


def route(cfg,t):
    points=cfg['walk']['path']
    x=curve([[p[0],p[1]] for p in points],t)
    y=curve([[p[0],p[2]] for p in points],t)
    # Last nonzero tangent retains the walking axis when the pair stop.
    a=max(0,t-.05); b=min(cfg['duration'],t+.05)
    dx=curve([[p[0],p[1]] for p in points],b)-curve([[p[0],p[1]] for p in points],a)
    dy=curve([[p[0],p[2]] for p in points],b)-curve([[p[0],p[2]] for p in points],a)
    if abs(dx)+abs(dy)<1e-6:
        for p,q in reversed(list(zip(points,points[1:]))):
            if p[0]<=t and abs(q[1]-p[1])+abs(q[2]-p[2])>1e-6:
                dx,dy=q[1]-p[1],q[2]-p[2]; break
    return (x,y), math.atan2(-dx,dy)


def base_positions(cfg,t):
    center,yaw=route(cfg,t); out={}
    for name,c in cfg['characters'].items():
        o=local_offset((value(c['lateral'],t),value(c['ahead'],t),0),yaw)
        out[name]=(center[0]+o[0],center[1]+o[1],0)
    out.update({n:tuple(c['position']) for n,c in cfg['supporting'].items()})
    return out


def evaluate(cfg,t):
    positions=base_positions(cfg,t); _,heading=route(cfg,t)
    # Approaches are evaluated before gaze, so all targets use current positions.
    for cue in cfg['actions']:
        if cue['kind']=='lean' and cue.get('approach',0):
            w=envelope(cue,t); a=positions[cue['actor']]; b=positions[cue['target']]
            dx,dy=b[0]-a[0],b[1]-a[1]; d=max(1e-6,math.hypot(dx,dy))
            travel=min(cue['approach'],max(0,d-.8))*w
            positions[cue['actor']]=(a[0]+dx/d*travel,a[1]+dy/d*travel,0)
    poses={}
    for name,c in {**cfg['characters'],**cfg['supporting']}.items():
        yaw=heading if name in cfg['characters'] else math.radians(c['yaw'])
        head=yaw; lean=0; talk=0
        for cue in cfg['actions']:
            if cue['actor']!=name: continue
            w=envelope(cue,t)
            if not w: continue
            a,b=positions[name],positions[cue['target']]
            toward=math.atan2(-(b[0]-a[0]),b[1]-a[1])
            if cue['kind']=='look':
                head=angle_mix(head,toward,w)
                yaw=angle_mix(yaw,toward,w*cue.get('body_weight',.15))
            elif cue['kind'] in ('turn','lean','talk'):
                yaw=angle_mix(yaw,toward,w); head=angle_mix(head,toward,w)
                if cue['kind']=='lean': lean=math.radians(cue.get('degrees',22))*w
                if cue['kind']=='talk': talk=max(talk,w)
        # Anatomical limit prevents an implausible backwards-facing head.
        head_delta=math.atan2(math.sin(head-yaw),math.cos(head-yaw))
        head_delta=max(-math.radians(80),min(math.radians(80),head_delta))
        poses[name]={'position':positions[name],'yaw':yaw,'head_yaw':head_delta,'lean':lean,'talk':talk}
    return poses,positions


def camera(cfg,t,poses,positions):
    _,heading=route(cfg,t)
    def shot(c):
        if c.get('mode','follow')=='shoulder':
            subject=c['subject']; p=poses[subject]; h=cfg['characters'][subject]['height']*.9
            o=local_offset(c.get('offset',[-.55,-1.6,.05]),p['yaw'])
            eye=[p['position'][i]+o[i]+(h if i==2 else 0) for i in range(3)]
        else:
            center=[sum(positions[n][i] for n in cfg['characters'])/len(cfg['characters']) for i in range(3)]
            o=local_offset(c['offset'],heading)
            eye=[center[i]+o[i] for i in range(3)]
        target=c.get('target','pair')
        if target=='pair':
            aim=[sum(positions[n][i] for n in cfg['characters'])/len(cfg['characters']) for i in range(3)]
            aim[2]=c.get('target_height',1.0)
            aim[1]+=c.get('look_ahead',.8)
        else:
            aim=list(positions[target]); spec={**cfg['characters'],**cfg['supporting']}[target]
            aim[2]+=spec['height']*.86
        return eye,aim,c.get('lens',35)
    current=shot(cfg['camera']['base'])
    for cue in cfg['camera']['cues']:
        w=envelope(cue,t)
        if w:
            other=shot(cue)
            current=([a+(b-a)*w for a,b in zip(current[0],other[0])],
                     [a+(b-a)*w for a,b in zip(current[1],other[1])],current[2]+(other[2]-current[2])*w)
    return current


def validate(cfg):
    assert cfg['duration']>0 and cfg['fps']>0
    names=set(cfg['characters'])|set(cfg['supporting'])
    assert not(set(cfg['characters'])&set(cfg['supporting']))
    path=cfg['walk']['path']; assert path[0][0]==0 and path[-1][0]==cfg['duration']
    assert all(a[0]<b[0] for a,b in zip(path,path[1:]))
    for c in cfg['characters'].values():
        for k in ('lateral','ahead'):
            v=c[k]
            if isinstance(v,list):
                assert len(v)>=2 and all(a[0]<b[0] for a,b in zip(v,v[1:]))
    for c in cfg['actions']+cfg['camera']['cues']:
        assert 0<=c['start']<c['end']<=cfg['duration'],c
        if 'peak' in c: assert c['start']<c['peak']<c['end']
        if 'actor' in c:
            assert c['actor'] in names and c['kind'] in ('look','turn','lean','talk')
            if c['kind']=='lean': assert c['actor'] in cfg['characters']
        if 'target' in c: assert c['target'] in names|{'pair'}
        if c.get('mode')=='shoulder': assert c['subject'] in cfg['characters']
    for c in cfg['dialogue']:
        assert 0<=c['start']<c['end']<=cfg['duration']
    return True
