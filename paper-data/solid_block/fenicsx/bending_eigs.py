"""Independent FE (DOLFINx) check of the slender-solid preconditioner mechanism (report 22).

Generalised eigenproblem  (K + m M) v = theta (P + m M) v  on a clamped-clamped strip, with
  K  : small-strain linear elasticity, obtained as ufl.derivative of the St Venant-Kirchhoff residual
       at the zero state (identical to linear elasticity there),
  P  : candidate preconditioner block:
         'P0'   (2mu+lam) inner(grad u, grad v)              (paper's compact component-wise Laplacian)
         'P2a'  component-decoupled anisotropic block: diagonal blocks of K
                (u_x: (2mu+lam) d_xx + mu d_yy ; u_y: mu d_xx + (2mu+lam) d_yy), no cross terms
         'K'    the consistent operator itself (sanity: theta == 1)
  M  : rho inner(u, v);  m = rho / (beta dt^2) with beta = 4/9, i.e. the FV block
       (2dt/3) K + (3/(2dt)) rho M multiplied by 3/(2dt)  (BDF2, constant step).
Clamping (both components) at x = 0 and x = L; traction-free long sides. Plane strain in 2-D.

Run only through the wrapper:
  (in a DOLFINx 0.10 environment; tested with DOLFINx 0.10.0, UFL 2025.2.1, petsc4py 3.25)
  python3 bending_eigs.py   [writes fenicsx_bending.csv/.json next to this script]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from mpi4py import MPI

import basix.ufl
import dolfinx
import ufl
from dolfinx import fem, mesh

ROOT = Path(__file__).resolve().parent
TAB = ROOT

# collapsible-channel wall (tutorial / paper): L = 10 m, h = 0.05 m, E = 4.55e8 Pa, nu = 0.3, rho = 1, dt = 0.00625 s
L0, H0, E0, NU, RHO, DT0 = 10.0, 0.05, 4.55e8, 0.3, 1.0, 0.00625
BETA = 4.0 / 9.0


def lame(E, nu):
    return E * nu / ((1 + nu) * (1 - 2 * nu)), E / (2 * (1 + nu))


def build(L, h, E, nu, rho, dt, nx, ny, degree=2, dim=2, width=None, nz=None, cell="quad"):
    lam, mu = lame(E, nu)
    m = rho / (BETA * dt ** 2)
    comm = MPI.COMM_SELF
    if dim == 2:
        ct = mesh.CellType.quadrilateral if cell == "quad" else mesh.CellType.triangle
        msh = mesh.create_rectangle(comm, [[0.0, 0.0], [L, h]], [nx, ny], ct)
    else:
        msh = mesh.create_box(comm, [[0.0, 0.0, 0.0], [L, width, h]], [nx, nz, ny], mesh.CellType.hexahedron)
    gdim = msh.geometry.dim
    el = basix.ufl.element("Lagrange", msh.basix_cell(), degree, shape=(gdim,))
    V = fem.functionspace(msh, el)
    u, v = ufl.TrialFunction(V), ufl.TestFunction(V)
    w = fem.Function(V)  # state (zero): K = dR/dw at w = 0 (SVK == linear elasticity there)
    I = ufl.Identity(gdim)
    F = I + ufl.grad(w)
    Egl = 0.5 * (F.T * F - I)
    S = lam * ufl.tr(Egl) * I + 2 * mu * Egl
    R = ufl.inner(F * S, ufl.grad(v)) * ufl.dx
    aK = ufl.derivative(R, w, u)
    aP0 = (2 * mu + lam) * ufl.inner(ufl.grad(u), ufl.grad(v)) * ufl.dx
    # component-decoupled anisotropic block: keep only d u_i / d x_j * d v_i / d x_j terms of K
    Kbar = 2 * mu + lam
    terms = []
    for i in range(gdim):
        for j in range(gdim):
            c = Kbar if i == j else mu
            terms.append(c * u[i].dx(j) * v[i].dx(j))
    aP2a = sum(terms) * ufl.dx
    aM = rho * ufl.inner(u, v) * ufl.dx

    def asm(a):
        A = fem.assemble_matrix(fem.form(a))
        return A.to_scipy().tocsr()

    mats = {"K": asm(aK), "P0": asm(aP0), "P2a": asm(aP2a), "M": asm(aM)}
    bs = V.dofmap.index_map_bs
    clamp = fem.locate_dofs_geometrical(V, lambda x: np.isclose(x[0], 0.0) | np.isclose(x[0], L))
    cl = np.concatenate([clamp * bs + c for c in range(bs)])
    n = mats["M"].shape[0]
    free = np.setdiff1d(np.arange(n), cl)
    for k in mats:
        mats[k] = mats[k][free][:, free].tocsc()
    X = V.tabulate_dof_coordinates()  # per block
    return dict(mats=mats, m=m, free=free, bs=bs, X=X, ndof=len(free), lam=lam, mu=mu, V=V, msh=msh)


def smallest_theta(Kc, Pc, M, m, k=6):
    A = (Kc + m * M).tocsc()
    B = (Pc + m * M).tocsc()
    # shift-invert at sigma = 0: largest of A^{-1} B  <=> smallest theta of A v = theta B v
    vals, vecs = spla.eigsh(A, k=k, M=B, sigma=0.0, which="LM", tol=1e-10)
    idx = np.argsort(vals)
    return vals[idx], vecs[:, idx]


def mode_metrics(vec, d, h):
    bs, free, X = d["bs"], d["free"], d["X"]
    n = len(X) * bs
    full = np.zeros(n)
    full[free] = vec
    U = full.reshape(-1, bs)
    ux, uy = U[:, 0], U[:, bs - 1]  # transverse = last coordinate direction (y in 2-D, z in 3-D)
    t = X[:, bs - 1]
    s = X[:, 0]
    Mfull = None
    frac_uy = float(np.sum(uy ** 2) / np.sum(U ** 2))  # nodal l2 (quick, Q2 nodes uniform)
    # through-thickness variation of the transverse displacement, per x-station
    key = np.round(s / (h * 1e-6)).astype(np.int64)
    if bs == 3:
        key = key * 100003 + np.round(X[:, 1] / (h * 1e-6)).astype(np.int64)
    order = np.argsort(key)
    ks, starts = np.unique(key[order], return_index=True)
    var = 0.0
    anti = 0.0
    nrm = 0.0
    umax = np.max(np.abs(uy))
    for a, b in zip(starts, list(starts[1:]) + [len(order)]):
        ids = order[a:b]
        var = max(var, np.ptp(uy[ids]) / umax)
        # antisymmetry of u_x about mid-thickness: pair t with h - t
        tt = t[ids]
        o = np.argsort(tt)
        uxs = ux[ids][o]
        anti += np.sum((uxs + uxs[::-1]) ** 2)
        nrm += np.sum(uxs ** 2)
    return dict(uy_fraction=frac_uy, uy_thickness_variation=float(var),
                ux_antisymmetry_residual=float(np.sqrt(anti / max(nrm, 1e-300))))


def beam_model(L, h, E, nu, rho, dt, ne=400):
    """1-D Euler-Bernoulli reduction of the same pair (Hermite cubic FE, clamped w = w' = 0).
    Displacement u = (-y w', w) (y from mid-thickness), per unit width:
      elastic  a_K = E' h^3/12 int w''^2            (plane strain E' = E/(1-nu^2))
      Laplacian a_P = Kbar [ 2 h int w'^2 + h^3/12 int w''^2 ]   (|grad u|^2 = y^2 w''^2 + 2 w'^2)
      mass     m [ h int w^2 + h^3/12 int w'^2 ]
    Returns the smallest theta of (a_K + mass, a_P + mass)."""
    lam, mu = lame(E, nu)
    Kb, Ep, m = 2 * mu + lam, E / (1 - nu ** 2), rho / (BETA * dt ** 2)
    le = L / ne
    xi, wq = np.polynomial.legendre.leggauss(6)

    def herm(x):  # x in [0,1]; shape funcs N, dN/ds, d2N/ds2 wrt physical s
        N = np.array([1 - 3 * x ** 2 + 2 * x ** 3, le * (x - 2 * x ** 2 + x ** 3), 3 * x ** 2 - 2 * x ** 3, le * (-x ** 2 + x ** 3)])
        dN = np.array([-6 * x + 6 * x ** 2, le * (1 - 4 * x + 3 * x ** 2), 6 * x - 6 * x ** 2, le * (-2 * x + 3 * x ** 2)]) / le
        d2 = np.array([-6 + 12 * x, le * (-4 + 6 * x), 6 - 12 * x, le * (-2 + 6 * x)]) / le ** 2
        return N, dN, d2
    m0 = np.zeros((4, 4)); m1 = np.zeros((4, 4)); m2 = np.zeros((4, 4))
    for q, wt in zip(xi, wq):
        x = 0.5 * (q + 1)
        N, dN, d2 = herm(x)
        m0 += 0.5 * wt * le * np.outer(N, N)
        m1 += 0.5 * wt * le * np.outer(dN, dN)
        m2 += 0.5 * wt * le * np.outer(d2, d2)
    nd = 2 * (ne + 1)
    G0 = np.zeros((nd, nd)); G1 = np.zeros((nd, nd)); G2 = np.zeros((nd, nd))
    for e in range(ne):
        ids = np.arange(2 * e, 2 * e + 4)
        G0[np.ix_(ids, ids)] += m0; G1[np.ix_(ids, ids)] += m1; G2[np.ix_(ids, ids)] += m2
    keep = np.arange(2, nd - 2)
    G0, G1, G2 = (G[np.ix_(keep, keep)] for G in (G0, G1, G2))
    Ms = m * (h * G0 + h ** 3 / 12 * G1)
    A = Ep * h ** 3 / 12 * G2 + Ms
    B = Kb * (2 * h * G1 + h ** 3 / 12 * G2) + Ms
    import scipy.linalg as sl
    return float(sl.eigh(A, B, eigvals_only=True, subset_by_index=[0, 0])[0])


def closed_form(L, h, E, nu, rho, dt):
    """theta(k) = (m + E' h^2 k^4/12) / (m + 2 Kbar k^2), minimised over k >= 2 pi / L (wavenumber)."""
    lam, mu = lame(E, nu)
    Kb, Ep, m = 2 * mu + lam, E / (1 - nu ** 2), rho / (BETA * dt ** 2)
    k = np.geomspace(2 * np.pi / L, 1e3 / h, 20000)
    th = (m + Ep * h ** 2 * k ** 4 / 12) / (m + 2 * Kb * k ** 2)
    return float(th.min())


def report03_model(L, h, E, nu, rho, dt):
    """Estimate of report 03 sec. 3: (Pi + lam_K)/(Pi + 1), Pi = 9 rho l^2/(16 pi^2 Kbar dt^2),
    lam_K = E' pi^2 h^2/(3 Kbar l^2), minimised over wavelength l <= L (Laplacian energy of u_y only)."""
    lam, mu = lame(E, nu)
    Kb, Ep = 2 * mu + lam, E / (1 - nu ** 2)
    l = np.geomspace(h * 1e-2, L, 20000)
    Pi = 9 * rho * l ** 2 / (16 * np.pi ** 2 * Kb * dt ** 2)
    lk = Ep * np.pi ** 2 * h ** 2 / (3 * Kb * l ** 2)
    return float(((Pi + lk) / (Pi + 1)).min())


def twist_fraction(vec, d, W):
    """3-D: fraction (nodal l2) of the transverse displacement u_z that is odd across the width (twist)."""
    bs, free, X = d["bs"], d["free"], d["X"]
    full = np.zeros(len(X) * bs); full[free] = vec
    uz = full.reshape(-1, bs)[:, 2]
    key = lambda y: np.round(np.c_[X[:, 0], y, X[:, 2]] * 1e6).astype(np.int64)
    idx = {tuple(k): i for i, k in enumerate(key(X[:, 1]))}
    mirror = np.array([idx[tuple(k)] for k in key(W - X[:, 1])])
    odd = 0.5 * (uz - uz[mirror])
    return float(np.sum(odd ** 2) / np.sum(uz ** 2))


def pcg_iters(A, Pfac, b, rtol=1e-6, maxit=5000):
    """Preconditioned CG, relative preconditioned-residual-independent test on ||r||_2/||b||_2."""
    x = np.zeros_like(b); r = b.copy(); z = Pfac(r); p = z.copy(); rz = r @ z; nb = np.linalg.norm(b)
    for it in range(1, maxit + 1):
        Ap = A @ p; a = rz / (p @ Ap); x += a * p; r -= a * Ap
        if np.linalg.norm(r) / nb < rtol:
            return it
        z = Pfac(r); rz2 = r @ z; p = z + (rz2 / rz) * p; rz = rz2
    return maxit


def gmres_iters(A, Pfac, b, rtol=1e-6, maxit=3000):
    """Unrestarted right-preconditioned GMRES (A P^-1 y = b, x = P^-1 y), modified Gram-Schmidt;
    stops when the Arnoldi residual (= true residual ||b - A x|| for right preconditioning) < rtol ||b||.
    Same protocol as the FV solid-only study (report 03: right, exact LU of the candidate, 1e-6, random rhs)."""
    n = len(b); beta = np.linalg.norm(b)
    Vb = np.zeros((maxit + 1, n)); H = np.zeros((maxit + 1, maxit))
    cs = np.zeros(maxit); sn = np.zeros(maxit); g = np.zeros(maxit + 1); g[0] = beta
    Vb[0] = b / beta
    for j in range(maxit):
        w = A @ Pfac(Vb[j])
        for i in range(j + 1):
            H[i, j] = w @ Vb[i]; w -= H[i, j] * Vb[i]
        H[j + 1, j] = np.linalg.norm(w)
        if H[j + 1, j] > 0:
            Vb[j + 1] = w / H[j + 1, j]
        for i in range(j):
            t = cs[i] * H[i, j] + sn[i] * H[i + 1, j]
            H[i + 1, j] = -sn[i] * H[i, j] + cs[i] * H[i + 1, j]; H[i, j] = t
        r = np.hypot(H[j, j], H[j + 1, j]); cs[j] = H[j, j] / r; sn[j] = H[j + 1, j] / r
        H[j, j] = r; H[j + 1, j] = 0.0
        g[j + 1] = -sn[j] * g[j]; g[j] = cs[j] * g[j]
        if abs(g[j + 1]) < rtol * beta:
            return j + 1
    return maxit


def case(tag, L=L0, h=H0, E=E0, dt=DT0, ny=4, aspect=4.0, degree=2, krylov=False, dim=2, width=None, nz=None,
         cell="quad", nx=None, keep_vec=False, mzero=False):
    t0 = time.time()
    if nx is None:
        nx = max(int(round((L / h) * ny / aspect)), 40)
    d = build(L, h, E, NU, RHO, dt, nx, ny, degree, dim, width, nz, cell)
    M, m = d["mats"]["M"], d["m"]
    res = dict(tag=tag, dim=dim, L=L, h=h, L_over_h=L / h, E=E, nu=NU, rho=RHO, dt=dt, m=m, nx=nx, ny=ny, nz=nz,
               width=width, degree=degree, cell=cell, ndof=d["ndof"])
    lam, mu = d["lam"], d["mu"]
    Kb = 2 * mu + lam
    res["Pi_L"] = m * L ** 2 / (2 * Kb * (2 * np.pi) ** 2)  # m / (2 Kbar k^2), k = 2 pi / L
    for P in ("P0", "P2a", "K"):
        th, V = smallest_theta(d["mats"]["K"], d["mats"][P], M, m, k=6 if P != "K" else 2)
        res[f"theta_{P}"] = th.tolist()
        if P == "P0":
            res["modes_P0"] = [mode_metrics(V[:, i], d, h) for i in range(len(th))]
            if keep_vec:
                res["_vec"] = V[:, 0]; res["_d"] = d
        if mzero and P == "P0":
            thk, _ = smallest_theta(d["mats"]["K"], d["mats"][P], M, 0.0, k=1)
            res["theta_P0_static"] = float(thk[0])
    res["theta_min_P0"] = res["theta_P0"][0]
    res["kappa_proxy_P0"] = 1.0 / res["theta_P0"][0]
    res["beam_model"] = beam_model(L, h, E, NU, RHO, dt) if dim == 2 else None
    res["closed_form"] = closed_form(L, h, E, NU, RHO, dt)
    res["report03_model"] = report03_model(L, h, E, NU, RHO, dt)
    if dim == 3:
        res["mode1_twist_fraction"] = twist_fraction(res.get("_vec") if keep_vec else
                                                     smallest_theta(d["mats"]["K"], d["mats"]["P0"], M, m, k=1)[1][:, 0],
                                                     d, width)
    if krylov:
        A = (d["mats"]["K"] + m * M).tocsc()
        rng = np.random.default_rng(1)
        b = rng.standard_normal(A.shape[0])
        kr = {}
        for P in ("P0", "P2a", "K"):
            lu = spla.splu((d["mats"][P] + m * M).tocsc())
            kr[P] = dict(pcg=pcg_iters(A, lu.solve, b), gmres=gmres_iters(A, lu.solve, b))
        res["krylov_rtol1e-6"] = kr
    res["runtime_s"] = time.time() - t0
    print(f"{tag:22s} L/h={L/h:6.1f} ndof={d['ndof']:7d} thP0={res['theta_P0'][0]:.3e} "
          f"thP2a={res['theta_P2a'][0]:.3e} thK={res['theta_K'][0]:.6f} beam={res['beam_model']} "
          f"cf={res['closed_form']:.3e} {res.get('krylov_rtol1e-6','')} {res['runtime_s']:.1f}s", flush=True)
    return res


def main():
    out = dict(meta=dict(dolfinx=dolfinx.__version__, ufl=ufl.__version__, basix=basix.__version__,
                         petsc4py=__import__("petsc4py").__version__, scipy=__import__("scipy").__version__,
                         numpy=np.__version__, beta=BETA, m_def="rho/(beta dt^2), beta=4/9",
                         base=dict(L=L0, h=H0, E=E0, nu=NU, rho=RHO, dt=DT0),
                         cmd=" ".join(sys.argv)), cases=[])
    C = out["cases"]
    # 1. slenderness at fixed L, E h^3 fixed (FV series A), 4 Q2 cells through thickness, cell aspect 4
    for s in (12.5, 25, 50, 100, 200, 400):
        h = L0 / s
        C.append(case(f"slender_{s:g}", h=h, E=E0 * (H0 / h) ** 3, krylov=True, mzero=True))
    # 2. stiffness at the paper wall
    for f in (1 / 8, 1 / 4, 1 / 2, 2, 4, 8):
        C.append(case(f"E_x{f:g}", E=E0 * f, krylov=(f in (1 / 8, 8))))
    # 3. time step
    for f in (1 / 4, 1 / 2, 2, 4):
        C.append(case(f"dt_x{f:g}", dt=DT0 * f, krylov=(f in (1 / 4, 4))))
    # 4. mesh refinement at L/h = 200 (paper wall) and L/h = 50: ny = 4, 8, 16 at fixed aspect; Q1 comparison
    for ny in (8, 16):
        C.append(case(f"refine_ny{ny}", ny=ny))
    C.append(case("refine_ny4_aspect1", ny=4, aspect=1.0))
    C.append(case("Q1_ny8_aspect1", ny=8, aspect=1.0, degree=1))
    C.append(case("P2tri_ny4", ny=4, cell="tri"))
    # 4b. the FV study's coarse wall mesh (80 x 8 cells for every h, cell aspect up to 40): Q1 (low order,
    #     shear-locking-prone like a low-order FV gradient) and Q2 on exactly that mesh
    for s in (50, 100, 200, 400):
        h = L0 / s
        for deg in (1, 2):
            C.append(case(f"fvmesh80x8_Q{deg}_{s:g}", h=h, E=E0 * (H0 / h) ** 3, nx=80, ny=8, degree=deg,
                          krylov=(deg == 1)))
    # 5. 3-D thin strip, L/h = 50 (width 1 m, 4 Q2 hexes through thickness, aspect 4), plane-strain-free
    h3 = 0.2
    C.append(case("3D_strip_Lh50", h=h3, E=E0 * (H0 / h3) ** 3, dim=3, width=1.0, nz=4, ny=4, krylov=True))
    for c in C:
        c.pop("_vec", None); c.pop("_d", None)
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / "fenicsx_bending.json").write_text(json.dumps(out, indent=1))
    cols = ["tag", "dim", "L_over_h", "h", "E", "dt", "nx", "ny", "degree", "cell", "ndof", "Pi_L", "theta_min_P0",
            "kappa_proxy_P0", "beam_model", "closed_form", "report03_model", "theta_P2a_min", "theta_K_min", "theta_P0_static",
            "pcg_P0", "pcg_P2a", "pcg_K", "gmres_P0", "gmres_P2a", "gmres_K", "mode1_uy_fraction",
            "mode1_uy_thickness_variation", "mode1_ux_antisymmetry_residual", "runtime_s"]
    with open(TAB / "fenicsx_bending.csv", "w") as f:
        f.write(",".join(cols) + "\n")
        for c in C:
            kr = c.get("krylov_rtol1e-6", {})
            row = dict(c, theta_P2a_min=c["theta_P2a"][0], theta_K_min=c["theta_K"][0],
                       mode1_uy_fraction=c["modes_P0"][0]["uy_fraction"],
                       mode1_uy_thickness_variation=c["modes_P0"][0]["uy_thickness_variation"],
                       mode1_ux_antisymmetry_residual=c["modes_P0"][0]["ux_antisymmetry_residual"],
                       **{f"{s}_{P}": kr.get(P, {}).get(s, "") for P in ("P0", "P2a", "K") for s in ("pcg", "gmres")})
            f.write(",".join("" if row.get(k) is None else (f"{row[k]:.6g}" if isinstance(row.get(k), float) else str(row.get(k, ""))) for k in cols) + "\n")


if __name__ == "__main__":
    main()
