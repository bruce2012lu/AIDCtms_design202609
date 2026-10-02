---
confidence: 0.85
valid_until: 2026-12-31
last_verified: 2026-09-26
expired: false
---

# UC-01b 单元胞 CFD

算的是单孔周期胞，胞面 2.4 mm（Y）× 3.0 mm（X），用来核对 v2 的 216 孔边界。不要把结果写成 95×75 整板热阻。

bc216 场 `design/cfd/uc01b_2.4x3.0lessmesh/fluent/uc01b_cht_less_bc216.cas.h5`，iter 421，已收敛。单孔入口 1.225×10⁻⁴ kg/s，壁面热流 579282 W/m²，静压降 1091.51 Pa，TIM 底 342.096 K。入口 313.15 K。该记忆文件中文完好，优先引用它。

同目录另一份 `uc01b-lessmesh.md` 的中文已损坏，只保留数字：iter 430 收敛，压降 2237.64 Pa，TIM 底 335.404 K。引用前先对照 HTML 结果报告，确认是不是另一次边界。

12 层网格目录 `design/cfd/uc01b_2.4x3.0lessmesh12cells/` 在 2026-09-26 上午仍有 Fluent 日志。未读完最新残差之前，不写新的性能结论。

ANSYS 根目录：`E:\cae\programfiles\Ansys2026\ANSYS Inc261\v261`。
