# Harbor walk — director-controlled Blender blocking

## Current take: v003

The current `scene.json` produces **take 3**, saved in `renders/v003/`. Takes 1 and 2 remain available.

- Mara approaches the blue soldier at **6–8 seconds**, stays to converse at **8–11 seconds**, and slowly turns toward Urban at **11–13 seconds**.
- Urban continues forward and settles at **8.8 seconds**, 3.25 metres beyond his previous stopping point and 1.3 metres farther along the quay than Mara. He turns back toward her while she finishes the conversation.
- The blue soldier pauses his repair work and faces Mara. Small arm gestures and head nods indicate their conversation; no additional spoken lines have been invented or synthesized.
- The centered following camera retains the take 2 height, distance and lens.
- Duration is **17 seconds / 408 frames**. The original third and fourth dialogue captions now run at 11.15–13.15 and 13.3–16.8 seconds, leaving the three-second side conversation clear.
- A reusable `talk` action now works for the main and supporting characters. It takes the same actor, target, start/end and fade controls as a turn, adding subtle gestures and suspending a supporting character's repair loop. Existing configurations still reproduce their original lead motion and camera.
- Watch `renders/v003/harbor_review.mp4`, use `renders/v003/harbor_clean.mp4` for guidance, or open `renders/v003/harbor_previs.blend`. Motion checks are in `renders/v003/motion_validation.json`.

## Previous take: v002

Take 2 is in `renders/v002/`, including its original configuration snapshot. Take 1 remains in `renders/v001/`.

- Camera tracks the live midpoint between Mara and Urban, 9.08 metres behind and 3.4 metres above the quay, with the same 35 mm lens. This centers the crane-style view and preserves approximately the original following distance.
- Urban eases to a stop at **6.0 seconds** and stays in place.
- Mara approaches `soldier_blue` from **6.0 to 8.0 seconds**, coming to rest about one metre from him. The supporting cast and repair props retain their previous locations.
- Mara turns toward Urban from **8.0 to 8.85 seconds**. Urban turns toward her shortly afterward, and they hold the dialogue positions through the end.
- Duration remains 15 seconds; dialogue wording and caption times remain the same. The review's third-beat caption now reads “Mara turns to Urban” to match the revised blocking.
- The motion builder and evaluator are unchanged. Configuration controls the camera, route, independent character offsets, and turn cues. The review encoder now derives the take label from its output folder.
- Watch `renders/v002/harbor_review.mp4`; use `renders/v002/harbor_clean.mp4` for guidance; open `renders/v002/harbor_previs.blend` for Blender review. Request-specific motion checks are saved in `renders/v002/motion_validation.json`.

The following first-pass notes describe v001 and the shared control system.

First pass: **15 seconds, 24 fps, 360 frames, 960 × 540**, rendered with the installed Blender 5.2.1 CLI. All figures and props are rectangular proxies. This is a standalone experiment in the requested scene folder, not a registered Renku Shot Plan.

## Watch and open

- `renders/v001/harbor_review.mp4`: picture plus time/frame counter, color legend, beat labels, and the exact first four dialogue turns as captions. Silent; dialogue timing is provisional.
- `renders/v001/harbor_clean.mp4`: unannotated 16:9 video for subsequent AI video guidance. Same camera and animation as the review copy.
- `renders/v001/harbor_previs.blend`: scene with ordinary baked keyframes. Open in Blender and play the timeline. No script execution or add-on is required for playback.
- `renders/v001/contact_sheet.jpg`: six moments for quick review.
- `renders/v001/dialogue.srt`: separate dialogue subtitles.

## The first pass

The saved source is Scene **03**, **The Harbor Argument**, scene ID `scene_fzf8844n`, active beat revision `scene_beat_sheet_cpp7a9eh`. Read-only snapshots are in `source/`.

The pair travel about ten metres. Mara observes net menders, then the shrine, then the blue soldier and shields. Urban keeps about half a pace ahead and briefly notices people while remaining less engaged. The camera follows from behind on the landward side, retaining the water and repair work in the composition.

The saved third beat explicitly stops Mara beside the shield rack. This pass preserves that stop: the walk slows around 9.8 seconds, Mara settles by 10.5, Urban takes another half step and turns back from 10.9. They hold the final exchange through 15 seconds. The specific route, colors, encounter timing and camera are provisional blocking choices, not changes to the saved beats.

| Time | Dialogue / action |
|---|---|
| 0–2 s | Establish repair activity and the pair walking |
| 2–4 s | Mara: “They are afraid of your gun.” |
| 4.3–7.6 s | Urban: “They are afraid of the man who can afford it.” |
| 8.5–10.6 s | Mara: “Then do not go to him.” |
| 11.2–14.8 s | Urban: “A design unfired is a corpse with clean hands.” |

## Direct by stable names

| ID | Proxy | Starting role / placement |
|---|---|---|
| `mara` | Coral | Walker's left |
| `urban` | Ochre | Walker's right, half a pace ahead |
| `refugee_teal` | Teal | Net mender, landward side |
| `refugee_green` | Green | Second refugee at the net table |
| `monk_violet` | Violet | Shrine, waterside |
| `civilian_lilac` | Lilac | Civilian beside the shrine |
| `soldier_blue` | Blue | Shield repair worker near the stopping point |
| `soldier_slate` | Slate blue | Second soldier |

Important props include `net_table`, `net_patch`, `shrine`, `shrine_flame`, `repair_bench`, `shield_rack`, `shield_a`–`shield_c`, `boat_01`, `boat_02`, and `urban.cannon_drawing`. The white chip on each head indicates its front, not facial detail.

## Editing model

**`scene.json` holds the directing choices. The Python scripts stay unchanged.** Rebuilding re-evaluates this configuration and bakes a fresh `.blend` plus a new render. Changes made manually to a generated `.blend` are not imported back into the configuration.

- All cue times are **seconds**. Frame 1 is time 0; frame 241 is time 10.
- Coordinates are **metres**, Z up. The route runs along world +Y; +X is the walker's right, toward the water. Right/left mean walking direction, not an arbitrary camera's screen direction.
- `walk.path` points are `[time, x, y]`. Shape-preserving interpolation provides continuous pacing and holds without overshooting. Equal positions at successive times produce a stop.
- `characters.<id>.lateral` sets separation; `ahead` sets forward lead. Either accepts a number or `[[time,value], ...]` for changes during the take.
- `camera.base.offset` is `[right, forward, up]` relative to the walking axis and pair midpoint. Negative forward is behind them. Lens values are millimetres.
- Shoulder cue offsets are relative to the subject's head height and body orientation. A camera cue fades in and out **inside** its start/end interval. Overlapping cues apply in list order, later cues blending over earlier ones.
- Actions are `look`, `turn`, `lean`, and `talk`. A `peak` gives an exact maximum time. A lean can also approach its target by a specified distance. Later actions take priority as they blend in. Remove or revise competing cues for a new interpretation. `look`, `turn`, and `talk` also accept supporting figures as actors; lean/approach remains a lead-character control.
- Movement drives the simple leg/arm swing; the gait settles during a hold. This is a kinematic blocking rig, without physical simulation or foot IK.
- Supporting figures and props have editable positions in the same config. Their repair gestures loop in place. Their body yaw values use degrees; +90 faces world −X.
- Every render contains its own `config.snapshot.json`, frame-level `motion.json`, and embedded Blender configuration. Editing commands back up replaced configs in `history/`. `run.py` requires a new empty output directory to preserve takes.

## Example directing commands

Run these from this `harbor-previs` folder. Each example saves a separate variant and leaves the main take alone.

```bash
# “Mara should be to the right of Urban instead.”
python3 direct.py --output examples/mara-right.json swap-sides mara urban

# “Over Mara's shoulder between 3 and 5 seconds.”
python3 direct.py --output examples/mara-shoulder.json camera \
  --start 3 --end 5 --subject mara --target urban

# “Mara should lean toward the blue guy at the tenth second.”
python3 direct.py --output examples/mara-lean.json action \
  --kind lean --actor mara --target soldier_blue \
  --start 9 --peak 10 --end 11 --degrees 28 --approach 0.65

# “Slow the whole scene to 18 seconds.” All cues and dialogue scale together.
python3 direct.py --output examples/slower-18s.json retime 18

# “Move the following camera lower and closer.” JSON values follow a dotted key.
python3 direct.py set camera.base.offset '[-2.5,-6.5,2.6]'

# “Let Mara draw level, then drop half a pace behind.”
python3 direct.py set characters.mara.ahead '[[0,0],[5,0.45],[9,-0.5],[15,-0.5]]'

# Build and render any chosen configuration into a NEW take folder.
python3 run.py --config examples/mara-right.json --out renders/v002

# Or build only, for immediate Blender review before rendering.
python3 run.py --config scene.json --out renders/v003 --build-only
```

To combine directions, use `--config examples/mara-right.json` as the input to another command. To update a cue in place, reuse its `--id`. Remove it with `python3 direct.py remove director_camera` or `remove director_action`.

Native Blender invocation, if preferred:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python build_previs.py -- --config scene.json --out renders/v004 --render
python3 finish.py renders/v004
```

`--frames 1,97,241` renders selected preview frames instead of a full animation. `finish.py` requires Python Pillow and FFmpeg. The verified Pillow-capable interpreter on this machine is `/Users/keremk/.pyenv/versions/3.10.10/bin/python3`; use that interpreter for `run.py` or `finish.py` if the shell selects a different Python environment. In the Codex sandbox this Blender installation crashes during Metal initialization; the successful renders used the same CLI outside that sandbox.

## Verification and limits

- `check_motion.py` verifies baseline lead separation, supporting-figure clearance, the settled stop, finite continuous camera positions, side swapping, timed shoulder camera selection, and a lean peak with return to baseline.
- Clean video checked with FFprobe: exactly **360 frames at 24 fps, 15.000 seconds**. The review video includes the same 360 rendered frames and adds bars outside the picture.
- Inspected representative baseline frames plus separate shoulder and lean previews under `qa/`. The three example directions are available as configuration variants; they are not inserted into the first-pass video.
- Timing and blocking are art-directed, not a collision-solving crowd system. After large layout or camera changes, inspect a few frames before a full render. The initial QA checks do not guarantee every future configuration is collision-free.
- No speech synthesis or high-fidelity AI generation is part of this previs pass. Use `harbor_clean.mp4` as the motion/composition guide for that later step.
