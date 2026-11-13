# pvbatch coll_anim.py <case> <outdir> [<time> <out.png> <width> <height>]
# Collapsible channel (QM, fluid level 2, 320x8 wall, rho_s/rho_f = 1, dt = 1/160 s):
# two stacked panels at true scale, (top) fluid kinematic pressure, (bottom) fluid speed
# with streamlines; in both the wall coloured by |D| on its displaced configuration and its
# undeformed outline. Without the optional arguments: one frame per written time in outdir;
# with them: a single image of the written time closest to <time>.
import sys, os, json
from paraview.simple import *
case, outdir = sys.argv[1], sys.argv[2]
single = len(sys.argv) > 3
W = int(sys.argv[5]) if single else 1920
nm = os.path.basename(case.rstrip("/"))
series = json.load(open(f"{case}/VTK/fluid/{nm}.vtm.series"))["files"]
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/{series[0]['name']}"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/{series[0]['name']}"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
fsl = Slice(Input=flp); fsl.SliceType = "Plane"; fsl.SliceType.Origin = [0, 0, 0.05]; fsl.SliceType.Normal = [0, 0, 1]
spd = Calculator(Input=fsl); spd.ResultArrayName = "speed"; spd.Function = "mag(U)"
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
ssl = Slice(Input=sop); ssl.SliceType = "Plane"; ssl.SliceType.Origin = [0, 0, 0.05]; ssl.SliceType.Normal = [0, 0, 1]
warp = WarpByVector(Input=ssl); warp.Vectors = ["POINTS", "D"]
wall = Transform(Input=warp); wall.Transform.Translate = [0, 0, 0.2]
und0 = Outline(Input=ssl); und = Transform(Input=und0); und.Transform.Translate = [0, 0, 0.3]
seeds = Line(Point1=[4.05, 0.02, 0.05], Point2=[4.05, 0.98, 0.05], Resolution=17)
st = StreamTracerWithCustomSource(Input=fsl, SeedSource=seeds); st.Vectors = ["POINTS", "U"]
st.MaximumStreamlineLength = 30.0; st.IntegrationDirection = "FORWARD"
stt = Transform(Input=st); stt.Transform.Translate = [0, 0, 0.1]
P, UM, DM = 450.0, 4.8, 0.22
X0, X1 = 4.0, 16.5
HP, HL = 250, 170            # panel and legend heights at 1920 wide (scaled with W)
sc = W / 1920.0; fs = sc
HP, HL = int(HP * sc), int(HL * sc); H = 2 * HP + HL


def cam(v):
    xc = 0.5 * (X0 + X1); v.CameraParallelProjection = 1
    v.CameraPosition = [xc, 0.52, 30]; v.CameraFocalPoint = [xc, 0.52, 0]; v.CameraViewUp = [0, 1, 0]
    v.CameraParallelScale = 0.5 * (X1 - X0) * HP / W


def blank():
    v = CreateView("RenderView"); v.OrientationAxesVisibility = 0
    v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]; return v


lp = GetColorTransferFunction("p"); lp.ApplyPreset("Cool to Warm", True); lp.RescaleTransferFunction(-P, P)
lu = GetColorTransferFunction("speed"); lu.ApplyPreset("Viridis", True); lu.RescaleTransferFunction(0.0, UM)
ld = GetColorTransferFunction("D"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.RescaleTransferFunction(0.0, DM)
for l, n in ((lp, 16), (lu, 16), (ld, 11)):
    l.Discretize = 1; l.NumberOfTableValues = n


def panel(field):
    v = blank()
    if field == "p":
        d = Show(fsl, v); ColorBy(d, ("POINTS", "p")); d.LookupTable = lp
    else:
        d = Show(spd, v); ColorBy(d, ("POINTS", "speed")); d.LookupTable = lu
        ds = Show(stt, v); ds.ColorArrayName = ["POINTS", ""]; ds.AmbientColor = ds.DiffuseColor = [1, 1, 1]; ds.LineWidth = 1.5 * fs; ds.Opacity = 0.75
    dw = Show(wall, v); ColorBy(dw, ("POINTS", "D", "Magnitude")); dw.LookupTable = ld
    du = Show(und, v); du.AmbientColor = du.DiffuseColor = [0, 0, 0]; du.LineWidth = 2.5 * fs; du.ColorArrayName = ["POINTS", ""]
    HideScalarBarIfNotNeeded(lp, v); HideScalarBarIfNotNeeded(lu, v); HideScalarBarIfNotNeeded(ld, v)
    for l in (lp, lu, ld):
        GetScalarBar(l, v).Visibility = 0
    cam(v); return v


vp, vu, vl = panel("p"), panel("U"), blank()
for l, r in ((lp, (-P, P)), (lu, (0.0, UM)), (ld, (0.0, DM))):
    l.AutomaticRescaleRangeMode = "Never"; l.RescaleTransferFunction(*r)
for l, t, pos, lb in ((lp, "Fluid kinematic pressure (m\u00b2/s\u00b2)", [0.03, 0.26], [-400, -200, 0, 200, 400]),
                      (lu, "Fluid speed (m/s)", [0.36, 0.26], [0, 1, 2, 3, 4]),
                      (ld, "Wall displacement magnitude (m)", [0.69, 0.26], [0, 0.1, 0.2])):
    sb = GetScalarBar(l, vl); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = int(21 * fs); sb.LabelFontSize = int(18 * fs)
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos; sb.ScalarBarThickness = int(14 * fs)
    sb.ScalarBarLength = 0.28; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = lb; sb.LabelFormat = "%-#.3g"
lay = CreateLayout("coll")
lay.SplitVertical(0, HP / H); lay.SplitVertical(2, HP / (HP + HL))
AssignViewToLayout(view=vp, layout=lay, hint=1); AssignViewToLayout(view=vu, layout=lay, hint=5); AssignViewToLayout(view=vl, layout=lay, hint=6)
lay.SetSize(W, H)
tt = Text(); tl = Show(tt, vl); tl.WindowLocation = "Upper Center"; tl.FontSize = int(20 * fs); tl.Color = [0.15, 0.15, 0.15]


def load(f):
    fl.FileName = [f"{case}/VTK/fluid/{f['name']}"]; so.FileName = [f"{case}/VTK/solid/{f['name']}"]
    tt.Text = f"t = {f['time']:.4f} s"


if single:
    t = float(sys.argv[3]); f = min(series, key=lambda x: abs(x["time"] - t)); load(f)
    tl.Visibility = 0
    SaveScreenshot(sys.argv[4], lay, ImageResolution=[W, H]); print("image at t =", f["time"])
else:
    os.makedirs(outdir, exist_ok=True)
    for i, f in enumerate(series):
        load(f); SaveScreenshot(f"{outdir}/f{i:04d}.png", lay, ImageResolution=[W, H])
    print("frames", len(series))
