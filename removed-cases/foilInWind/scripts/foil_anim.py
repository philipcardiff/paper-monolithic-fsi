# pvbatch foil_anim.py <dir with animFluidVTK/ and animSolidVTK/> <outdir> [<frame-index> <out.png> <width>]
# 3-D flag behind a block (foilInWind, QM, 128 ranks): perspective view of streamlines seeded
# upstream of the block (coloured by speed), translucent vortex cores (Q-criterion iso-surface)
# and the flag coloured by its displacement magnitude, its deformation magnified FOIL_MAG times
# (labelled; the flow is at true scale); the block is drawn as a grey box.
# Without the optional arguments: one frame per VTK output in outdir; with them: one image.
import sys, os, json
from paraview.simple import *
src, outdir = sys.argv[1], sys.argv[2]
single = len(sys.argv) > 3
W = int(sys.argv[5]) if single else 1920
H = int(W * 9 / 16); fs = W / 1920.0
fser = json.load(open(f"{src}/animFluidVTK/fluid/foil_qm.vtm.series"))["files"]
sser = {round(f["time"], 6): f["name"] for f in json.load(open(f"{src}/animSolidVTK/solid/foil_qm.vtm.series"))["files"]}
fl = XMLMultiBlockDataReader(FileName=[f"{src}/animFluidVTK/fluid/{fser[0]['name']}"])
so = XMLMultiBlockDataReader(FileName=[f"{src}/animSolidVTK/solid/{sser[round(fser[0]['time'], 6)]}"])
fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]; flp = CellDatatoPointData(Input=fli)
spd = Calculator(Input=flp); spd.ResultArrayName = "speed"; spd.Function = "mag(U)"
seeds = PointSource(Center=[0.035, 0.055, 0.055], Radius=0.016, NumberOfPoints=130)
st = StreamTracerWithCustomSource(Input=spd, SeedSource=seeds); st.Vectors = ["POINTS", "U"]
st.MaximumStreamlineLength = 0.25; st.IntegrationDirection = "FORWARD"
tube = Tube(Input=st); tube.Radius = 0.00012; tube.NumberofSides = 8
gr = Gradient(Input=flp); gr.ScalarArray = ["POINTS", "U"]; gr.ComputeQCriterion = 1; gr.QCriterionArrayName = "Q"
qiso = Contour(Input=gr); qiso.ContourBy = ["POINTS", "Q"]; qiso.Isosurfaces = [2000.0]
soi = ExtractBlock(Input=so); soi.Selectors = ["/Root/internal"]; sop = CellDatatoPointData(Input=soi)
dmu = Calculator(Input=sop); dmu.ResultArrayName = "Dum"; dmu.Function = "1e6*mag(D)"
MAGF = float(os.environ.get("FOIL_MAG", "200"))
flag = WarpByVector(Input=dmu); flag.Vectors = ["POINTS", "D"]; flag.ScaleFactor = MAGF
block = Box(XLength=0.01, YLength=0.01, ZLength=0.03, Center=[0.055, 0.055, 0.055])
v = CreateView("RenderView"); v.ViewSize = [W, H]; v.OrientationAxesVisibility = 0
v.UseColorPaletteForBackground = 0; v.Background = [1, 1, 1]
dt = Show(tube, v); ColorBy(dt, ("POINTS", "speed"))
lu = GetColorTransferFunction("speed"); lu.ApplyPreset("Viridis", True)
dfl = Show(flag, v); ColorBy(dfl, ("POINTS", "Dum"))
ld = GetColorTransferFunction("Dum"); ld.ApplyPreset("Reds", True); ld.InvertTransferFunction()
db = Show(block, v); db.ColorArrayName = ["POINTS", ""]; db.AmbientColor = db.DiffuseColor = [0.55, 0.55, 0.55]
DMAX = float(os.environ.get("FOIL_DMAX_UM", "0.05"))
for l, r in ((lu, (0.0, 1.4)), (ld, (0.0, DMAX))):
    l.AutomaticRescaleRangeMode = "Never"; l.RescaleTransferFunction(*r); l.Discretize = 1; l.NumberOfTableValues = 14
for l, t, pos, lb in ((lu, "Air speed (m/s)", [0.08, 0.04], [0, 0.4, 0.8, 1.2]), (ld, "Flag displacement magnitude (µm)", [0.58, 0.04], [0, DMAX / 2, DMAX])):
    sb = GetScalarBar(l, v); sb.Title = t; sb.ComponentTitle = ""; sb.Visibility = 1
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = int(22 * fs); sb.LabelFontSize = int(18 * fs)
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = pos
    sb.ScalarBarLength = 0.32; sb.AddRangeLabels = 0; sb.UseCustomLabels = 1; sb.CustomLabels = lb; sb.LabelFormat = "%-#.3g"
tt = Text(); tl = Show(tt, v); tl.WindowLocation = "Upper Left Corner"; tl.FontSize = int(22 * fs); tl.Color = [0.15, 0.15, 0.15]
mg = Text(Text=f"flag deformation magnified {int(MAGF)}\u00d7"); ml = Show(mg, v); ml.WindowLocation = "Upper Right Corner"; ml.FontSize = int(22 * fs); ml.Color = [0.15, 0.15, 0.15]
v.CameraPosition = [0.075, 0.175, 0.175]; v.CameraFocalPoint = [0.095, 0.055, 0.055]; v.CameraViewUp = [0, 0.7, -0.7]
v.CameraViewAngle = 25


def load(f):
    fl.FileName = [f"{src}/animFluidVTK/fluid/{f['name']}"]
    so.FileName = [f"{src}/animSolidVTK/solid/{sser[round(f['time'], 6)]}"]
    tt.Text = f"t = {f['time']:.3f} s"


if single:
    f = fser[int(sys.argv[3])]; load(f); tl.Visibility = 0
    SaveScreenshot(sys.argv[4], v, ImageResolution=[W, H])
    dmu.UpdatePipeline(); print("image at t =", f["time"], "Dmax um", dmu.PointData["Dum"].GetRange()[1])
else:
    os.makedirs(outdir, exist_ok=True)
    for i, f in enumerate(fser):
        load(f); SaveScreenshot(f"{outdir}/f{i:04d}.png", v, ImageResolution=[W, H])
    print("frames", len(fser))
