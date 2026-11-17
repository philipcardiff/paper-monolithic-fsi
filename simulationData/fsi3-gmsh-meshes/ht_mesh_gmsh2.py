#!/usr/bin/env python3
"""Quad gmsh fluid mesh family for Turek-Hron FSI3, version 2 (agent B).

Changes from ht_mesh_gmsh.py, after the Astra review (astra_1_answer.txt):
- flag-cylinder junction: one non-collapsed corner block J-Q-K-S spanning the
  101.5 deg fluid wedge, with K the point where the radial line from the
  cylinder (Q-K) and the vertical line from the flag (S-K) meet at the collar
  thickness T, so both layer blocks end orthogonally (no transition blocks);
  both wall edges of the corner block are graded from J with first cell y1;
- flag tip corners: a non-collapsed corner block C-P1-X-P2 at each corner, the
  flag and end-face tangential spacing graded down to y1 at the corner with
  the layer distribution (no fans);
- structured wall strips on the channel walls (first cell w_y1 s);
- every transfinite count even, Blossom (RecombinationAlgorithm 1; the mirrored count pairs keep the boundary even):
  no triangles;
- background size function scaled uniformly: h = s (h0 + grow d), box
  transition width fixed.

Geometry and patch names (in the tutorial order) as the tutorial fluid
blockMeshDict. Level L: s = 2^(-(L-1)/2). The 2-D mesh is extruded one cell by
extrude_msh.py.

    python3 ht_mesh_gmsh2.py --level 1 --out case_dir
"""
import argparse
import math
import os
import subprocess
from pathlib import Path

# Gmsh 4.11.1 was used; override the executable with the GMSH environment variable
GMSH = os.environ.get("GMSH", "/Applications/Gmsh.app/Contents/MacOS/gmsh")

# metres, level 1
DEFAULTS = dict(
    h_body=0.8e-3,    # tangential size on the cylinder and flag (uniform parts)
    grow=0.06,        # size growth per unit distance (scaled by s)
    h_band=3.5e-3,    # cap in the band y 0.10-0.30 m, x < x_band
    x_band=1.5,
    h_max=8.0e-3,     # cap elsewhere
    bl_y1=0.10e-3,    # first cell on cylinder and flag
    bl_ratio=1.22,
    bl_thick=4.0e-3,  # collar thickness T
    w_y1=0.4e-3,      # first cell on the channel walls
    w_ratio=1.22,
    w_thick=8.0e-3,   # wall strip thickness
    h_wall=2.5e-3,    # tangential size along the channel walls
    tip_y1=0.0,       # > 0: tip-only variant (31 Oct): flag and end face uniform
                      # tangentially (no grading to the corner) and the tip corner
                      # block first cell fixed at tip_y1 on every level (min T/nl)
)


def even(x: float) -> int:
    """Rounded count. No parity fix is needed: every transfinite count on the
    boundary of the unstructured region occurs in mirrored pairs (lower/upper,
    bottom/top), so that boundary always has an even number of edges."""
    return max(2, round(x))


def solve_ratio(L: float, y1: float, n: int) -> float:
    """r with y1 (r^n - 1)/(r - 1) = L (r < 1 allowed)."""
    if abs(y1 * n - L) < 1e-12 * L:
        return 1.0
    lo, hi = (1.0 + 1e-12, 4.0) if y1 * n < L else (0.05, 1.0 - 1e-12)
    for _ in range(300):
        m = 0.5 * (lo + hi)
        if y1 * (m**n - 1) / (m - 1) > L:
            hi = m
        else:
            lo = m
    return 0.5 * (lo + hi)


class Geo:
    def __init__(self):
        self.L, self.pt, self.ln = [], {}, {}

    def P(self, name, x, y):
        self.pt[name] = len(self.pt) + 1
        self.L.append(f"Point({self.pt[name]}) = {{{x:.12g}, {y:.12g}, 0}};")

    def Ln(self, name, a, b):
        self.ln[name] = len(self.ln) + 1
        self.L.append(f"Line({self.ln[name]}) = {{{self.pt[a]}, {self.pt[b]}}};")

    def Arc(self, name, a, c, b):
        self.ln[name] = len(self.ln) + 1
        self.L.append(f"Circle({self.ln[name]}) = {{{self.pt[a]}, {self.pt[c]}, {self.pt[b]}}};")

    def TF(self, name, n, r=1.0):
        prog = f" Using Progression {r:.12g}" if abs(r - 1) > 1e-12 else ""
        self.L.append(f"Transfinite Curve{{{self.ln[name]}}} = {n + 1}{prog};")

    def Blk(self, sid, loop, corners):
        cl = 1000 + sid
        ids = ", ".join(str(self.ln[k[1:]] * (-1 if k[0] == "-" else 1)) for k in loop)
        self.L.append(f"Curve Loop({cl}) = {{{ids}}};")
        self.L.append(f"Plane Surface({sid}) = {{{cl}}};")
        self.L.append(f"Transfinite Surface{{{sid}}} = {{{', '.join(str(self.pt[c]) for c in corners)}}};")
        self.L.append(f"Recombine Surface{{{sid}}};")


def geo(p: dict, s: float):
    T, R, xc, yc = p["bl_thick"], 0.05, 0.2, 0.2
    y1, hb = p["bl_y1"] * s, p["h_body"] * s
    # layer counts scale as 1/s from level 1, so the refinement ratio is the
    # same in every direction of the collar (rounded to even)
    y11, r1 = p["bl_y1"], p["bl_ratio"]
    nl = even(math.log(1 + T * (r1 - 1) / y11) / math.log(r1) / s)
    r = solve_ratio(T, y1, nl)          # collar layers: nl cells, first y1, sum T
    xj = xc + math.sqrt(R**2 - 0.01**2)
    xk = xc + math.sqrt((R + T)**2 - (0.01 + T)**2)
    fq = R / (R + T)
    qx, qy = xc + fq * (xk - xc), yc - fq * (0.01 + T)     # Q, lower
    th_q = math.atan2(yc - qy, qx - xc)
    # corner block wall edges: nl cells graded from J (first y1)
    len_jq = R * (th_q - math.atan2(0.01, xj - xc))
    r_jq = solve_ratio(len_jq, y1, nl)
    r_js = solve_ratio(xk - xj, y1, nl)
    # tangential counts of the uniform parts
    n_cyl = even((math.pi - th_q) * R / hb)
    n_fl = even((0.6 - T - xk) / hb)
    n_end = even((0.01 - T) / hb)
    tip = p["tip_y1"] > 0
    if tip:
        y1c = min(p["tip_y1"], T / nl)       # corner first cell, not refined
        rc = solve_ratio(T, y1c, nl)
        n_tc = even(T / hb)                   # flag / end-face part next to the corner
        c_last = y1c * rc ** (nl - 1)
    else:
        y1c, rc, n_tc, c_last = y1, r, nl, y1 * r ** (nl - 1)
    # wall strips
    yw1, hw = p["w_y1"] * s, p["h_wall"] * s
    Tw = p["w_thick"]
    nlw = even(math.log(1 + Tw * (p["w_ratio"] - 1) / p["w_y1"]) / math.log(p["w_ratio"]) / s)
    rw = solve_ratio(Tw, yw1, nlw)
    n_w = even(2.5 / hw)
    hmid = p["h_max"] * s
    n_io = even((0.41 - 2 * Tw) / hmid)

    g = Geo()
    g.P("c", xc, yc)
    for t, sg in (("l", -1), ("h", 1)):
        def Y(dy):  # offset from y = 0.2, mirrored
            return yc + sg * dy
        g.P("J" + t, xj, Y(0.01)); g.P("S" + t, xk, Y(0.01)); g.P("K" + t, xk, Y(0.01 + T))
        g.P("Q" + t, qx, Y(yc - qy))
        g.P("F" + t, 0.6 - T, Y(0.01)); g.P("Fo" + t, 0.6 - T, Y(0.01 + T))
        g.P("C" + t, 0.6, Y(0.01)); g.P("P1" + t, 0.6, Y(0.01 + T))
        g.P("X" + t, 0.6 + T, Y(0.01 + T)); g.P("P2" + t, 0.6 + T, Y(0.01))
        g.P("E" + t, 0.6, Y(0.01 - T)); g.P("Eo" + t, 0.6 + T, Y(0.01 - T))
    g.P("W", xc - R, yc); g.P("Wo", xc - R - T, yc)
    g.P("M", 0.6, yc); g.P("Mo", 0.6 + T, yc)
    for t, y0, y1w in (("b", 0.0, Tw), ("t", 0.41, 0.41 - Tw)):
        g.P("i" + t, 0, y0); g.P("iw" + t, 0, y1w); g.P("o" + t, 2.5, y0); g.P("ow" + t, 2.5, y1w)

    for t in ("l", "h"):
        # walls
        g.Arc("cjq" + t, "J" + t, "c", "Q" + t); g.Ln("fjs" + t, "J" + t, "S" + t)
        g.Arc("cwq" + t, "W", "c", "Q" + t)
        g.Ln("fsf" + t, "S" + t, "F" + t); g.Ln("ffc" + t, "F" + t, "C" + t)
        g.Ln("ece" + t, "C" + t, "E" + t); g.Ln("eem" + t, "E" + t, "M")
        # normals (wall -> outer)
        for a, b in (("Q", "K"), ("S", "K"), ("F", "Fo"), ("C", "P1"), ("C", "P2"), ("E", "Eo")):
            g.Ln(f"n{a}{b}{t}", a + t, b + t)
        # outer
        g.Arc("owk" + t, "Wo", "c", "K" + t); g.Ln("okf" + t, "K" + t, "Fo" + t)
        g.Ln("ofp" + t, "Fo" + t, "P1" + t); g.Ln("opx" + t, "P1" + t, "X" + t)
        g.Ln("oqx" + t, "P2" + t, "X" + t); g.Ln("ope" + t, "P2" + t, "Eo" + t)
        g.Ln("oem" + t, "Eo" + t, "Mo")
    g.Ln("nW", "W", "Wo"); g.Ln("nM", "M", "Mo")
    for t in ("b", "t"):
        g.Ln("w" + t, "i" + t, "o" + t); g.Ln("ws" + t, "iw" + t, "ow" + t)
        g.Ln("wi" + t, "i" + t, "iw" + t); g.Ln("wo" + t, "o" + t, "ow" + t)
    g.Ln("inm", "iwb", "iwt"); g.Ln("oum", "owb", "owt")

    for t in ("l", "h"):
        g.TF("cjq" + t, nl, r_jq); g.TF("fjs" + t, nl, r_js)
        for k in ("nQK", "nSK", "nFFo", "nEEo"):
            g.TF(k + t, nl, r)
        for k in ("nCP1", "nCP2", "opx", "oqx"):
            g.TF(k + t, nl, rc)
        g.TF("cwq" + t, n_cyl); g.TF("owk" + t, n_cyl)
        g.TF("fsf" + t, n_fl); g.TF("okf" + t, n_fl)
        if tip:                                                     # uniform up to the corner
            for k in ("ffc", "ofp", "ece", "ope"):
                g.TF(k + t, n_tc)
        else:
            g.TF("ffc" + t, nl, 1 / r); g.TF("ofp" + t, nl, 1 / r)  # graded down to the tip corner
            g.TF("ece" + t, nl, r); g.TF("ope" + t, nl, r)          # graded up from the corner
        g.TF("eem" + t, n_end); g.TF("oem" + t, n_end)
    g.TF("nW", nl, r); g.TF("nM", nl, r)
    for t in ("b", "t"):
        g.TF("w" + t, n_w); g.TF("ws" + t, n_w)
        rr = rw if t == "b" else 1 / rw
        g.TF("wi" + t, nlw, rr); g.TF("wo" + t, nlw, rr)
    g.TF("inm", n_io); g.TF("oum", n_io)

    sid = 0
    blocks = []
    for t in ("l", "h"):
        sid += 1; blocks.append(sid)
        g.Blk(sid, ["+cjq" + t, "+nQK" + t, "-nSK" + t, "-fjs" + t], ["J" + t, "Q" + t, "K" + t, "S" + t])
        sid += 1; blocks.append(sid)
        g.Blk(sid, ["+cwq" + t, "+nQK" + t, "-owk" + t, "-nW"], ["W", "Q" + t, "K" + t, "Wo"])
        sid += 1; blocks.append(sid)
        g.Blk(sid, ["+fsf" + t, "+nFFo" + t, "-okf" + t, "-nSK" + t], ["S" + t, "F" + t, "Fo" + t, "K" + t])
        sid += 1; blocks.append(sid)
        g.Blk(sid, ["+ffc" + t, "+nCP1" + t, "-ofp" + t, "-nFFo" + t], ["F" + t, "C" + t, "P1" + t, "Fo" + t])
        sid += 1; blocks.append(sid)
        g.Blk(sid, ["+nCP1" + t, "+opx" + t, "-oqx" + t, "-nCP2" + t], ["C" + t, "P1" + t, "X" + t, "P2" + t])
        sid += 1; blocks.append(sid)
        g.Blk(sid, ["+ece" + t, "+nEEo" + t, "-ope" + t, "-nCP2" + t], ["C" + t, "E" + t, "Eo" + t, "P2" + t])
        sid += 1; blocks.append(sid)
        g.Blk(sid, ["+eem" + t, "+nM", "-oem" + t, "-nEEo" + t], ["E" + t, "M", "Mo", "Eo" + t])
    for t in ("b", "t"):
        sid += 1; blocks.append(sid)
        g.Blk(sid, ["+w" + t, "+wo" + t, "-ws" + t, "-wi" + t], ["i" + t, "o" + t, "ow" + t, "iw" + t])
    ln = g.ln
    outer = ([ln["wsb"], ln["oum"], -ln["wst"], -ln["inm"]])
    coll = []
    for k in ("owkl", "okfl", "ofpl", "opxl", "-oqxl", "opel", "oeml",
              "-oemh", "-opeh", "oqxh", "-opxh", "-ofph", "-okfh", "-owkh"):
        coll.append(-ln[k[1:]] if k[0] == "-" else ln[k])
    g.L.append(f"Curve Loop(2000) = {{{', '.join(map(str, outer))}}};")
    g.L.append(f"Curve Loop(2001) = {{{', '.join(map(str, coll))}}};")
    g.L.append("Plane Surface(500) = {2000, 2001};")
    g.L.append("Recombine Surface{500};")
    collar_curves = sorted({abs(x) for x in coll})
    tips = [g.pt[k] for k in ("P1l", "P2l", "P1h", "P2h")]
    gr = p["grow"] * s
    ht = hb * (1 + T / R)
    g.L.append(f"""
Field[10] = Distance;
Field[10].CurvesList = {{{', '.join(map(str, collar_curves))}}};
Field[10].Sampling = 4000;
Field[11] = MathEval;
Field[11].F = "{ht:.6g} + {gr:.6g}*F10";
Field[16] = Distance;
Field[16].PointsList = {{{', '.join(map(str, tips))}}};
Field[17] = MathEval;
Field[17].F = "{(y1 if not tip else c_last):.6g} + {(r - 1 if not tip else gr):.6g}*F16";
Field[12] = Box;
Field[12].VIn = {p['h_band'] * s:.6g};
Field[12].VOut = {p['h_max'] * s:.6g};
Field[12].XMin = 0; Field[12].XMax = {p['x_band']};
Field[12].YMin = 0.10; Field[12].YMax = 0.30;
Field[12].ZMin = -1; Field[12].ZMax = 1;
Field[12].Thickness = {(p['h_max'] - p['h_band']) / p['grow']:.6g};
Field[14] = Distance;
Field[14].CurvesList = {{{ln['wsb']}, {ln['wst']}}};
Field[14].Sampling = 5000;
Field[15] = MathEval;
Field[15].F = "{hw:.6g} + {gr:.6g}*F14";
Field[13] = Min;
Field[13].FieldsList = {{11, 12, 15, 17}};
Background Field = 13;
Mesh.MeshSizeExtendFromBoundary = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.Algorithm = 8;
Mesh.RecombinationAlgorithm = 1;
Mesh.RecombineOptimizeTopology = 5;
Mesh.Smoothing = 10;
Mesh.MshFileVersion = 2.2;
Physical Surface("fluid") = {{{', '.join(map(str, blocks))}, 500}};
// patch order as the tutorial (mapFields -consistent needs it)
Physical Curve("plate") = {{{', '.join(str(ln[k + t]) for t in ('l', 'h') for k in ('fjs', 'fsf', 'ffc', 'ece', 'eem'))}}};
Physical Curve("outlet") = {{{ln['wob']}, {ln['oum']}, {ln['wot']}}};
Physical Curve("inlet") = {{{ln['wib']}, {ln['inm']}, {ln['wit']}}};
Physical Curve("cylinder") = {{{', '.join(str(ln[k + t]) for t in ('l', 'h') for k in ('cjq', 'cwq'))}}};
Physical Curve("bottom") = {{{ln['wb']}}};
Physical Curve("top") = {{{ln['wt']}}};
""")
    info = (f"s {s:.6f}; collar T {T:g}: {nl} layers, first {y1:.4g}, ratio {r:.5f}; corner block wall ratios "
            f"{r_jq:.4f}/{r_js:.4f}; tangential uniform: cylinder half {n_cyl}, flag {n_fl}, end half {n_end} (+{nl} graded "
            f"at each tip corner); tip corner {nl} x {nl}, first {y1c:.4g}, ratio {rc:.5f}, tip parts {n_tc}; wall strip {Tw:g}: {nlw} layers, first {yw1:.4g}, ratio {rw:.5f}, {n_w} along")
    return "// generated by ht_mesh_gmsh2.py; " + info + "\n" + "\n".join(g.L) + "\n", info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--level", type=int, default=1)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--no-mesh", action="store_true")
    for k, v in DEFAULTS.items():
        ap.add_argument("--" + k.replace("_", "-"), type=float, default=v)
    a = ap.parse_args()
    p = {k: getattr(a, k) for k in DEFAULTS}
    s = 2.0 ** (-(a.level - 1) / 2)
    a.out.mkdir(parents=True, exist_ok=True)
    text, info = geo(p, s)
    (a.out / "mesh.geo").write_text(text)
    (a.out / "mesh_family.txt").write_text(
        "generator ht_mesh_gmsh2.py\n" + "".join(f"{k} {v:g}\n" for k, v in p.items())
        + f"level {a.level}\nscale {s:.6f}\n# {info}\n")
    print(info)
    if not a.no_mesh:
        with (a.out / "log.gmsh").open("w") as fh:
            r = subprocess.run([GMSH, str(a.out / "mesh.geo"), "-2", "-o", str(a.out / "mesh2d.msh"), "-nt", "1"],
                               stdout=fh, stderr=subprocess.STDOUT)
        if r.returncode:
            raise SystemExit(f"gmsh failed, see {a.out / 'log.gmsh'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
