<!-- Copied from claude-runs/animations/out/README.md (13 Nov 2026). Scripts are in
     figures/scripts/animations; data, frames and website formats stay in
     claude-runs/animations. -->
# FSI animations and field images (13 Nov 2026)

For the solver paper's supplementary material, the solids4foam website and slides.
Every animation has: `NAME.mp4` (H.264, yuv420p, 30 fps, crf 18; slides and
supplementary material), `NAME.webm` (VP9; website), `NAME.gif` (looping, <= 5 MB;
website) and `NAME-poster.png` (one frame). Rendering scripts: `../scripts/`;
encoder: `../scripts/encode.sh`. Same style as the paper's field images.

## ringAddedMass
Elastic ring vibrating in its n = 2 mode in a fluid-filled rigid annulus (strong
added-mass level, mu = 10.08; quasi-monolithic coupling, factor-2 mesh, 100 steps per
period, quarter model mirrored): fluid kinematic pressure and the ring coloured by its
displacement magnitude over two periods, with the deformation of both regions magnified
250 times.
- Run: local rerun of mafinal4-ram-qm-strong-m2-n100 (`../data/ring_anim`), first two
  periods (t = 0-16.35 s) written every 4 steps; local build ffffeb525 + #697 fix.
- MP4 loops the two periods three times (10 s).

## tube3d-pressure-pulse
Pressure pulse travelling along a three-dimensional elastic tube (quasi-monolithic
coupling, tutorial mesh): fluid kinematic pressure on the longitudinal symmetry plane of
the half tube and the wall coloured by its displacement magnitude, displaced and
magnified ten times, t = 0-8 ms.
- Run: local rerun of the 3dTube tutorial case (`../data/tube_anim`) written every
  0.1 ms; local build ffffeb525 + #697 fix. Transient, not looped.

## womersleyTube-pulse
Pulsatile flow in a compliant tube over one period (axisymmetric, mirrored about the
axis; quasi-monolithic coupling, factor-2 mesh, 200 steps per period): axial fluid
velocity with velocity profiles at five stations, showing the off-axis velocity maximum
and the flow reversal, and the wall coloured by the magnitude of its radial displacement
(true scale).
- Run: local rerun of mafinal4-wom-qm-m2-n200 (`../data/wom_anim`) to t = 300 s
  (six periods), last period t = 250-300 s written every 5 steps; local build ffffeb525 +
  #697 fix. Seamless loop (40 frames per period), MP4 three periods (10 s).

## collapsibleChannel-collapse
Collapse of a flexible channel wall under an external pressure (quasi-monolithic
coupling, fluid level 2, 320 x 8 wall, rho_s/rho_f = 1, dt = 1/160 s, true scale):
(top) fluid kinematic pressure, (bottom) fluid speed with streamlines, with the wall
coloured by its displacement magnitude and its undeformed outline, t = 0-0.75 s.
- Run: local rerun of the order-1 320 x 8 case of the order study (`../data/coll_o1_320x8`,
  set-up coll-ho697/mk_coll.sh), written every 0.0125 s; local build ffffeb525 + #697 fix.
- Paper field image: `collapsibleChannel-field.png` (2400 px wide), same layout at the
  first trough, t = 0.4625 s.

## HronTurek3-flag
Hron-Turek FSI3: the elastic flag behind the cylinder over one period of its
oscillation (quasi-monolithic coupling, level-2 meshes, t = 5.892-6.075 s): fluid
vorticity and the flag coloured by its displacement magnitude, with its undeformed
outline.
- Run: MeluXina /project/home/p201136/philip-anim/fsi3_qm2, restart of fsi3g qm_2
  (build qm-a421, a421f063d, as the paper's FSI3 runs) from t = 5.888 to 6.1 s, VTK every
  35 steps (0.00495 s); 2.48 node-hours (job 5455829).
- Seamless loop: frames 0-36 (one period, 37 frames; the 38th frame matches the first to
  0.6% of the tip amplitude); MP4 four periods.

## foilInWind-flag
Three-dimensional flexible flag behind a block in a uniform air flow (quasi-monolithic
coupling, t = 0-2.5 s): streamlines seeded upstream of the block coloured by air speed,
and the flag coloured by its displacement magnitude with its deformation magnified 50
times. The wake becomes unsteady and the flag starts to flutter and twist from
t ~ 1 s; its displacement reaches about 0.14 mm by t = 2.5 s.
- Run: MeluXina /project/home/p201136/philip-anim/foil_qm, rerun of rf-foil-qm-dt0.0025
  (128 ranks, dt = 0.0025 s) to t = 2.5 s with merged VTK every 10 steps (0.025 s);
  build build-gm697 (#679 + #690 + #697 fix); 2.56 node-hours (job 5455835).
- Website version is an animated WebP (the GIF exceeded 5 MB).
- Paper field image: `foilInWind-field.png` (2400 px), t = 2.45 s.
