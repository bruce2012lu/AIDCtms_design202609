import os
import h5py
import numpy as np

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cas = os.path.join(root, "fluent", "uc01b_cht_less_12y_i600.cas.h5")
with h5py.File(cas, "r") as fc:
    ds = fc["meshes/1/nodes/coords/1"]
    near = []
    n = ds.shape[0]
    for i0 in range(0, n, 2_000_000):
        block = np.asarray(ds[i0 : i0 + 2_000_000, 2], np.float64)
        m = (block > -0.00008) & (block < 0.00008)
        if np.any(m):
            near.append(block[m])
uniq = np.unique(np.round(np.concatenate(near), 7))
for z in uniq:
    print("%.7f m   %.4f mm" % (z, z * 1000))
