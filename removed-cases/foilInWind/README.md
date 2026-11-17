# Three-dimensional flag (foilInWind), removed from the paper

Removed from the solver paper on 17 Nov 2026 (Philip's review: a new case in the Limitations
section was not needed). Figures, the geometry SVG, the animation (website and slides only)
and their scripts are kept here. Paths in the scripts still refer to the old locations.
`../sectionLimitations.tex` is the removed Limitations section (Section 7 of the 16 Nov draft).

## Animation (foilInWind-flag)
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
