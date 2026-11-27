# Independent finite-element check of the compact solid block (Section 3.5.2)

`bending_eigs.py` solves the generalised eigenvalue problem (K + mM) v = θ (P + mM) v for a clamped plane-strain
strip with the collapsible-channel wall parameters (L = 10 m, E h³ fixed, ν = 0.3, ρ = 1, Δt = 0.00625 s,
m = ρ/(βΔt²), β = 4/9 as in the BDF2 finite-volume block). K is the consistent small-strain tangent (UFL
derivative of the St Venant–Kirchhoff residual at the zero state), P the compact block (2μ+λ)∇u:∇v, a
component-decoupled anisotropic block, or K itself. Output: `fenicsx_bending.csv` (θ_min, Krylov counts,
mode diagnostics, for slenderness, modulus and time-step series, element/mesh controls, and the 80×8 Q1 control).

Values quoted in the text: θ_min = 1.58e-4 (Q2, L/h = 200; mesh-independent to 5 digits), 3.15e-4 and 1.25e-4
(Q1 on the 80×8 mesh, L/h = 200 and 400). Run time about 1 min in serial (DOLFINx 0.10.0).
