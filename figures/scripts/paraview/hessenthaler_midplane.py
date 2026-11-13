# pvbatch hv_midplane.py <case> <rF1meshcase> <outA.png> <outB.png>
# (a) |U| on the plane x = 0.3 mm at t = 45 s (QM rF0) with the deformed flap
#     (coloured by |D|) and its undeformed outline; (b) the rF1 mesh on the same
#     plane near the flap, with the undeformed flap outline.
import sys
from paraview.simple import *
case, mcase, outA, outB = sys.argv[1:5]
X0 = 0.0003
def plane(src):
    s = Slice(Input=src); s.SliceType = "Plane"; s.SliceType.Origin = [X0, 0, 0]; s.SliceType.Normal = [1, 0, 0]
    try: s.Triangulatetheslice = 0
    except Exception: pass
    return s
def view(size):
    v = CreateView("RenderView"); v.ViewSize = size; v.OrientationAxesVisibility = 0
    v.Background = [1, 1, 1]; v.UseColorPaletteForBackground = 0
    v.CameraParallelProjection = 1; v.CameraViewUp = [0, 1, 0]
    return v
def bar(l, v, title, labs, pos, length=0.30):
    sb = GetScalarBar(l, v); sb.Title = title; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 30; sb.LabelFontSize = 26
    sb.Orientation = "Horizontal"; sb.AddRangeLabels = 0; sb.WindowLocation = "Any Location"; sb.ScalarBarLength = length
    sb.UseCustomLabels = 1; sb.CustomLabels = labs; sb.LabelFormat = "%-#.2g"; sb.Position = pos
fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/case_22500.vtm"])
so = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/solid/case_22500.vtm"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]
# undeformed flap outline on the plane (reference configuration of the solid)
undsl = plane(soi); undo = FeatureEdges(Input=ExtractSurface(Input=undsl)); undo.FeatureEdges = 0; undo.NonManifoldEdges = 0; undo.ManifoldEdges = 0
sop = CellDatatoPointData(Input=soi)
warp = WarpByVector(Input=sop); warp.Vectors = ["POINTS", "pointD"]; warp.ScaleFactor = 1.0
dmm = Calculator(Input=warp); dmm.AttributeType = "Point Data"; dmm.ResultArrayName = "Dmm"; dmm.Function = "mag(pointD)*1000"
dsl = plane(dmm)
fsl = plane(CellDatatoPointData(Input=fli))
clipz = Clip(Input=fsl); clipz.ClipType = "Plane"; clipz.ClipType.Origin = [0, 0, 0.16]; clipz.ClipType.Normal = [0, 0, 1]; clipz.Invert = 1
# (a)
va = view([2400, 1300])
da = Show(clipz, va); ColorBy(da, ("POINTS", "U", "Magnitude"))
lu = GetColorTransferFunction("U"); lu.ApplyPreset("Viridis", True); lu.AutomaticRescaleRangeMode = "Never"; lu.RescaleTransferFunction(0.0, 0.63)
lu.Discretize = 1; lu.NumberOfTableValues = 14
ds = Show(dsl, va); ColorBy(ds, ("POINTS", "Dmm"))
ld = GetColorTransferFunction("Dmm"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction(); ld.AutomaticRescaleRangeMode = "Never"; ld.RescaleTransferFunction(0.0, 16.2)
ld.Discretize = 1; ld.NumberOfTableValues = 12
# in-plane streamlines in the slow central region (white)
sls = []
for z, n in ((0.012, 16), (0.050, 18), (0.110, 18)):
    st = StreamTracer(Input=clipz, SeedType="Line"); st.Vectors = ["POINTS", "U"]
    st.SeedType.Point1 = [X0, -0.0155, z]; st.SeedType.Point2 = [X0, 0.0155, z]; st.SeedType.Resolution = n
    st.SurfaceStreamlines = 1; st.IntegrationDirection = "BOTH"; st.MaximumStreamlineLength = 0.5; st.MaximumSteps = 20000
    sls.append(st)
sl = AppendDatasets(Input=sls)
dsl2 = Show(sl, va); dsl2.ColorArrayName = ["POINTS", ""]; dsl2.AmbientColor = dsl2.DiffuseColor = [1, 1, 1]; dsl2.LineWidth = 1.6; dsl2.Opacity = 0.85
du = Show(undo, va); du.ColorArrayName = ["POINTS", ""]; du.AmbientColor = du.DiffuseColor = [0, 0, 0]; du.LineWidth = 3
bar(lu, va, "Fluid velocity magnitude (m/s)", [0, 0.2, 0.4, 0.6], [0.12, 0.03])
bar(ld, va, "Flap displacement magnitude (mm)", [0, 4, 8, 12, 16], [0.58, 0.03])
va.CameraPosition = [-1.0, 0.0, 0.065]; va.CameraFocalPoint = [0.0, 0.0, 0.065]; va.CameraViewUp = [0, 1, 0]
va.CameraParallelScale = 0.052
SaveScreenshot(outA, va, ImageResolution=[2400, 1300], TransparentBackground=0)
# (b) rF1 mesh near the flap
mr = XMLMultiBlockDataReader(FileName=[f"{mcase}/VTK/rF1mesh_0.vtm"])
mi = ExtractBlock(Input=mr); mi.Selectors = ["/Root/internal"]
ms = plane(mi)
vb = view([2400, 1300])
dm = Show(ms, vb); dm.Representation = "Wireframe"; dm.ColorArrayName = ["POINTS", ""]
dm.AmbientColor = dm.DiffuseColor = [0.25, 0.25, 0.30]; dm.LineWidth = 1.0
du2 = Show(undo, vb); du2.ColorArrayName = ["POINTS", ""]; du2.AmbientColor = du2.DiffuseColor = [0.8, 0.1, 0.1]; du2.LineWidth = 4
vb.CameraPosition = [-1.0, 0.004, 0.036]; vb.CameraFocalPoint = [0.0, 0.004, 0.036]; vb.CameraViewUp = [0, 1, 0]
vb.CameraParallelScale = 0.022
SaveScreenshot(outB, vb, ImageResolution=[2400, 1300], TransparentBackground=0)
