# Mesh layers of the geometry figures (F-geo)

Mesh layers for the case geometry figures (`paper-data/submission_plan.md`,
§2 F-geo). Each mesh is the case's coarsest mesh: the solids4foam tutorial
mesh, which is level 1 (L1) of the case's verification study
(foilInWind has none). The meshes were made
with the tutorials' own mesh steps (from each `Allrun`), with OpenFOAM v2512,
from solids4foam `v2.4-1103-g85b0c1de6`
(`tutorials/fluidSolidInteraction/<case>`).

Every case first runs

    blockMesh -region solid
    blockMesh -region fluid

in a copy of the tutorial (all polyMesh files are ASCII, except 3dTube,
whose binary mesh ParaView reads directly). The 2-D layers were then drawn
with

    figures/scripts/mesh_layer.py figures/mesh/<case>-mesh.pdf \
        --region fluid=<case>/constant/fluid/polyMesh \
        --region solid=<case>/constant/solid/polyMesh [options]

and the 3-D layers with `figures/scripts/mesh_render3d.py` (ParaView 6.1.1
`pvpython`; PNG with a transparent background, the camera recorded in the
JSON file). Each JSON file next to an image gives the plotted bounding box
(2-D) or the camera (3-D), in the mesh's own coordinates (no scaling).

| File | Case | Mesh | Extra steps / options | Fluid cells | Solid cells |
| --- | --- | --- | --- | ---: | ---: |
| `cavityFlexibleBottom-mesh.pdf` | cavityFlexibleBottom | tutorial (L1) | – | 1688 | 160 |
| `TurekHron2006-conformal-mesh.pdf` | TurekHron2006 FSI3 | conformal (`./Allrun monolithic` variant) | `system/{fluid,solid}/blockMeshDict.monolithic` copied over `blockMeshDict` (as `selectCaseVariant . monolithic` does) | 1859 | 150 |
| `TurekHron2006-mesh.pdf` | TurekHron2006 FSI3 | tutorial default, non-conformal (partitioned runs) | – | 5336 | 630 |
| `blobInTreacle-mesh.pdf` | blobInTreacle | tutorial (L1) | – | 480 | 120 |
| `ringAddedMass-mesh.pdf` | ringAddedMass | tutorial (L1), quarter ring | `--width-cm 8` (single column) | 576 | 192 |
| `womersleyTube-mesh.pdf` | womersleyTube | tutorial (L1), axisymmetric wedge | axial-radial plane, `--axes x,y` (default) | 1280 | 512 |
| `collapsibleChannel-mesh.pdf` | collapsibleChannel | tutorial (L1) | – | 3200 | 640 |
| `3dTube-mesh.png` | 3dTube | tutorial (L1), quarter tube | `--fluid inlet,symmetry-x,symmetry-y --solid inlet,symmetry-x,symmetry-y,outer-wall --view=-1,-0.35,-0.5 --up=0,1,0 --width-px 3000 --aspect 0.3` | 16000 | 6400 |
| `foilInWind-mesh.png` | foilInWind (3-D) | tutorial | `setSet -batch setSet.batch -region fluid`, `refineMesh -region fluid -overwrite` (from `Allrun`); render `--fluid walls,inlet,outlet,block --solid interface,fixed --cull-front fluid --view=-0.6,0.5,1 --up=0,1,0 --width-px 3000 --aspect 0.6` | 176248 | 4608 |

Notes:

- Only TurekHron2006 has a mesh variant: the `monolithic` variant replaces
  both blockMeshDicts with a coarser mesh whose `plate` interface is
  conformal (132 of 132 interface points coincide). The default tutorial
  mesh is non-conformal (10 of 434 solid and 170 fluid `plate` points
  coincide). The other cases use one mesh for all couplings, and all their
  interfaces are conformal.
- womersleyTube (15 × 1.1) and collapsibleChannel (25 × 1.05) are long and
  thin: at full text width the whole mesh is about 1.1 cm and 0.6 cm high.
  The annotation layer may need to break or crop them.
- foilInWind is three-dimensional (no `empty` patch), so it is a ParaView
  render, not a `mesh_layer.py` drawing. The fluid side walls are drawn with
  their front faces culled, so only the far walls show behind the flag.
- `mesh_layer.py` change: for a `wedge` patch all faces are kept. Its
  "lower side in the out-of-plane coordinate" filter is meant for the two
  sides of an `empty` patch; on a tilted wedge patch the out-of-plane
  coordinate grows with the radius, so the filter dropped half the cells of
  the womersleyTube mesh.
