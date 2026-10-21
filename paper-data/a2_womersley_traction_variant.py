"""Exact Womersley-tube solution with the full Cauchy traction (reference)
and with the Laplacian-form traction -p n + mu dU/dn (newtonIcoFluid's
patchViscousForce), to predict the monolithic-minus-partitioned offset.

Usage (needs numpy only):
    git -C <solids4foam> show 257b2e564:tutorials/fluidSolidInteraction/\
womersleyTube/verification/scripts/womersley_exact.py > /tmp/x/womersley_exact.py
    python3 -I a2_womersley_traction_variant.py /tmp/x/womersley_exact.py

The output is quoted in a2_discretisation_differences.md (section B1).
It is a travelling-wave estimate: the tutorial imposes the full-traction
exact solution at both tube ends, which this estimate does not model."""
import cmath, math, sys, importlib.util
import numpy as np
spec = importlib.util.spec_from_file_location("we", sys.argv[1])
we = importlib.util.module_from_spec(spec); spec.loader.exec_module(we)

class LapTube(we.Tube):
    def __init__(self, prm, normal=True, shear=True, **kw):
        super().__init__(prm, **kw); self.dn, self.ds = normal, shear
    def fluid_rows(self, k, r):
        f = super().fluid_rows(k, r)
        # Full: srr = -p + 2 mu dur ; srx = mu (dux - i k ur)
        # Laplacian form drops mu*dur (normal) and mu*(-i k ur) (shear)
        w, rho, mu, s = self.omega, self.rho, self.mu, self.s(k)
        I0k, I1k = we.bessel(0, k*r, True), we.bessel(1, k*r, True)
        I0s, I1s = we.bessel(0, s*r, True), we.bessel(1, s*r, True)
        dI1k, dI1s = I0k - I1k/(k*r), I0s - I1s/(s*r)
        dur = np.array([1j*k*k/(rho*w)*dI1k, 1j*k*dI1s])
        if self.dn: f["srr"] = f["srr"] - mu*dur
        if self.ds: f["srx"] = f["srx"] + mu*1j*k*f["ur"]
        return f

P = we.PARAMETERS
L = P["length"]
def summary(t):
    k = t.solve()
    out = {"k": k, "Q0": t.flow_rate()}
    for name, x in (("L4", L/4), ("L2", L/2), ("3L4", 3*L/4), ("0", 0.0)):
        ph = cmath.exp(-1j*k*x)
        out["ur_"+name] = complex(t.U[-1])*ph
        out["ux_"+name] = complex(t.W[-1])*ph
    return out
ref = summary(we.Tube(P))
for label, kw in (("normal+shear", {}), ("normal only", {"shear": False}),
                  ("shear only", {"normal": False})):
    m = summary(LapTube(P, **kw))
    print(f"== Laplacian-form traction ({label}) minus full traction, relative")
    print(f"  k: real {m['k'].real/ref['k'].real-1:+.3e}  imag {m['k'].imag/ref['k'].imag-1:+.3e}")
    for name in ("0", "L4", "L2", "3L4"):
        a, b = m["ur_"+name], ref["ur_"+name]
        c, d = m["ux_"+name], ref["ux_"+name]
        print(f"  x={name:>3}: radial amp {abs(a)/abs(b)-1:+.3e} phase {cmath.phase(a/b):+.3e} rad;"
              f" axial amp {abs(c)/abs(d)-1:+.3e} phase {cmath.phase(c/d):+.3e} rad")
    print(f"  flow rate at x=0: amp {abs(m['Q0'])/abs(ref['Q0'])-1:+.3e}")
print("reference |ur(0)|, |ux(0)|:", abs(ref["ur_0"]), abs(ref["ux_0"]), "k", ref["k"])
