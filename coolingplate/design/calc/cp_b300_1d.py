# -*- coding: utf-8 -*-
"""
CP-B300-JM-01 一维热工水力计算书（可复算）
用法: set PYTHONIOENCODING=utf-8 && python cp_b300_1d.py > cp_b300_1d_out.txt
所有数值来源于 model.py，报告 v2.0 与本计算书同源。
"""
import math
import model as M


def sep(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


sep("0. 口径")
print(f"几何: 板 {M.GEO['plate_L']}x{M.GEO['plate_W']}x{M.GEO['plate_T']} mm | "
      f"die {M.GEO['die_w']}x{M.GEO['die_h']} x{M.GEO['n_die']} | "
      f"HBM {M.GEO['hbm_w']}x{M.GEO['hbm_h']} x{M.GEO['n_hbm']}")
print(f"射流: D={M.GEO['D_jet']} Sx={M.GEO['S_jet_x']} Sy={M.GEO['S_jet_y']} "
      f"H={M.GEO['H_jet']} mm, "
      f"N={M.N_JET} ({M.GEO['n_jet_x']}x{M.GEO['n_jet_y']} x2), "
      f"Sx/D={M.SD_X:.1f}, Sy/D={M.SD_Y:.1f}, H/D={M.HD:.1f}, f={M.F_AREA:.5f}")
for fl in (M.WATER40, M.PG25_40):
    print(f"物性 {fl.name}: rho={fl.rho} cp={fl.cp} mu={fl.mu:.3e} "
          f"k={fl.k} Pr={fl.Pr:.2f}")

sep("1. 功率拆分（封装假设，待官方 power map）")
for n in M.DESIGN_POINTS:
    s = M.solve(n)
    tot = 2 * s["p_die"] + 8 * s["p_hbm"] + s["p_other"]
    print(f"{n} P={s['P']:.0f} W | die {s['p_die']:.1f} Wx2 | "
          f"HBM {s['p_hbm']:.2f} Wx8 | 其它 {s['p_other']:.1f} W | "
          f"校核合计 {tot:.1f} W")

sep("2. 热流密度")
print(f"单die {M.A_DIE*1e4:.2f} cm2 | 单HBM {M.A_HBM*1e4:.2f} cm2 | "
      f"板 {M.A_PLATE*1e4:.1f} cm2")
for n in M.DESIGN_POINTS:
    s = M.solve(n)
    print(f"{n}: die均 {s['q_die']:.1f} W/cm2 (x2.5 热点 {s['q_die']*2.5:.0f}) | "
          f"HBM均 {s['q_hbm']:.1f} | 板均 {s['q_plate']:.1f}")

sep("3. 流体混合温升 dTf = P/(m cp)")
for fl in (M.WATER40, M.PG25_40):
    print(f"-- {fl.name}")
    for Q in (1.6, 2.0, 2.2, 2.4):
        c = " | ".join(f"{P:.0f}W -> {M.delta_tf(fl,Q,P):.2f} K"
                       for P in (1100.0, 1400.0))
        print(f"   Q={Q:.1f} L/min (m={M.mass_flow(fl,Q):.4f} kg/s): {c}")

sep("4. 射流孔水力")
print(f"单孔 {M.A_JET_1*1e6:.4f} mm2, 总 {M.A_JET*1e6:.2f} mm2")
for n in M.DESIGN_POINTS:
    s = M.solve(n)
    j = s["jet"]
    print(f"{n}: GPU {s['Qg']:.2f} L/min -> V={j['V']:.3f} m/s, "
          f"Re_D={j['Re']:.0f}, 孔口dP={j['dP']/1000:.2f} kPa")

sep("5. 换热系数三模型")
for n in M.DESIGN_POINTS:
    s = M.solve(n)
    o, c = s["opt"], s["con"]
    h_stag = c["h_stag"]
    flag = "  << Re 低于 Martin 有效域 2000，属外推" if o["extrapolated"] else ""
    print(f"{n} Re_D={o['Re']:.0f}")
    print(f"   A 驻点式:   h_stag = {h_stag:,.0f} W/m2K（只代表驻点核）")
    print(f"   B Martin:   K={o['K']:.4f} Nu={o['Nu']:.1f} "
          f"h_avg = {o['h']:,.0f} W/m2K{flag}")
    print(f"   C 肋+导管:  Nu_ch={c['Nu']:.2f} h_ch={c['h_ch']:,.0f} "
          f"eta_fin={c['eta']:.3f} -> h_eff = {c['h_eff']:,.0f} W/m2K")
    print(f"   -> R_conv: B(乐观) {o['R']:.4f} / C(保守) {c['R']:.4f} C/W")

sep("6. GPU 短槽（通道侧）")
print(f"每die槽数 {M.N_CH_DIE} | {M.GEO['ch_w']}x{M.GEO['ch_h']} mm | "
      f"Dh={M.DH_CH*1e3:.4f} mm | f*Re={M.FRE_CH:.2f}")
print(f"湿润面积/die: 肋 {M.A_FIN_DIE*1e6:.0f} + 槽底 {M.A_BOT_DIE*1e6:.0f} "
      f"= {M.A_WET_DIE*1e6:.0f} mm2, 放大 {M.AREA_GAIN:.2f}x")
for n in M.DESIGN_POINTS:
    s = M.solve(n)
    for tag, cs in (("cell(真实)", s["ch"]), ("bank(对比)", s["ch_bank"])):
        print(f"{n} [{tag}] V={cs['V']:.3f} m/s Re={cs['Re']:.0f} "
              f"L={cs['L']*1e3:.1f} mm dP={cs['dP']/1000:.4f} kPa")
print("结论: 两种拓扑下槽内 dP 均 <0.1 kPa -> 短槽是扩展表面(肋)，不是压降元件。")

sep("7. HBM 区校核（无射流）")
print(f"通道 {M.GEO['hbm_ch_w']}x{M.GEO['hbm_ch_h']} mm x{M.GEO['n_hbm_ch']} 条, "
      f"Dh={M.DH_HBM*1e3:.3f} mm, f*Re={M.FRE_HBM:.2f}")
for n in M.DESIGN_POINTS:
    h = M.solve(n)["hbm"]
    print(f"{n}: Q={h['Q_lpm']:.2f} L/min V={h['V']:.3f} m/s "
          f"(帽 {M.GEO['V_cap_hbm']}) {'OK' if h['ok'] else '超帽!'} "
          f"Re={h['Re']:.0f} dP={h['dP']/1000:.2f} kPa")

sep("8. 热阻链、壳温与结温")
print(f"余铜 {M.GEO['base_cu']} mm, A_2die={M.A_2DIE*1e4:.2f} cm2 -> "
      f"R_wall={M.R_WALL:.5f} C/W")
print(f"假设区间: R_TIM2 {M.R_TIM2[0]}~{M.R_TIM2[1]}, "
      f"R_pkg {M.R_PKG[0]}~{M.R_PKG[1]} C/W")
for n in M.DESIGN_POINTS:
    s = M.solve(n)
    verdict = ("双模型均达标" if s["pass_hi"] else
               ("乐观达标/保守超标 -> 必须 CFD+TTV 收敛"
                if s["pass_lo"] else "双模型均超标"))
    print(f"\n{n} P={s['P']:.0f} W Q={s['Q']:.1f} L/min 目标 <{s['target']}")
    print(f"   R_c-in = {s['R_lo']:.4f} ~ {s['R_hi']:.4f} C/W  [{verdict}]")
    print(f"   dT_c   = {s['dTc'][0]:.1f} ~ {s['dTc'][1]:.1f} K")
    print(f"   Tc     = {s['Tc'][0]:.1f} ~ {s['Tc'][1]:.1f} C")
    print(f"   Tj     = {s['Tj'][0]:.1f} ~ {s['Tj'][1]:.1f} C")
    print(f"   dTf    = {s['dTf']:.2f} K -> 出液 {s['Tin']+s['dTf']:.1f} C")

sep("9. 压降预算")
for n in M.DESIGN_POINTS:
    s = M.solve(n)
    d = s["dp"]
    print(f"{n} Q={s['Q']:.1f} L/min:")
    print(f"   孔口(K={M.K_ORIFICE}) {d['orifice']/1000:.2f} kPa | "
          f"GPU槽 {d['channel']/1000:.3f} | HBM槽 {d['hbm']/1000:.2f} | "
          f"歧管/隔墙 {d['manifold'][0]/1000:.0f}~{d['manifold'][1]/1000:.0f}(待CFD)")
    print(f"   板内合计 {d['total'][0]/1000:.1f} ~ {d['total'][1]/1000:.1f} kPa "
          f"(目标 <={M.GEO['dP_target']}, 上限 {M.GEO['dP_limit']})")

sep("10. PG25 复算（同几何同流量）")
for n in M.DESIGN_POINTS:
    sw = M.solve(n, M.WATER40)
    sp = M.solve(n, M.PG25_40)
    print(f"{n}: Re {sp['opt']['Re']:.0f} (水 {sw['opt']['Re']:.0f}) | "
          f"h {sp['opt']['h']:,.0f} vs {sw['opt']['h']:,.0f} "
          f"({(sp['opt']['h']/sw['opt']['h']-1)*100:+.1f}%)")
    print(f"   R_conv {sp['opt']['R']:.4f} vs {sw['opt']['R']:.4f} "
          f"({(sp['opt']['R']/sw['opt']['R']-1)*100:+.1f}%) | "
          f"dTf {sp['dTf']:.2f} vs {sw['dTf']:.2f} K | "
          f"孔口dP {sp['jet']['dP']/1000:.2f} vs {sw['jet']['dP']/1000:.2f} kPa")
print("注: 实算 h 掉约 29%，大于 v1.x 假设的 -15%。PG25 必须单独定流量。")

sep("11. 差距闭合：需要多大 h（footprint 基准）")
tags = {0.008: "常规垫(差)", 0.006: "常规垫(好)",
        0.004: "高性能TIM2", 0.002: "液金/焊接"}
for n in M.DESIGN_POINTS:
    s = M.solve(n)
    print(f"{n} 目标 <{s['target']} C/W (当前保守 h_eff="
          f"{s['con']['h_eff']:,.0f}, 乐观 {s['opt']['h']:,.0f}):")
    for t2 in (0.008, 0.006, 0.004, 0.002):
        hr = M.h_required(s["target"], t2)
        if math.isinf(hr):
            print(f"   TIM2={t2:.3f} ({tags[t2]}): 预算被 TIM2 吃光，不可行")
        else:
            gap = hr / s["con"]["h_eff"]
            print(f"   TIM2={t2:.3f} ({tags[t2]}): 需 h >= {hr:,.0f} W/m2K "
                  f"(保守模型差 {(gap-1)*100:+.0f}%)")

sep("12. 敏感性：孔径（N=216, GPU 1.6 L/min；Re<2000 时 Martin 不采用）")
print(f"{'D':>5} {'Sx/D':>6} {'Sy/D':>6} {'H/D':>5} {'V':>7} {'Re_D':>6} "
      f"{'dP_orif':>8} {'Martin':>8}")
for r in M.orifice_sweep():
    print(f"{r['D']:5.2f} {r['sd_x']:6.1f} {r['sd_y']:6.1f} {r['hd']:5.1f} "
          f"{r['V']:7.3f} {r['Re']:6.0f} {r['dP']/1000:8.2f} "
          f"{'applied' if r['martin_applied'] else 'not used':>8}")
print("读法: 孔径减小 -> V 与 Re_D 上升, 孔口 dP 上升, 仍远低于 20 kPa 窗;")
print("      Re_D 仍 < 2000, Martin 1977 不采用, 不由它改 R_c-in;")
print("      0.40 mm 是单胞 CFD 孔径, 过滤收到 40 um。")

sep("13. 几何闭合校核")
for nm, expr, got, want in M.geometry_checks():
    ok = "OK" if abs(got - want) < 1e-6 else f"ERR (期望 {want})"
    print(f"{nm:12s} {expr:38s} = {got:.1f} mm  {ok}")

sep("14. 机械校核（两端固支板条模型，3 bar 表压）")
mc = M.mech_checks()
print(f"{'工况':46s} {'σ/MPa':>8} {'挠度/μm':>9} {'安全系数':>9}")
for nm, s_, w_, n_ in mc["cases"]:
    print(f"{nm:46s} {s_/1e6:8.2f} {w_*1e6:9.2f} {n_:9.0f}")
print(f"铜屈服强度取 {mc['sy']/1e6:.0f} MPa（退火态，保守）")
print(f"外形体积 {mc['volume']*1e6:.1f} cm3, 按 {mc['fill']*100:.0f}% "
      f"实体率估质量 {mc['mass']*1e3:.0f} g")

print("\n计算书结束。报告 v2.0 引用的每个数字均可由本脚本复现。")
