import os
import h5py
import numpy as np

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cas = os.path.join(root, "fluent", "uc01b_cht_less_12y_i600.cas.h5")
if not os.path.isfile(cas):
    cas = os.path.join(root, "fluent", "uc01b_cht_less_12y_i300.cas.h5")
print("cas", cas)
with h5py.File(cas, "r") as fc:
    ds = fc["meshes/1/nodes/coords/1"]
    print("shape", ds.shape, "dtype", ds.dtype)
    # z is the last component. Read in chunks and keep values near the interface.
    near = []
    step = 2_000_000
    n = ds.shape[0]
    for i0 in range(0, n, step):
        block = np.asarray(ds[i0 : i0 + step, 2], np.float64)
        m = (block > -0.00215) & (block < -0.00170)
        if np.any(m):
            near.append(block[m])
        print("chunk", i0, flush=True)
vals = np.concatenate(near)
uniq = np.unique(np.round(vals, 7))
print("unique near interface", uniq.size)
for z in uniq:
    print("%.7f mm %.4f" % (z, z * 1000))
