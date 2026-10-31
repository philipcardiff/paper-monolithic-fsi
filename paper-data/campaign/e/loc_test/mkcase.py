"""ht_smooth_case.py with the mesh from ht_mesh_local.py (env REGION, FINE)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ht_mesh_local as hl
import ht_mesh_smooth as ms
import ht_smooth_case as hc
region, fine = os.environ["REGION"], int(os.environ.get("FINE", "4"))
ms.build = lambda base, level, params=None: hl.build(base, level, fine, hl.REGIONS[region], params)[0]
sys.exit(hc.main())
