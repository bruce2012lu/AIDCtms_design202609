# Grace CPU 冷却区网格

对象是 CP-GRACE-MC-01 的 CPU 区。当前算例是沿板面 Y 的交错流：相邻槽一条朝后面板、一条朝托盘前侧，槽端在 Y 向封死，再往 Z 汇流。

方案和数字在 `GRACE_CPU_交错流网格方案_v1.0.md`。网格由 `mesh/write_grace_cpu_counterflow.py` 生成，一维对照在 `calc_counterflow.py`。

- 交错流一对槽：`mesh/grace_cpu_counterflow_pair.msh`（2487936 单元，米）
- 交错流说明和边界：`mesh/grace_cpu_counterflow_info.txt`
- ICEM 骨架：`icem/build_grace_cpu_counterflow.rpl`（毫米）
- Fluent 算例（不迭代）：`fluent/grace_cpu_counterflow_setup.jou`、`fluent/grace_cpu_counterflow_check.jou`

早先的平行槽网格仍留着，不是当前算例：

- 单通道全六面体：`mesh/grace_cpu_channel.msh`（715440 单元）
- 说明：`GRACE_CPU_ICEM网格方案_v1.0.md`

ICEM 里用 File → Replay Scripts → Replay 打开 rpl。Fluent 只读 msh。本机 `E:\cae\programfiles\Ansys2026` 下目前没有 Fluent / ICEM 可执行文件，所以还没有软件内的 mesh/check。
