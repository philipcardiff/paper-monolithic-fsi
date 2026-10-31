"""cavityFlexibleBottom QM with interpolate(U) linear on L2-L4, build a421f063d:
the R-fix definitions (tutorial schemes, as Table tab:cavity_m) with only the
continuity-flux interpolation changed; L4 on 8 ranks (not a timing run)."""
import importlib.util, sys
P = "/project/home/p201287/philip/qm-head/campaign/ma/ma_run.py"
spec = importlib.util.spec_from_file_location("ma_run", P)
ma = importlib.util.module_from_spec(spec); sys.modules["ma_run"] = ma
spec.loader.exec_module(ma)
rf = {r["id"]: r for r in ma.definitionsRfix()}
runs = []
for lvl in (2, 3, 4):
    r = dict(rf[f"rf-cav-qm-L{lvl}"])
    r.update(id=f"lin-cav-qm-L{lvl}", interp="linear", item="2b a421",
             ranks=8 if lvl == 4 else 1)
    runs.append(r)
ma.definitions = lambda: runs
ma.main()
