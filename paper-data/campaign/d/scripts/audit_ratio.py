"""Max neighbour cell-size ratio sqrt(V_P/V_N) over internal faces of a 2-D fluid mesh."""
import re, sys, math, json
from pathlib import Path
case = Path(sys.argv[1])
def lst(p):
    t = p.read_text()
    m = re.search(r"\n(\d+)\s*\n\(", t)
    n = int(m.group(1)); body = t[m.end():]
    return body, n
def scal(p):
    body, n = lst(p); return [float(x) for x in body.split(None, n)[:n]]
def vecs(p):
    body, n = lst(p); v = re.findall(r"\(([^()]+)\)", body)[:n]; return [tuple(map(float, s.split())) for s in v]
def labels(p):
    body, n = lst(p); return [int(x) for x in body.split(None, n)[:n]]
pm = case / "constant/fluid/polyMesh"
own, nei = labels(pm / "owner"), labels(pm / "neighbour")
V = scal(case / "constant/fluid/V"); C = vecs(case / "constant/fluid/C")
out = []
for f, (o, n) in enumerate(zip(own, nei)):
    r = math.sqrt(max(V[o], V[n]) / min(V[o], V[n]))
    x = 0.5 * (C[o][0] + C[n][0]); y = 0.5 * (C[o][1] + C[n][1])
    out.append((r, x, y))
out.sort(reverse=True)
wake = [t for t in out if 0.6 < t[1] < 2.5 and 0.1 < t[2] < 0.3]
cnt = lambda L, a: sum(1 for t in L if t[0] > a)
print(json.dumps(dict(cells=len(V), max=out[0], wake_max=wake[0] if wake else None,
    faces_gt_1p5=cnt(out, 1.5), faces_gt_2=cnt(out, 2.0), wake_gt_1p5=cnt(wake, 1.5), wake_gt_2=cnt(wake, 2.0),
    top_wake=[(round(r,3), round(x,4), round(y,4)) for r, x, y in wake[:6]])))
