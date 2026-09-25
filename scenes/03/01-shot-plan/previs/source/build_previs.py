"""Run using Blender --background --python build_previs.py -- [options].

No runtime handlers: all motion is baked into ordinary editable keyframes.
Re-run this unchanged builder after directing through scene.json/direct.py.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from motion import evaluate, camera, validate

p=argparse.ArgumentParser()
p.add_argument('--config',default=str(ROOT/'scene.json'))
p.add_argument('--out',default=str(ROOT/'renders/v001'))
p.add_argument('--render',action='store_true')
p.add_argument('--frames',help='Comma-separated preview frames')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
cfg=json.loads(Path(args.config).read_text()); validate(cfg)
OUT=Path(args.out).resolve(); OUT.mkdir(parents=True,exist_ok=True)
(OUT/'config.snapshot.json').write_text(json.dumps(cfg,indent=2)+'\n')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x,scene.render.resolution_y=cfg['resolution']
scene.render.resolution_percentage=100
scene.render.fps=cfg['fps']
scene.frame_start=1; scene.frame_end=round(cfg['duration']*cfg['fps'])
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.display.shading.light='STUDIO'
scene.display.shading.studio_light='paint.sl'
scene.display.shading.studiolight_rotate_z=.3
scene.display.shading.color_type='OBJECT'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.1
scene.display.shading.curvature_valley_factor=.7
scene.display.shading.show_object_outline=True
scene.display.shading.object_outline_color=(.12,.15,.17)
scene.display.shading.background_type='WORLD'
scene.world=bpy.data.worlds.new('Neutral background')
scene.world.color=(.19,.23,.26)
scene.view_settings.view_transform='Standard'
scene.display.render_aa='16'

collections={}
for name in ('LEADS','SUPPORTING','PROPS','HARBOR','CAMERAS'):
    col=bpy.data.collections.new(name); scene.collection.children.link(col); collections[name]=col

def link(obj,collection):
    for col in list(obj.users_collection): col.objects.unlink(obj)
    collections[collection].objects.link(obj)

def rgb(h):
    # Workbench display swatches; deliberately bright, distinguishable proxies.
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)

def cube(name,loc,size,color,collection='PROPS',parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=bpy.context.object; o.name=name; link(o,collection)
    o.parent=parent; o.location=loc; o.scale=size; o.color=rgb(color)
    return o

def empty(name,collection,parent=None,loc=(0,0,0)):
    o=bpy.data.objects.new(name,None); collections[collection].objects.link(o)
    o.empty_display_type='PLAIN_AXES'; o.empty_display_size=.25
    o.parent=parent; o.location=loc
    return o

def character(name,c,collection):
    h=c['height']; root=empty(name,collection)
    root['director_id']=name; root['label']=c['label']; root['color_hex']=c['color']
    # Eight rectangular proxies: feet/legs, torso, arms, head, facing chip.
    torso=empty(name+'.torso_pivot',collection,root,(0,0,.47*h))
    cube(name+'.body',(0,0,.17*h),(.30*h,.20*h,.34*h),c['color'],collection,torso)
    head=empty(name+'.head_pivot',collection,torso,(0,0,.44*h))
    cube(name+'.head',(0,0,0),(.22*h,.20*h,.18*h),c['color'],collection,head)
    cube(name+'.facing',(0,.105*h,0),(.13*h,.014*h,.055*h),'F3EDD9',collection,head)
    legs=[]; arms=[]
    for side in (-1,1):
        leg=empty(name+('.leg_L' if side<0 else '.leg_R'),collection,root,(side*.087*h,0,.47*h))
        cube(leg.name+'.block',(0,0,-.235*h),(.135*h,.17*h,.47*h),c['color'],collection,leg)
        legs.append(leg)
        arm=empty(name+('.arm_L' if side<0 else '.arm_R'),collection,torso,(side*.207*h,0,.31*h))
        cube(arm.name+'.block',(0,0,-.16*h),(.095*h,.12*h,.36*h),c['color'],collection,arm)
        arms.append(arm)
    if name=='urban':
        cube('urban.cannon_drawing',(.19*h,.13*h,.12*h),(.08,.09,.48),'ECE0BD',collection,torso)
    return dict(root=root,torso=torso,head=head,legs=legs,arms=arms)

leads={n:character(n,c,'LEADS') for n,c in cfg['characters'].items()}
extras={n:character(n,c,'SUPPORTING') for n,c in cfg['supporting'].items()}
for n,r in extras.items():
    c=cfg['supporting'][n]; r['root'].location=c['position']; r['root'].rotation_euler.z=math.radians(c['yaw'])
    if c['activity'] in ('mend','hammer','tend'): r['torso'].rotation_euler.x=-.18
    if c['activity']=='hammer':
        cube(n+'.hammer',(.0,0,-.28),(.25,.10,.10),'D6D9DC','SUPPORTING',r['arms'][1])

cube('quay',(0,7,-.25),(9.4,42,.5),'B6B5AD','HARBOR')
cube('harbor_water',(17,7,-.64),(24,70,.12),'69858D','HARBOR')
cube('quay_edge',(4.7,7,-.07),(.25,42,.16),'D1CFC4','HARBOR')
cube('warehouse_wall',(-5.4,9,1.7),(1.0,40,3.4),'949B99','HARBOR')
for y in range(-6,28,6):
    cube('warehouse_recess_'+str(y),(-4.88,y,1.0),(.025,2,2),'737F7F','HARBOR')
for y in range(-6,28,3):
    cube('quay_joint_'+str(y),(0,y,.006),(9.2,.025,.012),'A2A69F','HARBOR')
for y in (-2,5,13,20):
    cube('mooring_post_'+str(y),(4.2,y,.3),(.28,.32,.6),'677676','HARBOR')
for name,c in cfg['props'].items(): cube(name,c['position'],c['size'],c['color'])
# Net is represented by a coarse five-line grid, not simulated geometry.
nx,ny,nz=cfg['props']['net_patch']['position']
for i in range(5):
    cube('net_strand_'+str(i),(nx-.5+i*.25,ny,nz+.035),(.022,1.7,.015),'797E72')
for i in range(6):
    cube('net_cross_'+str(i),(nx,ny-.8+i*.3,nz+.036),(1.2,.022,.015),'797E72')

data=bpy.data.cameras.new('Follow camera'); cam=bpy.data.objects.new('camera.follow',data)
collections['CAMERAS'].objects.link(cam); scene.camera=cam
data.sensor_width=36; data.clip_start=.08; data.clip_end=180
data.lens=cfg['camera']['base']['lens']

distances={n:0.0 for n in leads}; previous={}; previous_rotation=None
qa=[]
for frame in range(1,scene.frame_end+1):
    t=(frame-1)/cfg['fps']; poses,positions=evaluate(cfg,t)
    for name,r in leads.items():
        pose=poses[name]; pos=pose['position']; c=cfg['characters'][name]
        step=math.dist(previous.get(name,pos),pos); distances[name]+=step; previous[name]=pos
        # Distance-driven gait slows and settles when the director holds position.
        speed=step*cfg['fps']
        if frame==1:
            future=evaluate(cfg,1/cfg['fps'])[0][name]['position']; speed=math.dist(pos,future)*cfg['fps']
        amp=math.radians(cfg['walk']['leg_swing_degrees'])*min(1,speed/.85)
        phase=distances[name]/cfg['walk']['stride_metres']*2*math.pi+c['phase']
        swing=math.sin(phase)*amp
        r['root'].location=pos
        r['root'].rotation_euler.z=pose['yaw']
        r['torso'].rotation_euler.x=-pose['lean']
        r['head'].rotation_euler.z=pose['head_yaw']
        r['head'].rotation_euler.x=.045*math.sin(t*3.2)*pose['talk']
        for i,leg in enumerate(r['legs']): leg.rotation_euler.x=swing*(-1 if i else 1)
        for i,arm in enumerate(r['arms']): arm.rotation_euler.x=-swing*.65*(-1 if i else 1)
        r['arms'][0].rotation_euler.x+=(-.3+.10*math.sin(t*2.6))*pose['talk']
        for key in ('root','torso','head'):
            r[key].keyframe_insert(data_path='location',frame=frame)
            r[key].keyframe_insert(data_path='rotation_euler',frame=frame)
        for o in r['legs']+r['arms']: o.keyframe_insert(data_path='rotation_euler',frame=frame)
    for n,r in extras.items():
        activity=cfg['supporting'][n]['activity']
        pose=poses[n]; talk=pose['talk']
        r['root'].rotation_euler.z=pose['yaw']
        r['head'].rotation_euler.z=pose['head_yaw']
        r['head'].rotation_euler.x=.04*math.sin(t*3.2+1.7)*talk
        r['torso'].rotation_euler.x=(-.18 if activity in ('mend','hammer','tend') else 0)*(1-talk)
        for key in ('root','head','torso'): r[key].keyframe_insert(data_path='rotation_euler',frame=frame)
        for i,arm in enumerate(r['arms']):
            work=(-.8+.32*math.sin(t*5+i)) if activity=='hammer' else ((-.65+.10*math.sin(t*3+i)) if activity!='idle' else 0)
            # Pause repair work; gesture with the free hand, keeping the hammer lowered.
            gesture=(-.32+.08*math.sin(t*2.6+1.7)) if i==0 else -.10
            arm.rotation_euler.x=work*(1-talk)+gesture*talk
            arm.keyframe_insert(data_path='rotation_euler',frame=frame)
    eye,aim,lens=camera(cfg,t,poses,positions)
    cam.location=eye
    rotation=(Vector(aim)-Vector(eye)).to_track_quat('-Z','Y')
    cam.rotation_euler=rotation.to_euler('XYZ',previous_rotation) if previous_rotation else rotation.to_euler()
    previous_rotation=cam.rotation_euler.copy()
    data.lens=lens
    cam.keyframe_insert(data_path='location',frame=frame); cam.keyframe_insert(data_path='rotation_euler',frame=frame)
    data.keyframe_insert(data_path='lens',frame=frame)
    qa.append({'frame':frame,'time':round(t,4),'characters':poses,'camera':{'eye':eye,'aim':aim,'lens':lens}})

for b in cfg['beats']: scene.timeline_markers.new(b['label'],frame=round(b['start']*cfg['fps'])+1)
for d in cfg['dialogue']: scene.timeline_markers.new(d['speaker']+': '+d['text'],frame=round(d['start']*cfg['fps'])+1)
# Embed directing configuration and instructions inside the blend too.
for name,body in [('DIRECTOR_CONFIG.json',json.dumps(cfg,indent=2)),('READ_ME','Edit scene.json or use direct.py, then rebuild with the same script. All animation is baked. World +Y = walk; +X = walker right. Color IDs live on character root objects.')]:
    txt=bpy.data.texts.new(name); txt.write(body)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.overlay.show_overlays=False
scene.frame_set(1)
scene.render.filepath=str(OUT/'frames/frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'harbor_previs.blend'))
(OUT/'motion.json').write_text(json.dumps(qa,indent=2)+'\n')
if args.frames:
    for frame in map(int,args.frames.split(',')):
        scene.frame_set(frame); scene.render.filepath=str(OUT/f'preview_{frame:04d}.png')
        bpy.ops.render.render(write_still=True)
elif args.render:
    (OUT/'frames').mkdir(exist_ok=True)
    scene.render.filepath=str(OUT/'frames/frame_')
    bpy.ops.render.render(animation=True)
print('PREVIS_READY',OUT)
