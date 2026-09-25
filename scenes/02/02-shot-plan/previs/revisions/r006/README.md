# Scene 02 hard-cut previs

Edit `scene.json` for camera, blocking, timing, duration and resolution; edit `build_previs.py` for geometry/performance. +Y faces the icons; master screen-left is -X. `description.md` and `playback.json` must be kept aligned with any timing changes. Native camera timeline markers make the cuts; native keyframes retain motion in the blend without handlers.

From this source directory, with an absolute project path substituted for PROJECT and a fresh ATTEMPT directory:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python-exit-code 1 --python build_previs.py -- --out PROJECT/tmp/operations/previs/council/candidate --frames-dir PROJECT/tmp/media/previs/shot_plan_vhrjk7x7/ATTEMPT/frames --frames 1,133,241,337,433,816
/Applications/Blender.app/Contents/MacOS/Blender --background PROJECT/tmp/operations/previs/council/candidate/council.blend --python-exit-code 1 -o PROJECT/tmp/media/previs/shot_plan_vhrjk7x7/ATTEMPT/frames/#### -s 1 -e 816 -a
python3 finish.py --frames-dir PROJECT/tmp/media/previs/shot_plan_vhrjk7x7/ATTEMPT/frames --output PROJECT/tmp/media/previs/shot_plan_vhrjk7x7/ATTEMPT/previs.mp4
```

Build-only: omit `--frames`. Render one frame: load the blend and use `-f N`. Resume a matching interrupted render with an explicit missing `-s START -e END -a` range. Rebuild and use a fresh frame directory whenever inputs change. The encoder refuses to overwrite movies or partial encodes. The builder writes only candidate working blends; do not aim it at registered revisions. Blender 5.2.1, Workbench studio display, 960×540, 24fps. No audio, text overlays, captions or timecodes.

Visual sources inspected: chamber spatial sheet `locations/imperial-council-chamber/imperial-council-chamber-s-sheet-gb34.png`, Urban `cast/urban/urban-character-sheet-2.png`, Constantine `cast/constantine-xi-palaiologos/constantine-xi-main-imperial-cha.png`, and Loukas `cast/loukas-notaras/codex-character-sheet-a.png`. No external textures or source dependencies; all geometry and illustration strokes are procedural.
