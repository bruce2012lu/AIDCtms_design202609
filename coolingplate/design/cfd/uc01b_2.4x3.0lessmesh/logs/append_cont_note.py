# -*- coding: utf-8 -*-
p = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh\UC01b_lessmesh_结果报告_v1.0.md"
note = """

---

## 5. 续算（从 iter 430 的场接着算）

第 430 步收敛后原进程已退出。按同一桌面命令重新打开，读 `fluent/uc01b_cht_less_t4_gpu.cas.h5` 与 `.dat.h5`，没有读 msh，没有初始化。判据数值不变。因为场已经满足判据，这次把提前停止关掉，否则 iterate 会在第一步就停。计划再走 1000 步。日志：`logs/fluent_cht_less_gui_continue.log`。窗口仍开着。

```text
\"E:\\cae\\programfiles\\Ansys2026\\ANSYS Inc261\\v261\\fluent\\ntbin\\win64\\fluent.exe\" 3ddp -r26.1.0 -t4 -gpu -i fluent\\uc01b_cht_less_continue.jou
```

从 iter **430** 续上。写本段时已走到 **547**（还剩约 883 步）。窗口标题：`uc01b_cht_less_t4_gpu Parallel Fluent@DESKTOP-JHEHF28 [3d, dp, pbns, sstkw, 4-processes, gpu]`，会话 1。约从 539 步起每步打印 `activating bcgstab`，单步变慢，计算没有退出。

```
   547  2.5481e-07  1.6043e-07  3.3379e-07  3.1842e-07  9.1814e-07  6.5888e-07  1.5819e-04
```

连续性 2.55e-7，能量 9.18e-7，omega 停在 **1.582e-4**（与 430 步的 1.581e-4 同一平台，没有收紧 omega 判据）。温度和压降要等这 1000 步块结束、期刊打印面平均之后才更新；在此之前工程量仍是第 4 节的 iter 430 数字。续算场将写成 `fluent/uc01b_cht_less_t4_gpu_cont.cas.h5`，不覆盖 430 步的 cas/dat。
"""
raw = open(p, "rb").read()
text = raw.decode("gbk")
if "## 5." in text:
    print("already")
else:
    text = text + note
    open(p, "wb").write(text.encode("gbk"))
    print("ok", text.count("## 5."))
