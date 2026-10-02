# -*- coding: utf-8 -*-
from pathlib import Path

src = Path(__file__).with_name("hbm_w08h20.jou")
text = src.read_text(encoding="ascii")
text = text.replace("hbm_w08h20_run.log", "hbm_cf_w08h20_run.log")
text = text.replace("mesh/hbm_w08h20.msh", "mesh/hbm_cf_w08h20.msh")
text = text.replace("fluent/hbm_w08h20\"", "fluent/hbm_cf_w08h20\"")
text = text.replace("fluent/hbm_w08h20_i200", "fluent/hbm_cf_w08h20_i200")
old = """/define/boundary-conditions/zone-type inlet mass-flow-inlet
/define/boundary-conditions/zone-type outlet pressure-outlet
/define/boundary-conditions/zone-type wall_heat wall
/define/boundary-conditions/zone-type wall_adiabat wall
/define/boundary-conditions/zone-type wall_side wall
/define/boundary-conditions/set/mass-flow-inlet inlet () mass-flow no 3.30733333e-3 t no 313.15 q
/define/boundary-conditions/set/pressure-outlet outlet () t no 313.15 q"""
new = """/define/boundary-conditions/zone-type inlet_lo mass-flow-inlet
/define/boundary-conditions/zone-type inlet_hi mass-flow-inlet
/define/boundary-conditions/zone-type outlet_lo pressure-outlet
/define/boundary-conditions/zone-type outlet_hi pressure-outlet
/define/boundary-conditions/zone-type wall_heat wall
/define/boundary-conditions/zone-type wall_adiabat wall
/define/boundary-conditions/zone-type wall_side wall
/define/boundary-conditions/set/mass-flow-inlet inlet_lo () mass-flow no 1.41742857e-3 t no 313.15 q
/define/boundary-conditions/set/mass-flow-inlet inlet_hi () mass-flow no 1.88990476e-3 t no 313.15 q
/define/boundary-conditions/set/pressure-outlet outlet_lo () t no 313.15 q
/define/boundary-conditions/set/pressure-outlet outlet_hi () t no 313.15 q"""
if old not in text:
    raise SystemExit("bc block missing")
text = text.replace(old, new)
old_rep = """/report/surface-integrals/area-weighted-avg
inlet
()
pressure
no
/report/surface-integrals/area-weighted-avg
outlet
()
pressure
no
/report/surface-integrals/mass-flow-rate
inlet
outlet
()
no"""
new_rep = """/report/surface-integrals/area-weighted-avg
inlet_lo
inlet_hi
()
pressure
no
/report/surface-integrals/area-weighted-avg
outlet_lo
outlet_hi
()
pressure
no
/report/surface-integrals/mass-flow-rate
inlet_lo
inlet_hi
outlet_lo
outlet_hi
()
no"""
if old_rep not in text:
    raise SystemExit("report block missing")
text = text.replace(old_rep, new_rep)
note = (
    "; Counterflow: even channels enter at high Y (inlet_hi), leave at the low-Y Z header.\n"
    "; Odd channels enter at low Y (inlet_lo), leave at the high-Y Z header.\n"
    "; Mass flow split 4/7 and 3/7 of 0.20 L/min. Check off. Do not stop before step 200.\n"
)
first, rest = text.split("\n", 1)
text = note + rest
out = Path(__file__).with_name("hbm_cf_w08h20.jou")
out.write_bytes(text.replace("\r\n", "\n").encode("ascii"))
print(out)
