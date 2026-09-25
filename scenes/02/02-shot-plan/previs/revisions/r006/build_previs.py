import bpy, math, json, sys, argparse, random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser(); p.add_argument('--out',required=True); p.add_argument('--frames-dir',required=True); p.add_argument('--frames'); a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
c=json.loads((R/'scene.json').read_text()); out=Path(a.out); out.mkdir(parents=True,exist_ok=True); frames=Path(a.frames_dir); frames.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); s=bpy.context.scene
s.render.engine='BLENDER_WORKBENCH'; s.render.resolution_x,s.render.resolution_y=c['resolution']; s.render.resolution_percentage=100; s.render.fps=c['fps']; s.frame_start=1; s.frame_end=round(c['fps']*c['duration']); s.render.image_settings.file_format='PNG'; s.render.filepath=str(frames)+'/'
s.world=bpy.data.worlds.new('World'); s.world.color=(.12,.14,.16); s.view_settings.view_transform='Standard'
sh=s.display.shading; sh.light='STUDIO'; sh.studio_light='paint.sl'; sh.color_type='OBJECT'; sh.show_shadows=True; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.curvature_ridge_factor=1.2; sh.curvature_valley_factor=1; sh.show_object_outline=True; sh.object_outline_color=(.055,.048,.04); sh.background_type='WORLD'; s.display.render_aa='8'
def color(h): return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
def cube(n,loc,scale,col,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1); o=bpy.context.object; o.name=n; o.parent=parent; o.location=loc; o.scale=scale; o.color=color(col); return o
def ball(n,loc,scale,col,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8); o=bpy.context.object; o.name=n; o.parent=parent; o.location=loc; o.scale=scale; o.color=color(col)
 for f in o.data.polygons:f.use_smooth=True
 return o
def empty(n,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(n,None); s.collection.objects.link(o); o.parent=parent; o.location=loc; return o
def rod(n,start,end,r,col,parent=None):
 d=Vector(end)-Vector(start); bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=1,depth=1); o=bpy.context.object; o.name=n; o.parent=parent; o.location=(Vector(start)+Vector(end))/2; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.scale=(r,r,d.length); o.color=color(col); return o
def line(n,pts,col='29251E',r=.005,parent=None):
 cr=bpy.data.curves.new(n,'CURVE'); cr.dimensions='3D'; cr.bevel_depth=r; cr.bevel_resolution=1; sp=cr.splines.new('POLY'); sp.points.add(len(pts)-1)
 for q,pt in zip(sp.points,pts):q.co=(*pt,1)
 o=bpy.data.objects.new(n,cr); s.collection.objects.link(o); o.parent=parent; o.color=color(col); return o
# Spatial location sheet: five west windows, icon wall north, east ledgers.
cube('stone floor',(0,0,-.12),(7.2,12,.24),'78786E')
for x in range(-3,4):
 for y in range(-5,6): cube('floor joint',(x,y,.004),(.012,1,.008),'5B5C56'); cube('floor joint',(x,y,.005),(1,.012,.008),'5B5C56')
cube('north wall',(0,5.7,2.6),(7.2,.25,5.2),'99998C'); cube('east wall',(3.6,0,2.6),(.25,11.5,5.2),'99998C')
# West wall built around windows, with arched surrounds.
cube('west sill wall',(-3.6,0,.5),(.3,11.5,1),'99998C'); cube('west upper wall',(-3.6,0,4.85),(.3,11.5,.7),'99998C')
for y in (-4.4,-2.2,0,2.2,4.4):
 cube('window cold daylight',(-3.68,y,2.7),(.06,1.35,3.35),'BAD0D8')
 for yy in (y-.78,y+.78):cube('window jamb',(-3.58,yy,2.75),(.35,.2,3.5),'C4C1AF')
 cube('deep window sill',(-3.45,y,1.05),(.55,1.7,.15),'C4C1AF')
 cube('window mullion',(-3.56,y,2.45),(.08,.055,2.8),'716F62'); cube('window crossbar',(-3.56,y,2.8),(.08,1.4,.05),'716F62')
 pts=[(-3.4,y+.79*math.cos(q*math.pi/24),3.62+.79*math.sin(q*math.pi/24)) for q in range(25)]; line('stone arch',pts,'C4C1AF',.11)
for y in (-5.5,-3.3,-1.1,1.1,3.3,5.5):cube('west wall pier',(-3.6,y,2.6),(.3,.62,5.2),'99998C')
for y in (-4,-2,0,2,4):cube('ceiling beam',(0,y,4.85),(7.2,.22,.25),'403A30')
cube('icon wall paneling',(0,5.48,.8),(7,.13,1.6),'493E2E')
for x in (-2.6,-1.3,0,1.3,2.6):
 cube('icon gold frame',(x,5.47,3.1),(1.15,.13,2.05),'9A7E42'); cube('icon dark ground',(x,5.38,3.1),(1.02,.035,1.88),'413E30')
 ball('icon halo',(x,5.34,3.52),(.3,.025,.33),'B59D5D'); ball('icon painted face',(x,5.29,3.49),(.14,.02,.2),'9F8360'); cube('icon painted robes',(x,5.29,2.85),(.5,.025,.65),'716044')
for y in (1.8,4):
 cube('ledger sideboard',(3.1,y,.55),(.65,1.6,1.1),'524736'); cube('cabinet top',(3.08,y,1.14),(.8,1.8,.1),'716047')
# Central scarred wood table.
cube('council tabletop',(0,0,.94),(1.8,5,.15),'67503A')
for x in (-.68,.68):
 for y in (-1.95,1.95):cube('table leg',(x,y,.45),(.16,.18,.9),'4F3E2F')
for x in (-.6,-.3,0,.3,.6):cube('plank seam',(x,0,1.019),(.012,5,.006),'403629')
random.seed(23)
for i in range(35):
 x=random.uniform(-.8,.8); y=random.uniform(-2.3,2.3); line('table wear',[(x,y,1.023),(x+.015,y+random.uniform(.05,.3),1.023)],'A18D69',.003)
def chair(x,y):
 cube('chair seat',(x,y,.48),(.65,.64,.12),'493B2E'); cube('chair back',(x+.3,y,.94),(.1,.65,.95),'493B2E')
 for yy in (y-.27,y+.27):
  for xx in (x-.25,x+.25):cube('chair leg',(xx,yy,.24),(.07,.07,.48),'493B2E')
chair(1.3,-.45); chair(1.3,.55)
for y in (-1.6,1.8):chair(1.3,y)
for y in (-1.8,1.7):
 cube('closed ledger',(.48,y,1.055),(.4,.53,.065),'4C3D2B'); cube('parchment edge',(.47,y,1.095),(.36,.48,.012),'B7AD8A')
# Scroll expands across X; its drawing is retained geometric charcoal linework.
scroll=empty('unrolling parchment',(-.69,-.475,1.032)); cube('parchment sheet',(.69,0,0),(1.38,.95,.012),'DBCA9E',scroll)
roll=rod('scroll moving roll',(-.69,0,0),(.69,0,0),.057,'D8C498')
# Detailed production drawing, UV mapped to the unfolding sheet and packed in the blend.
mesh=bpy.data.meshes.new('bombard drawing surface')
mesh.from_pydata([(0,-.475,.018),(1.38,-.475,.018),(1.38,.475,.018),(0,.475,.018)],[],[(0,1,2,3)]); mesh.update()
surface=bpy.data.objects.new('detailed bombard manuscript',mesh); s.collection.objects.link(surface); surface.parent=scroll
uv=mesh.uv_layers.new(name='UVMap')
for i,co in enumerate(((0,0),(1,0),(1,1),(0,1))):uv.data[i].uv=co
mat=bpy.data.materials.new('bombard parchment artwork'); mat.use_nodes=True
tex=mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(R/'bombard-drawing.png')); tex.image.pack(); mat.node_tree.nodes.active=tex
mat.node_tree.links.new(tex.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color']); surface.data.materials.append(mat)
for child in scroll.children:child.location.y+=.475
# Articulated, costume-coded human proxies. Local forward is +Y.
actors={}
for name,v in c['characters'].items():
 seated=name!='urban'; root=empty(name,v['position']); root.rotation_euler.z=math.radians(v['yaw']); hip=.55 if seated else .88; torso=empty(name+' torso',(0,0,hip),root)
 coat={'urban':'665340','loukas':'302F2C','emperor':'353139'}[name]; skin='B69A7C'; headz=.74 if seated else .68
 ball(name+' coat',(0,0,.23),(.25,.16,.38),coat,torso)
 if name=='urban':cube('leather apron',(0,.148,.08),(.37,.035,.6),'4B3B2C',torso)
 if name=='emperor':cube('gold imperial trim',(0,.157,.22),(.1,.026,.57),'A98D4D',torso)
 if name=='loukas':cube('brocade front',(0,.153,.24),(.13,.023,.52),'B19F79',torso)
 head=empty(name+' head',(0,0,headz),torso); ball(name+' face',(0,0,0),(.133,.126,.18),skin,head)
 ball(name+' nose',(0,.135,-.01),(.029,.05,.041),skin,head)
 for side in (-1,1):
  ball(name+' ear',(side*.132,0,-.015),(.028,.024,.047),skin,head)
  ball(name+' eye white',(side*.05,.114,.036),(.028,.013,.015),'D4CBB8',head); ball(name+' pupil',(side*.05,.127,.036),(.011,.008,.01),'302C25',head)
  brow=cube(name+' brow',(side*.05,.126,.065),(.07,.015,.014),'594D3D',head)
 ball(name+' mouth',(0,.117,-.082),(.038,.012,.008),'584337',head)
 if name=='loukas':
  ball('grey goatee',(0,.09,-.133),(.038,.038,.054),'908A79',head)
  for side in (-1,1):ball('grey moustache',(side*.023,.123,-.064),(.035,.019,.016),'908A79',head)
 else:
  ball(name+' beard',(0,.04,-.105),(.11,.099,.082),'3F382E',head); ball(name+' hair',(0,-.022,.112),(.137,.12,.083),'3B342A',head)
 if name=='emperor':
  rod('imperial crown',(0,0,.135),(0,0,.215),.145,'B19550',head)
  for j in range(8):ball('crown jewel',(.148*math.cos(j*math.tau/8),.148*math.sin(j*math.tau/8),.175),(.017,.017,.017),'6A3530',head)
 for side in (-1,1):
  if seated:
   rod(name+' thigh',(side*.13,0,.51),(side*.13,.4,.46),.10,coat,root); rod(name+' shin',(side*.13,.4,.46),(side*.13,.43,.09),.075,coat,root); ball(name+' shoe',(side*.13,.49,.07),(.10,.17,.07),'39322A',root)
  else:
   rod(name+' leg',(side*.13,0,.86),(side*.15,.02,.12),.09,coat,root); ball(name+' boot',(side*.15,.07,.09),(.11,.17,.09),'39322A',root)
 arms=[]
 for side in (-1,1):
  arms.append([rod(name+' upper arm',(0,0,0),(0,0,.2),.072,'713D30' if name=='loukas' else coat),rod(name+' forearm',(0,0,0),(0,0,.2),.063,'713D30' if name=='loukas' else coat),ball(name+' hand',(0,0,0),(.061,.042,.035),skin)])
 actors[name]=(root,torso,head,arms)
pointing_finger=rod('Urban pointing index',(0,0,0),(.1,0,0),.014,'B69A7C')
def ramp(t,a,b):
 v=max(0,min(1,(t-a)/(b-a))); return v*v*(3-2*v)
def key(o,f):
 for path in ('location','rotation_euler','scale'):o.keyframe_insert(data_path=path,frame=f)
def pose_rod(o,start,end,f):
 d=Vector(end)-Vector(start); o.location=(Vector(start)+Vector(end))/2; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.scale.z=d.length; key(o,f)
# Bake motion to native keyframes so the .blend renders without Python handlers.
dialogue={d['turn']:d for d in c['dialogue']}
u1,u2,l=dialogue[2],dialogue[5],dialogue[3]
for f in range(1,s.frame_end+1,2):
 t=(f-1)/c['fps']; ac=c['action']; lean=ramp(t,ac['leanStart'],ac['leanEnd']); whisper=ramp(t,ac['whisperStart'],ac['whisperArrive']); unroll=ramp(t,ac['unrollStart'],ac['unrollEnd'])
 scroll.scale.y=.07+.93*unroll; key(scroll,f); roll.location=(0,-.475+.95*scroll.scale.y,1.088); key(roll,f)
 for name,(root,torso,head,arms) in actors.items():
  root.location=c['characters'][name]['position']; root.rotation_euler.z=math.radians(c['characters'][name]['yaw'])
  torso.rotation_euler=(0,0,0); head.rotation_euler=(0,0,0)
  if name=='urban':
   torso.rotation_euler.x=-.3*lean; head.rotation_euler.x=.13*lean
   if u1['startSeconds']<t<u1['endSeconds'] or u2['startSeconds']<t<u2['endSeconds']: head.rotation_euler.x+=.018*math.sin(t*4)
  if name=='loukas':
   root.location.y+=.12*whisper; torso.location.z=.55+.16*whisper; torso.rotation_euler.y=.85*whisper; head.rotation_euler.z=-1.4*whisper
   if l['startSeconds']<t<l['endSeconds']:head.rotation_euler.x=.025*math.sin(t*4)
  if name=='emperor':
   head.rotation_euler.z=.18*whisper
   if dialogue[4]['startSeconds']<t<dialogue[4]['endSeconds']:head.rotation_euler.x=.018*math.sin(t*3)
  key(root,f); key(torso,f); key(head,f); bpy.context.view_layer.update()
  for j,side in enumerate((-1,1)):
   shoulder=torso.matrix_world@Vector((side*.245,0,.43)); elbow=torso.matrix_world@Vector((side*.30,.12,.19))
   if name=='urban':
    initial=Vector((-.65,-.43 if j==0 else -.475+.95*(.07+.93*unroll),1.12)); dest=Vector((-.65,-.39,1.065)) if j==0 else Vector((-.12,.16,1.074))
    hand=initial.lerp(dest,lean)
    if j==1 and u2['startSeconds']<t<u2['endSeconds']:hand.z+=.055*(.5+.5*math.sin(t*2.7))
   else:
    hand=Vector((.76,root.location.y+side*.23,1.065))
    if name=='loukas' and j==1:hand=hand.lerp(Vector((1.12,.34,1.33)),whisper)
    if name=='loukas' and l['startSeconds']<t<l['endSeconds'] and j==0:hand.z+=.08*math.sin((t-l['startSeconds'])*math.pi/(l['endSeconds']-l['startSeconds']))
   elbow=(shoulder+hand)/2+Vector((-.06 if name=='urban' else .1,side*.05,-.10))
   pose_rod(arms[j][0],shoulder,elbow,f); pose_rod(arms[j][1],elbow,hand,f); arms[j][2].location=hand; key(arms[j][2],f)
   if name=='urban' and j==1:pose_rod(pointing_finger,hand,hand+Vector((.115,0,-.025)),f)
# camera markers produce hard cuts, exact to zero-based playback segment starts.
cams={}
for name,v in c['cameras'].items():
 data=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,data); s.collection.objects.link(o); o.location=v['position']; o.rotation_euler=(Vector(v['target'])-o.location).to_track_quat('-Z','Y').to_euler(); data.lens=v['lens']; data.clip_start=.03; cams[name]=o
for cut in c['cuts']:
 m=s.timeline_markers.new(cut['id'],frame=1+round(cut['seconds']*c['fps'])); m.camera=cams[cut['camera']]
# Texture display for the manuscript, solid palette for all other geometry.
sh.color_type='TEXTURE'
palette={}
for ob in s.objects:
 if ob.type in {'MESH','CURVE'} and not ob.data.materials:
  col=tuple(ob.color)
  if col not in palette:
   m=bpy.data.materials.new('previs palette'); m.diffuse_color=col;palette[col]=m
  ob.data.materials.append(palette[col])
s.camera=cams['master']; s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'council.blend'))
if a.frames:
 for f in map(int,a.frames.split(',')):
  s.frame_set(f); s.render.filepath=str(frames/f'{f:04}.png'); bpy.ops.render.render(write_still=True)
