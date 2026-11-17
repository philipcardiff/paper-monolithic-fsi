# pvbatch coll_trough.py <case> <time> <out.png> [lic]
# Collapsible channel (QM, fluid level 2, 320x8 wall, rho_s/rho_f = 1, dt = 1/160 s) at one
# written time, two stacked panels at true scale: (top) fluid kinematic pressure, (bottom)
# fluid speed, optionally with a line-integral-convolution texture showing the flow
# direction; in both the wall coloured by |D| on its displaced configuration and its
# undeformed outline. Colour ranges are those of the chosen time (not the fixed ranges of
# the animation, coll_anim.py).
import sys, os, json
from paraview.simple import *
case, t, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
lic = len(sys.argv) > 4 and sys.argv[4] == "lic"
W = 2400
nm = os.path.basename(case.rstrip("/"))
series = json.load(open(f"{case}/VTK/fluid/{nm}.vtm.series"))["files"]
f = min(series, key=lambda x: abs(x["time"] - t))
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/{f['name']}"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/{f['name']}"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
fsl = Slice(Input=flp); fsl.SliceType = "Plane"; fsl.SliceType.Origin = [0, 0, 0.05]; fsl.SliceType.Normal = [0, 0, 1]
spd = Calculator(Input=fsl); spd.ResultArrayName = "speed"; spd.Function = "mag(U)"
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
ssl = Slice(Input=sop); ssl.SliceType = "Plane"; ssl.SliceType.Origin = [0, 0, 0.05]; ssl.SliceType.Normal = [0, 0, 1]
warp = WarpByVector(Input=ssl); warp.Vectors = ["POINTS", "D"]
wall = Transform(Input=warp); wall.Transform.Translate = [0, 0, 0.2]
und0 = Outline(Input=ssl); und = Transform(Input=und0); und.Transform.Translate = [0, 0, 0.3]
spd.UpdatePipeline(); warp.UpdatePipeline()
pr = fsl.PointData["p"].GetRange(); ur = spd.PointData["speed"].GetRange(); dr = warp.PointData["D"].GetRange(-1)
print("t =", f["time"], "p", pr, "speed", ur, "Dmax", dr[1])
X0, X1 = 4.0, 16.5
HP, HL = 300, 190
H = 2 * HP + HL


def cam(v):
    xc = 0.5 * (X0 + X1); v.CameraParallelProjection = 1
    v.CameraPosition = [xc, 0.52, 30]; v.CameraFocalPoint = [xc, 0.52, 0]; v.CameraViewUp = [0, 1, 0]
    v.CameraParallelScale = 0.5 * (X1 - X0) * HP / W


def blank():
    v = CreateView("RenderView"); v.OrientationAxesVisibility = 0
    v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]; return v


P0 = 50.0 * int(pr[0] / 50.0 - 1)            # round the pressure range outwards to 50
U1 = 0.25 * int(ur[1] / 0.25 + 1)
D1 = 0.05 * int(dr[1] / 0.05 + 1)
lp = GetColorTransferFunction("p"); lp.ApplyPreset("Viridis", True)
lu = GetColorTransferFunction("speed"); lu.ApplyPreset("Inferno", True)
ld = GetColorTransferFunction("D"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction()
for l, n in ((lp, 16), (lu, 16), (ld, 10)):
    l.Discretize = 1; l.NumberOfTableValues = n
rng = {lp: (P0, 0.0), lu: (0.0, U1), ld: (0.0, D1)}


def panel(field):
    v = blank()
    if field == "p":
        d = Show(fsl, v); ColorBy(d, ("POINTS", "p")); d.LookupTable = lp
    else:
        d = Show(spd, v)
        if lic:
            d.SetRepresentationType("Surface LIC")
            d.SelectInputVectors = ["POINTS", "U"]
            d.ColorMode = "Multiply"; d.EnhanceContrast = "LIC and Color"; d.LICIntensity = 0.9
            d.NumberOfSteps = 60; d.StepSize = 0.5; d.NormalizeVectors = 1
        ColorBy(d, ("POINTS", "speed")); d.LookupTable = lu
    dw = Show(wall, v); ColorBy(dw, ("POINTS", "D", "Magnitude")); dw.LookupTable = ld
    du = Show(und, v); du.AmbientColor = du.DiffuseColor = [0, 0, 0]; du.LineWidth = 3; du.ColorArrayName = ["POINTS", ""]
    for l in (lp, lu, ld):
        HideScalarBarIfNotNeeded(l, v); GetScalarBar(l, v).Visibility = 0
    cam(v); return v


vp, vu, vl = panel("p"), panel("U"), blank()
for l, r in rng.items():
    l.AutomaticRescaleRangeMode = "Never"; l.RescaleTransferFunction(*r)


def ticks(a, b, n):
    return [a + (b - a) * k / n for k in range(n + 1)]


for l, ttl, pos, lb in ((lp, "Fluid kinematic pressure (m²/s²)", [0.03, 0.22], ticks(P0, 0.0, 3)),
                        (lu, "Fluid speed (m/s)", [0.36, 0.22], ticks(0.0, U1, 4)),
                        (ld, "Wall displacement magnitude (m)", [0.69, 0.22], ticks(0.0, D1, 5))):
    sb = GetScalarBar(l, vl); sb.Title = ttl; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 26; sb.LabelFontSize = 22
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos; sb.ScalarBarThickness = 18
    sb.ScalarBarLength = 0.28; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = lb; sb.LabelFormat = "%-#.3g"
lay = CreateLayout("coll")
lay.SplitVertical(0, HP / H); lay.SplitVertical(2, HP / (HP + HL))
AssignViewToLayout(view=vp, layout=lay, hint=1); AssignViewToLayout(view=vu, layout=lay, hint=5); AssignViewToLayout(view=vl, layout=lay, hint=6)
lay.SetSize(W, H)
SaveScreenshot(out, lay, ImageResolution=[W, H])
