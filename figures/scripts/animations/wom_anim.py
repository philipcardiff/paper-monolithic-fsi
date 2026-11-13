# pvbatch wom_anim.py <case> <framesdir>: pulsatile (Womersley) tube over its last period
# (axisymmetric wedge mirrored about the axis): axial fluid velocity with profile arrows at
# five stations, wall coloured by |radial displacement| at true scale (the fluid and
# solid displacement fields have different references, so nothing is magnified).
import sys, os, json
from paraview.simple import *
case, outdir = sys.argv[1], sys.argv[2]; os.makedirs(outdir, exist_ok=True)
MAG = 1.0
series = json.load(open(f"{case}/VTK/fluid/wom_anim.vtm.series"))["files"]
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/{series[0]['name']}"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/{series[0]['name']}"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
fwc = Calculator(Input=flp); fwc.ResultArrayName = "Dm"; fwc.Function = f"{MAG-1}*D"
fwarp = WarpByVector(Input=fwc); fwarp.Vectors = ["POINTS", "Dm"]
fsl = Slice(Input=fwarp); fsl.SliceType = "Plane"; fsl.SliceType.Origin = [0, 0, 0]; fsl.SliceType.Normal = [0, 0, 1]
ux = Calculator(Input=fsl); ux.ResultArrayName = "Ux"; ux.Function = "1000*U_X"
uxm = MergeBlocks(Input=ux); fm_m = Transform(Input=uxm); fm_m.Transform.Scale = [1, -1, 1]
fm = AppendDatasets(Input=[uxm, fm_m])
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
swc = Calculator(Input=sop); swc.ResultArrayName = "Dm"; swc.Function = f"{MAG}*D"
swarp = WarpByVector(Input=swc); swarp.Vectors = ["POINTS", "Dm"]
ssl = Slice(Input=swarp); ssl.SliceType = "Plane"; ssl.SliceType.Origin = [0, 0, 0]; ssl.SliceType.Normal = [0, 0, 1]
dr = Calculator(Input=ssl); dr.ResultArrayName = "Dr"; dr.Function = "abs(D_Y)*1000"
swm = MergeBlocks(Input=dr); sm_m = Transform(Input=swm); sm_m.Transform.Scale = [1, -1, 1]
sm = Transform(Input=AppendDatasets(Input=[swm, sm_m])); sm.Transform.Translate = [0, 0, 0.02]
lines = []
for x in (1.5, 4.5, 7.5, 10.5, 13.5):
    pl = PlotOverLine(Input=fsl); pl.Point1 = [x, 0.0, 0]; pl.Point2 = [x, 0.985, 0]; pl.Resolution = 8; lines.append(pl)
uv = Calculator(Input=AppendDatasets(Input=lines)); uv.ResultArrayName = "Uax"; uv.Function = "U_X*iHat"
gl = Glyph(Input=uv, GlyphType="Arrow"); gl.OrientationArray = ["POINTS", "Uax"]; gl.ScaleArray = ["POINTS", "Uax"]
gl.ScaleFactor = 0.95 / 0.00135; gl.GlyphMode = "All Points"; gl.GlyphType.TipRadius = 0.06; gl.GlyphType.TipLength = 0.22; gl.GlyphType.ShaftRadius = 0.015
glm = MergeBlocks(Input=gl); gm_m = Transform(Input=glm); gm_m.Transform.Scale = [1, -1, 1]
glt = Transform(Input=AppendDatasets(Input=[glm, gm_m])); glt.Transform.Translate = [0, 0, 0.05]
umax = dmax = 0.0
for f in series:
    fl.FileName = [f"{case}/VTK/fluid/{f['name']}"]; so.FileName = [f"{case}/VTK/solid/{f['name']}"]
    ux.UpdatePipeline(); dr.UpdatePipeline()
    r = ux.PointData["Ux"].GetRange(); umax = max(umax, abs(r[0]), abs(r[1])); dmax = max(dmax, dr.PointData["Dr"].GetRange()[1])
print("umax mm/s", umax, "dmax mm", dmax)
U = round(umax + 0.05, 1); DM = round(dmax + 0.05, 1)
v = CreateView("RenderView"); v.ViewSize = [1920, 400]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(fm, v); ColorBy(d1, ("POINTS", "Ux"))
lu = GetColorTransferFunction("Ux"); lu.ApplyPreset("Blue Orange (divergent)", True); lu.Discretize = 1; lu.NumberOfTableValues = 16; lu.RescaleTransferFunction(-U, U)
d2 = Show(sm, v); ColorBy(d2, ("POINTS", "Dr"))
ld = GetColorTransferFunction("Dr"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 10; ld.RescaleTransferFunction(0.0, DM)
d3 = Show(glt, v); d3.ColorArrayName = ["POINTS", ""]; d3.AmbientColor = d3.DiffuseColor = [0, 0, 0]
for l, t, pos, labs in ((lu, "Axial fluid velocity (mm/s)", [0.10, 0.02], [-U, -U / 2, 0, U / 2, U]),
                        (ld, "Wall radial displacement magnitude (mm)", [0.58, 0.02], [0, DM / 2, DM])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 20; sb.LabelFontSize = 17
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.28; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = "%-#.2g"
tt = Text(); tl = Show(tt, v); tl.WindowLocation = "Lower Center"; tl.FontSize = 18; tl.Color = [0.15, 0.15, 0.15]
pass  # true scale, no magnification label
v.CameraParallelProjection = 1
v.CameraPosition = [7.5, -0.45, 30]; v.CameraFocalPoint = [7.5, -0.45, 0]; v.CameraViewUp = [0, 1, 0]; v.CameraParallelScale = 1.646
T0 = series[0]["time"]
for i, f in enumerate(series):
    fl.FileName = [f"{case}/VTK/fluid/{f['name']}"]; so.FileName = [f"{case}/VTK/solid/{f['name']}"]
    tt.Text = f"t/T = {(f['time'] - T0) / 50.0:.3f}"
    SaveScreenshot(f"{outdir}/f{i:04d}.png", v, ImageResolution=[1920, 400])
print("frames", len(series))
