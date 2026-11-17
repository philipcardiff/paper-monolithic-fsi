# Turek–Hron FSI3: Gmsh fluid mesh family (levels 1–3)

The three quadrilateral-dominant fluid meshes of the solver paper's FSI3 study (Section 6.1),
and the scripts that built the solver paper's FSI3 cases on them.

| Level | Fluid cells | Hexes + prisms | `plate` patch faces | Solid mesh used (blocks 1+2 x across) | Δt coupled (rigid 0–2 s) |
|---|---|---|---|---|---|
| 1 | 96 712 | 96 704 + 8 | 910 | 62+368 x 24 | 2e-4 (5e-4) |
| 2 | 194 183 | 194 175 + 8 | 1 286 | 88+520 x 34 | 1.414e-4 (3.54e-4) |
| 3 | 387 219 | 387 217 + 2 | 1 818 | 124+736 x 48 | 1e-4 (2.5e-4) |

The solid mesh is the tutorial plate `blockMeshDict` (`system/solid/blockMeshDict.monolithic`
at a421f063d) with uniform cells of about the fluid spacing along the flag (the uniform middle part of each long
side of the flag has 430, 608 and 860 fluid faces); `mk_fsi3_case.py`
sets the counts.

Level L scales the size field by s = 2^(-(L-1)/2). Patch names are those of the solids4foam
`TurekHron2006` tutorial: `plate`, `outlet`, `inlet`, `cylinder`, `bottom`, `top`,
`frontAndBackPlanes` (empty). All other patches are written as type `patch`.

## Tools

- Gmsh 4.11.1 (macOS build). Other Gmsh versions may give slightly different meshes, because
  the unstructured region uses Blossom recombination.
- Python 3 (standard library only).
- OpenFOAM v2512 (`gmshToFoam`, `checkMesh`).

## Generating level L

```bash
export GMSH=/path/to/gmsh          # default: /Applications/Gmsh.app/Contents/MacOS/gmsh
python3 ht_mesh_gmsh2.py --level L --bl-y1 3e-4 --tip-y1 3e-4 --out tL   # writes tL/mesh.geo, mesh2d.msh
python3 extrude_msh.py tL/mesh2d.msh tL/mesh.msh                    # one cell in z, dz = 0.015 m
source <OpenFOAM v2512>/etc/bashrc
./mk_foam.sh tL                                                     # constant/polyMesh + checkMesh
```

`--bl-y1 3e-4 --tip-y1 3e-4` are required. `--bl-y1` is the level-1 first-cell height of the
layers around the cylinder and flag; it scales with s, giving 0.300, 0.212 and 0.150 mm on
levels 1–3. `--tip-y1` selects the tip-only variant and caps the first cell of the flag-tip
corner blocks: 0.300, 0.300 and 0.286 mm. The `mesh_family_levelL.txt` files record every
parameter.

## Checks (regenerated on 17 Nov 2026, Mac Studio, Gmsh 4.11.1, OpenFOAM v2512)

The regenerated `constant/polyMesh/points` are byte-identical to the meshes the paper used
(MeluXina `p201136/philip-ht/fsi3g/meshes/tL`):

| Level | md5 of `constant/polyMesh/points` | checkMesh max non-orthogonality |
|---|---|---|
| 1 | 13890c5f7c5b4ca65093bcfd17dedc6d | 28.5 |
| 2 | a2eac580e785500f8f0e9410155b6a7b | 38.8 |
| 3 | 8a74309d848141974fec7801fb11a123 | 44.6 |

## Building the solver-paper cases (reference only)

`mk_fsi3_case.py` and `run_fsi3.sh` are the exact scripts used on MeluXina (md5-checked). They
start from the `TurekHron2006` tutorial at solids4foam `a421f063d` (branch
`feature-petsc-snes-quasi-monolithic`) and need its `*.monolithic` variants (also for the IQN-ILS
case, which takes the solid mesh and the fluid-mesh-motion fields from them); the `development`
tutorial has no `*.monolithic` files:

```bash
# next to the scripts: tut/ = TurekHron2006 tutorial at a421f063d;
# meshes in $FSI3_GMSH/tL/constant/polyMesh (default ~/claude-runs/agent-b-gmsh)
export FSI3_GMSH=/path/to/meshes
python3 mk_fsi3_case.py --level L --coupling iqn --ranks N --out runs/iqn_L   # or --coupling qm
ENV_SH=/path/to/openfoam-and-solids4foam-env.sh ./run_fsi3.sh runs/iqn_L     # 0-2 s rigid, then coupled to 6 s
```

The solid and interface settings, the IQN-ILS settings and the fluid-mesh motion they write
are listed in the coordination-board message of 17 Nov 2026 (paper-monolithic-fsi#13).

## Fluid-mesh motion on these meshes

In trials that replayed the FSI3 flag motion from t = 25 s of a reference run
(`moveDynamicMesh`), the OpenFOAM `velocityLaplacian` and `displacementLaplacian` solvers, with
quadratic inverse-volume or quadratic/linear inverse-distance diffusivities, folded cells
(non-orthogonality 180°) between t = 25.7 and 26.0 s. The solids4foam solid-model motion
solver (`solids4foamSolidModel` with the total displacement from the initial points,
`diffusionElastic` with mu = 1 and K = 3, linear `inverseDistance 2(plate cylinder)`) kept the
maximum non-orthogonality at 39–45° (the undeformed meshes have 28–45°) up to t = 30.2 s on
levels 2–4. All solver-paper FSI3 runs, QM and IQN-ILS, use this solver.
