"""qm_post.py with the 3dTube time-spacing tolerance relaxed from 1e-3 to
1e-2 (solids4foam#641: 6-digit times resolve L3 spacings only to ~0.8%)."""
import importlib.util, math, sys, types
S = "/project/home/p201287/philip/qm-final/runs/r4r5-scripts/scripts/qm_post.py"
spec = importlib.util.spec_from_file_location("qm_post", S)
qp = importlib.util.module_from_spec(spec); sys.modules["qm_post"] = qp
spec.loader.exec_module(qp)
shim = types.SimpleNamespace(**{k: getattr(math, k) for k in dir(math) if not k.startswith("_")})
def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
    return math.isclose(a, b, rel_tol=1e-2 if rel_tol == 1e-3 else rel_tol, abs_tol=abs_tol)
shim.isclose = isclose
orig = qp.load
def load(name, path):
    m = orig(name, path)
    if name == "tube_drv": m.math = shim
    return m
qp.load = load
sys.argv = [S] + sys.argv[1:]
qp.main() if hasattr(qp, "main") else None
