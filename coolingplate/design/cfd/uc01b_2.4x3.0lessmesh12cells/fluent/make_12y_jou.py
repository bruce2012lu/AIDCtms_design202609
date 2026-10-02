# -*- coding: utf-8 -*-
"""Write the 12-cell GPU journal. Does not launch Fluent."""
from pathlib import Path

FLU = Path(__file__).resolve().parent
ROOT = FLU.parent
BASE = "D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd/uc01b_2.4x3.0lessmesh12cells"
L = []
a = L.append
a("; 12-cell less mesh, single precision, GPU. n_bl=7. Y joins are mesh interfaces.")
a("; Each inlet_jet_XX is one hole, 1.225e-4 kg/s. wall_heat 579282 W/m2.")
a("; Y ends: fluid pressure-outlet, solid adiabatic. return_slot (Z) is an adiabatic wall.")
a("; Save iterations 300, 400, 500, 600, 1000.")
a("/file/set-batch-options yes yes no")
a("/file/confirm-overwrite yes")
a(f'/file/start-transcript "{BASE}/logs/fluent_cht_less_12y_cpu_init.log"')
a(f'/file/read-case "{BASE}/mesh/uc01b_cht_less_12y.msh"')
a("/mesh/check")
a("/define/boundary-conditions/list-zones")
a("/define/boundary-conditions/zone-type interior interior")
for i in range(1, 13):
    a(f"/define/boundary-conditions/zone-type inlet_jet_{i:02d} mass-flow-inlet")
a("/define/boundary-conditions/zone-type return_slot wall")
a("/define/boundary-conditions/zone-type return_slot:096 wall")
a("/define/boundary-conditions/zone-type outlet_y_front pressure-outlet")
a("/define/boundary-conditions/zone-type outlet_y_back pressure-outlet")
a("/define/boundary-conditions/zone-type wall_y_front wall")
a("/define/boundary-conditions/zone-type wall_y_back wall")
a("/define/boundary-conditions/zone-type SYM symmetry")
for j in range(1, 12):
    for tag in ("ifl", "icu", "itm"):
        a(f"/define/boundary-conditions/zone-type {tag}_{j:02d}a interface")
        a(f"/define/boundary-conditions/zone-type {tag}_{j:02d}b interface")
for j in range(1, 12):
    for tag in ("ifl", "icu", "itm"):
        a("/define/mesh-interfaces/create")
        a(f"{tag}-{j:02d}")
        a("no")
        a(f"{tag}_{j:02d}a")
        a(f"{tag}_{j:02d}b")
        a("()")
        a("()")
a("/define/models/energy yes")
for _ in range(4):
    a("no")
a("/define/models/viscous/kw-sst yes")
a("/define/materials/copy fluid water-liquid")
a("/define/materials/copy solid copper")
a("""/define/materials/change-create
water-liquid
water-liquid
yes
constant
992.2
yes
constant
4179
yes
constant
0.631
yes
constant
6.53e-4
no
no
no
/define/materials/change-create
copper
copper
yes
constant
8960
yes
constant
385
yes
constant
390
/define/materials/change-create
aluminum
tim2
yes
constant
2800
yes
constant
1000
yes
constant
8.818342
yes
/define/boundary-conditions/fluid
fluid
yes
water-liquid
no
no
no
no
0
no
0
no
0
no
0
no
0
no
1
no
no
no
no
no
/define/boundary-conditions/solid
solid_cu
yes
copper
no
no
no
no
0
no
0
no
0
no
0
no
0
no
1
no
no
no
/define/boundary-conditions/solid
solid_tim2
yes
tim2
no
no
no
no
0
no
0
no
0
no
0
no
0
no
1
no
no
no""")
for i in range(1, 13):
    a(f"/define/boundary-conditions/set/mass-flow-inlet inlet_jet_{i:02d} () mass-flow no 1.225e-4 t no 313.15 q")
a("/define/boundary-conditions/set/pressure-outlet outlet_y_front () t no 313.15 q")
a("/define/boundary-conditions/set/pressure-outlet outlet_y_back () t no 313.15 q")
a("/define/boundary-conditions/wall")
a("wall_heat")
a("no")
a("0")
a("no")
a("0")
a("no")
a("yes")
a("heat-flux")
a("no")
a("579282")
a("no")
a("no")
a("1")
a("/report/reference-values/temperature 313.15")
a("/define/operating-conditions/operating-pressure 101325")
a("/solve/set/p-v-coupling 24")
a("/solve/set/pseudo-transient yes")
a("yes")
a("1")
a("1")
a("0")
a("yes")
a("1")
a("/solve/set/discretization-scheme/pressure 10")
a("/solve/set/discretization-scheme/mom 0")
a("/solve/set/discretization-scheme/k 0")
a("/solve/set/discretization-scheme/omega 0")
a("/solve/set/discretization-scheme/temperature 0")
a("/solve/monitors/residual/print? yes")
a("/solve/monitors/residual/plot? yes")
a("/solve/monitors/residual/criterion-type 0")
a("/solve/monitors/residual/check-convergence? no")
for _ in range(6):
    a("no")
a("/solve/initialize/set-defaults/temperature 313.15")
a("/solve/initialize/initialize-flow")
init_case = f"{BASE}/fluent/uc01b_cht_less_12y_cpu_init"
a(f'/file/write-case-data "{init_case}"')
a("/file/stop-transcript")
a("/exit")
(FLU / "uc01b_cht_less_12y_cpu_init.jou").write_text("\n".join(L) + "\n", encoding="ascii", newline="\n")

G = []
g = G.append
g("; Single precision. 4 CPU processes. GPU offload is the coupled AMG only.")
g("; First order throughout. Save case-data at iterations 200, 400, 600, 800, 1000.")
g("/file/set-batch-options yes yes no")
g("/file/confirm-overwrite yes")
g(f'/file/start-transcript "{BASE}/logs/fluent_cht_less_12y_sp_gpgpu.log"')
g(f'/file/read-case-data "{init_case}.cas.h5"')
g("/parallel/gpgpu/show")
out = f"{BASE}/fluent/uc01b_cht_less_12y"


def save(n):
    g(f'/file/write-case-data "{out}_i{n}"')


g("/solve/iterate 200")
save(200)
g("/solve/iterate 200")
save(400)
g("/solve/iterate 200")
save(600)
g("/solve/iterate 200")
save(800)
g("/solve/iterate 200")
save(1000)
g("/file/stop-transcript")
(FLU / "uc01b_cht_less_12y_gpu_solve.jou").write_text("\n".join(G) + "\n", encoding="ascii", newline="\n")
print("wrote cpu init and gpu solve journals")
