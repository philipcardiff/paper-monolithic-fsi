# pvbatch wom_field.py <case> <step> <out.png>: pulsatile (Womersley) tube, axisymmetric
# wedge mirrored about the axis: axial fluid velocity with velocity profiles (arrows)
# at five stations, and the wall coloured by radial displacement (no magnification).
import sys
from paraview.simple import *
case, step, out = sys.argv[1], sys.argv[2], sys.argv[3]
MAG = 100.0
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/{step}.vtm"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/{step}.vtm"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
fsl = Slice(Input=flp); fsl.SliceType = "Plane"; fsl.SliceType.Origin = [0, 0, 0]; fsl.SliceType.Normal = [0, 0, 1]
ux = Calculator(Input=fsl); ux.ResultArrayName = "Ux"; ux.Function = "1000*U_X"
uxm = MergeBlocks(Input=ux)
fm_m = Transform(Input=uxm); fm_m.Transform.Scale = [1, -1, 1]
fm = AppendDatasets(Input=[uxm, fm_m])
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
ssl = Slice(Input=sop); ssl.SliceType = "Plane"; ssl.SliceType.Origin = [0, 0, 0]; ssl.SliceType.Normal = [0, 0, 1]
dr = Calculator(Input=ssl); dr.ResultArrayName = "Dr"; dr.Function = "D_Y*1000"
wv = Calculator(Input=dr); wv.ResultArrayName = "Dw"; wv.Function = f"D*{MAG}"
sw = wv  # no magnification: the wall is coloured by its radial displacement
swm = MergeBlocks(Input=sw)
sm_m = Transform(Input=swm); sm_m.Transform.Scale = [1, -1, 1]
sm = AppendDatasets(Input=[swm, sm_m])
# profile arrows at five stations (upper half and mirrored)
lines = []
for x in (1.5, 4.5, 7.5, 10.5, 13.5):
    pl = PlotOverLine(Input=fsl); pl.Point1 = [x, -0.0, 0]; pl.Point2 = [x, 0.985, 0]; pl.Resolution = 8
    lines.append(pl)
app = AppendDatasets(Input=lines)
uv = Calculator(Input=app); uv.ResultArrayName = "Uax"; uv.Function = "U_X*iHat"
gl = Glyph(Input=uv, GlyphType="Arrow"); gl.OrientationArray = ["POINTS", "Uax"]; gl.ScaleArray = ["POINTS", "Uax"]
gl.ScaleFactor = 0.95 / 0.00135; gl.GlyphMode = "All Points"; gl.GlyphType.TipRadius = 0.06; gl.GlyphType.TipLength = 0.22; gl.GlyphType.ShaftRadius = 0.015
glm = MergeBlocks(Input=gl)
gm_m = Transform(Input=glm); gm_m.Transform.Scale = [1, -1, 1]
gm = AppendDatasets(Input=[glm, gm_m])
glt = Transform(Input=gm); glt.Transform.Translate = [0, 0, 0.05]
v = CreateView("RenderView"); v.ViewSize = [2400, 560]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
d1 = Show(fm, v); ColorBy(d1, ("POINTS", "Ux"))
lu = GetColorTransferFunction("Ux"); lu.ApplyPreset("Blue Orange (divergent)", True); lu.Discretize = 1; lu.NumberOfTableValues = 16
U = 1.4; lu.RescaleTransferFunction(-U, U)
d2 = Show(sm, v); ColorBy(d2, ("POINTS", "Dr"))
ld = GetColorTransferFunction("Dr"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.Discretize = 1; ld.NumberOfTableValues = 10; ld.RescaleTransferFunction(0.0, 0.6)
d3 = Show(glt, v); d3.ColorArrayName = ["POINTS", ""]; d3.AmbientColor = d3.DiffuseColor = [0, 0, 0]
for l, t, pos, labs, fmt in ((lu, "Axial fluid velocity (mm/s)", [0.12, 0.02], [-1.4, -0.7, 0, 0.7, 1.4], "%-#.2g"),
                              (ld, "Wall radial displacement (mm)", [0.6, 0.02], [0, 0.2, 0.4, 0.6], "%-#.2g")):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 26; sb.LabelFontSize = 22
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.28; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = fmt
v.CameraParallelProjection = 1
v.CameraPosition = [7.5, -0.5, 30]; v.CameraFocalPoint = [7.5, -0.5, 0]; v.CameraViewUp = [0, 1, 0]
v.CameraParallelScale = 1.78
SaveScreenshot(out, v, ImageResolution=[2400, 560])
