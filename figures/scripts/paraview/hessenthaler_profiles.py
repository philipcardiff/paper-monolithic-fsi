# pvbatch hessenthaler_profiles.py <fluid.vtu | case> <out.csv>: Hessenthaler Phase I,
# pointwise v_z (mm/s) every 0.25 mm along y on the line x = 0 of the MRI planes
# z = 10 and 30 mm, and the average over a 1.302 x 1.302 x 6 mm MRI voxel
# (4 x 4 x 12 sub-samples) centred at each point. Input: the reconstructed fluid
# internal mesh at t = 45 s (foamToVTK -region fluid -time 45 -no-boundary
# -no-point-data), or a case with VTK/fluid/case_22500.vtm (QM rF0).
# Output columns: z_mm, y_mm, vz_point, vz_voxel; joined into
# paper-data/hessenthaler/profiles_pointwise.csv.
import sys
import numpy as np
from paraview.simple import XMLUnstructuredGridReader, XMLMultiBlockDataReader, ExtractBlock, MergeBlocks
from paraview import servermanager as sm
from vtk import vtkCellDataToPointData, vtkPoints, vtkPolyData, vtkProbeFilter
from vtk.numpy_interface import dataset_adapter as dsa
case, out = sys.argv[1], sys.argv[2]
if case.endswith(".vtu"):
    m = XMLUnstructuredGridReader(FileName=[case])
else:
    fl = XMLMultiBlockDataReader(FileName=[f"{case}/VTK/fluid/case_22500.vtm"])
    fli = ExtractBlock(Input=fl); fli.Selectors = ["/Root/internal"]
    m = MergeBlocks(Input=fli)
c2p = vtkCellDataToPointData(); c2p.SetInputData(sm.Fetch(m)); c2p.Update()


def probe(P):
    vp = vtkPoints()
    for p in P:
        vp.InsertNextPoint(*p)
    pd = vtkPolyData(); pd.SetPoints(vp)
    f = vtkProbeFilter(); f.SetInputData(pd); f.SetSourceData(c2p.GetOutput()); f.Update()
    o = dsa.WrapDataObject(f.GetOutput())
    return np.array(o.PointData["U"])[:, 2], np.array(o.PointData["vtkValidPointMask"])


ys = np.arange(-40.0, 40.0001, 0.25)
S = (4, 4, 12); SZ = (1.302e-3, 1.302e-3, 6.0e-3)
offs = [[((n + 0.5) / S[d] - 0.5) * SZ[d] for n in range(S[d])] for d in range(3)]
with open(out, "w") as h:
    h.write("z_mm,y_mm,vz_point,vz_voxel\n")
    for z in (10.0, 30.0):
        vz, ok = probe([(0.0, 1e-3 * y, 1e-3 * z) for y in ys])
        Q = [(a, 1e-3 * y + b, 1e-3 * z + c) for y in ys for a in offs[0] for b in offs[1] for c in offs[2]]
        vq, okq = probe(Q)
        vq = vq.reshape(len(ys), -1); okq = okq.reshape(len(ys), -1)
        for i, y in enumerate(ys):
            n = okq[i].sum()
            vp = f"{1e3 * vz[i]:.3f}" if ok[i] else ""
            vv = f"{1e3 * (vq[i] * okq[i]).sum() / n:.3f}" if n >= 0.5 * okq.shape[1] else ""
            h.write(f"{z:g},{y:.2f},{vp},{vv}\n")
