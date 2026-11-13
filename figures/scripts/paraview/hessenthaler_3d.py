# pvbatch hv_3d_v2.py <case> <out.png>: Hessenthaler Phase I, QM rF0 (build-bf697)
# at t = 45 s. Deformed flap coloured by |D| (mm, Reds) with its undeformed
# outline, streamlines coloured by |U| (Viridis) from both inlets and from a seed
# cloud around the flap (both directions), translucent vessel walls.
import sys
from paraview.simple import *
case, out = sys.argv[1], sys.argv[2]
ZCUT = 0.13
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/case_22500.vtm"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/case_22500.vtm"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]
flp = CellDatatoPointData(Input=fli)
wall = XMLPolyDataReader(FileName=[f"{case}/VTK/fluid/case_22500/boundary/wall.vtp"])
wallc = Clip(Input=wall); wallc.ClipType = "Plane"; wallc.ClipType.Origin = [0, 0, ZCUT]; wallc.ClipType.Normal = [0, 0, 1]; wallc.Invert = 1
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]
sos = ExtractSurface(Input=soi)
und = FeatureEdges(Input=sos); und.BoundaryEdges = 0; und.NonManifoldEdges = 0; und.ManifoldEdges = 0; und.FeatureAngle = 30
warp = WarpByVector(Input=sos); warp.Vectors = ["POINTS", "pointD"]; warp.ScaleFactor = 1.0
dmm = Calculator(Input=warp); dmm.AttributeType = "Point Data"; dmm.ResultArrayName = "Dmm"; dmm.Function = "mag(pointD)*1000"
def tubes(seed, n, direction, radius):
    st = StreamTracerWithCustomSource(Input=flp, SeedSource=seed)
    st.Vectors = ["POINTS", "U"]; st.IntegrationDirection = direction; st.MaximumStreamlineLength = 0.6
    st.IntegratorType = "Runge-Kutta 4-5"; st.MaximumSteps = 20000
    c = Clip(Input=st); c.ClipType = "Plane"; c.ClipType.Origin = [0, 0, ZCUT]; c.ClipType.Normal = [0, 0, 1]; c.Invert = 1
    t = Tube(Input=ExtractSurface(Input=c)); t.Radius = radius; t.NumberofSides = 10
    return t
inlet = AppendDatasets(Input=[PointSource(Center=[0, y, -0.026], Radius=0.0095, NumberOfPoints=90) for y in (0.02715, -0.02715)])
near = PointSource(Center=[0, 0.004, 0.040], Radius=0.024, NumberOfPoints=80)
t_in = tubes(inlet, 110, "FORWARD", 0.00022)
t_nr = tubes(near, 80, "BOTH", 0.00013)
v = CreateView("RenderView"); v.ViewSize = [2400, 1450]; v.OrientationAxesVisibility = 0
v.Background = [1, 1, 1]; v.UseColorPaletteForBackground = 0
try: v.UseFXAA = 1
except Exception: pass
dw = Show(wallc, v); dw.Representation = "Surface"; dw.AmbientColor = dw.DiffuseColor = [0.72, 0.75, 0.80]
dw.Opacity = 0.14; dw.ColorArrayName = ["POINTS", ""]; dw.Specular = 0.0
lu = GetColorTransferFunction("U"); lu.ApplyPreset("Viridis", True); lu.RescaleTransferFunction(0.0, 0.63)
for t in (t_in, t_nr):
    d = Show(t, v); ColorBy(d, ("POINTS", "U", "Magnitude")); d.Specular = 0.25
lu.AutomaticRescaleRangeMode = "Never"; lu.RescaleTransferFunction(0.0, 0.63)
ds = Show(dmm, v); ColorBy(ds, ("POINTS", "Dmm")); ds.Specular = 0.2
ld = GetColorTransferFunction("Dmm"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.AutomaticRescaleRangeMode = "Never"; ld.RescaleTransferFunction(0.0, 16.2)
du = Show(und, v); du.ColorArrayName = ["POINTS", ""]; du.AmbientColor = du.DiffuseColor = [0.0, 0.0, 0.0]; du.LineWidth = 3.0; du.RenderLinesAsTubes = 1
for l, t, labs, pos in ((lu, "Fluid velocity magnitude (m/s)", [0, 0.2, 0.4, 0.6], [0.10, 0.035]),
                        (ld, "Flap displacement magnitude (mm)", [0, 4, 8, 12, 16], [0.58, 0.035])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 30; sb.LabelFontSize = 26
    sb.Orientation = "Horizontal"; sb.AddRangeLabels = 0; sb.WindowLocation = "Any Location"; sb.ScalarBarLength = 0.30
    sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = "%-#.2g"; sb.Position = pos
v.CameraPosition = [-0.205, 0.090, -0.066]; v.CameraFocalPoint = [0.0, -0.016, 0.050]; v.CameraViewUp = [0, 1, 0]
v.CameraViewAngle = 30
SaveScreenshot(out, v, ImageResolution=[2400, 1450], TransparentBackground=0)
