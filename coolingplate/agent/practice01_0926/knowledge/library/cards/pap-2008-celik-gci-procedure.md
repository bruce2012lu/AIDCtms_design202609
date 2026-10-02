---
id: pap-2008-celik-gci-procedure
trust_level: L2
verified_from: fulltext（Table 1 已逐格核对 PDF p.9）
last_verified: 2026-10-02
stages: [5]
benchmark_candidate: true
---

# Celik et al. 2008 · CFD 离散不确定度的估计与报告（GCI 五步法）

Celik, I.B., Ghia, U., Roache, P.J., Freitas, C.J., Coleman, H., Raad, P.E. "Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications." *J. Fluids Eng.* 130(7):078001, 2008。本地是 ASME 官网托管的期刊政策稿（`jfenumaccuracy.pdf`，15 页：PDF p.1–2 为 1993 年政策十条，p.3–15 为 2008 程序）。

## 公式（PDF p.5–7）

1. 代表尺寸：\(h=\big[\tfrac1N\sum\Delta V_i\big]^{1/3}\)（三维）；二维用 \(\big[\tfrac1N\sum\Delta A_i\big]^{1/2}\)（Eq.1–2）。
2. 加密比 \(r=h_{coarse}/h_{fine}>1.3\)，三套网格系统加密（p.6）。
3. 表观阶数（Eq.3a–3c）：
\[
p=\frac{1}{\ln r_{21}}\Big|\ln|\varepsilon_{32}/\varepsilon_{21}|+q(p)\Big|,\quad
q(p)=\ln\frac{r_{21}^p-s}{r_{32}^p-s},\quad s=\operatorname{sgn}(\varepsilon_{32}/\varepsilon_{21})
\]
4. 外推值（Eq.4）：\(\phi_{ext}^{21}=\dfrac{r_{21}^p\phi_1-\phi_2}{r_{21}^p-1}\)
5. 误差与 GCI（Eq.5–7）：
\[
e_a^{21}=\Big|\frac{\phi_1-\phi_2}{\phi_1}\Big|,\quad e_{ext}^{21}=\Big|\frac{\phi_{ext}^{12}-\phi_1}{\phi_{ext}^{12}}\Big|,\quad GCI_{fine}^{21}=\frac{1.25\,e_a^{21}}{r_{21}^p-1}
\]

前提：每个方程残差至少降 3 个数量级，最好 4 个（p.4）；迭代误差应比离散误差小一个量级（附录 A，p.14，抽取排版错乱，用前看原页）。只有两套网格时按 Roache 取 Fs = 3（NASA NPARC 页面，条目 pap-0000-nasa-nparc-spatial-convergence）。

## 关键表

`tables/pap-2008-celik-gci-procedure__table1.csv`：Table 1 三列算例（单调收敛、p < 1、振荡收敛）。注意第 1 列是**二维**网格（r21 = (18000/8000)^{1/2} = 1.5）。

## 本库实现

`tools/gci.py` 实现五步法；`tests/test_gci.py` 用 Table 1 三列全部回归通过（p、φ_ext、e_a、e_ext、GCI 与原表一致到表中保留位数）。

## 对本项目

UC-01b 目前只有一套收敛网格（m425，4,259,680 HEXA，TIM 面 341.385 K；另一边界 bc216 为 342.096 K），12 层网格仍在算。按本方法至少还缺两套系统加密网格，所以**内部 CFD 结果目前不能报告离散不确定度**。建议关心量：TIM 面平均温度、板内压降、驻点温度；Wei 2021 对同类单元胞报告了驻点温度 0.2 % 的离散误差，可作目标量级。
