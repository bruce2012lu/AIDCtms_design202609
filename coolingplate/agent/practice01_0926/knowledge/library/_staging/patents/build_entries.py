"""合并 Google Patents 抓取结果 + fetch 记录 + 人工研读批注 -> entries.json。"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
TODAY = "2026-10-02"
pages = {}
for f in ("all.json", "r4.json", "r5.json"):
    for x in json.loads((HERE / f).read_text(encoding="utf-8")):
        pages[x["query"]] = x
fetched = json.loads((HERE / "fetch_results.json").read_text(encoding="utf-8"))
plan = {p[0]: p for p in json.loads((HERE / "plan.json").read_text(encoding="utf-8"))}

# 人工批注：title_zh, org, 重合度, 权1要点, 重合点, 规避点, 备注, 额外 key_data
A = {
"pat-2019-jetcool-wo2020210587a1": dict(
  t="微射流喷嘴与电子元件共置的电子器件热管理（PCT）", org="JetCool Technologies Inc", rel="低",
  c1="第一层内设发热电子元件，并设贯穿该层厚度的流体通道（即喷嘴）用于带走该元件热量。",
  ov="同为微射流喷嘴阵列概念；但本案把喷嘴做在承载电子元件的同一层（板/基板）内。",
  av="本项目喷嘴板为独立紫铜零件、不承载有源电子元件，权1 前提不满足。",
  note="PCT 已进入国家阶段（US12100643B2），PCT 本身显示 Ceased 属正常。"),
"pat-2019-jetcool-us12100643b2": dict(
  t="微射流喷嘴与电子元件共置的电子器件热管理（US 授权）", org="JetCool Technologies Inc", rel="低",
  c1="第一层含有源发热元件且共置贯穿通道（喷嘴）；第二层含第二发热元件；两层间的歧管层构成储液腔。",
  ov="喷嘴贯穿板厚 + 上游歧管腔的拓扑与喷嘴板+静压箱相似。",
  av="权1 要求喷嘴所在层同时“内置”有源发热元件，并要求第二电子层；本项目喷嘴板无电子元件，基本不落入。"),
"pat-2019-jetcool-us11844193b2": dict(
  t="直接接触式流体冷却模块（微射流喷嘴板直接冲击处理器封装）", org="JetCool Technologies Inc", rel="高",
  c1="入口 → 入口静压腔 → 微射流喷嘴板（多个孔形成微射流，至少部分喷嘴非均匀排布）→ 储液腔；储液腔一侧由处理器封装上表面界定，射流直接冲击封装表面；模块按处理器配件安装孔位紧固而非与处理器机械固定。",
  ov="入口静压腔 + 微射流喷嘴板 + 冲击腔的三层拓扑与本项目“静压箱 + 喷嘴板 + 喷距约 2 mm 冲击腔”高度一致；非均匀喷嘴排布亦可能与 216 孔分区（D0.40/0.50 两种孔径）相关。",
  av="权1 要求储液腔由处理器封装上表面直接界定（直接液冷、无底板）。本项目射流冲击紫铜底板（间接冷板），是主要区别；需关注同族续案 US20250056759A1 / EP4498428 是否扩展到带底板方案。",
  note="同族含 US11191184B2、EP3977832B1、CN113994772B 等，覆盖面广。"),
"pat-2019-onsemi-us12002736b2": dict(
  t="大功率半导体器件射流冲击冷却（射流凸台）", org="Semiconductor Components Industries LLC（onsemi）", rel="中",
  c1="换热底座内设共底面的进液腔和出液腔；射流板平行底面；射流板上设凸起的射流凸台（pedestal），喷嘴开在凸台顶面；腔室隔板连接射流板与底面，将进、出液腔分隔在隔板两侧。",
  ov="射流板 + 进/出液腔分隔与本项目喷嘴板 + 静压箱类似。",
  av="本项目喷嘴板为平板、无凸起射流凸台，且无“连接射流板与底面”的腔室隔板，可规避权1。",
  note="v1.4 未写申请人，实为 onsemi；同族 CN112652586A、US12368088B2。"),
"pat-2022-onsemi-us12255124b2": dict(
  t="带旁通流体的大功率半导体射流冲击冷却", org="Semiconductor Components Industries LLC（onsemi）", rel="中",
  c1="进液腔 → 射流板喷嘴 → 出液腔；另设至少一个旁通喷嘴，从进液腔直接把旁通流体导入出液腔，与射流流体汇合为出口流。",
  ov="进液腔 / 射流板 / 出液腔结构与本项目一致；若本项目静压箱在喷嘴板外围设泄流孔或旁路以降压降，会直接落入。",
  av="确保所有流体只经喷嘴进入冲击腔，不设从静压箱直通出液侧的旁通孔。",
  note="CN 同族 CN117529012A（申请中）。"),
"pat-2012-ibm-us10244654b2": dict(
  t="斜射流冲击与带肋通道组合的冷板（制造方法）", org="International Business Machines Corp", rel="中",
  c1="（方法）制作带多个倾斜射流孔的射流板（偏离法向一定角度），制作带肋通道壁的底板，二者结合成带肋通道，射流方向与通道长边垂直。",
  ov="射流板 + 底板通道（与本项目底板短槽相近）的组合。",
  av="本项目为垂直射流；且该专利已失效（未缴年费），可作为自由现有技术。",
  note="Google 显示 Expired - Fee Related；同族 US9219022B2 等。"),
"pat-2020-google-us11310937b2": dict(
  t="芯片冷却用近边缘射流冲击歧管（Google TPU 直接液冷模块）", org="Google LLC", rel="中",
  c1="孔板（orifice plate）上同时有多个供液孔和回液孔，孔板底面密封于含电路的基板顶面；冷却液分配歧管有供液腔（连通供液孔）和回液腔（连通回液孔）；第一密封件密封孔板与歧管；歧管底面设外圈槽和内圈槽，分别容纳第一、第二密封件。",
  ov="孔板上供液孔与回液孔交错（分布回流）+ 上部供/回液歧管，属分布回流射流结构；摘要提到 ASIC/HBM 冷却。",
  av="权1 的限定落在歧管底面内外双圈密封槽；本项目为钎焊/焊接紫铜冷板、无此双 O 圈结构，规避难度低。分布回流概念本身可援引 IBM US8413712B2（已失效）作现有技术。",
  note="同族 EP3916777B1、CN112185918B、TWI840627B。"),
"pat-2016-ibm-us10306801b2": dict(
  t="两相冷却系统用冷板装置（渐扩通道）", org="International Business Machines Corp", rel="低",
  c1="可叠层的第一层含第一通道，接入口；第二层第二通道连通出口；两层通道组成高度和宽度均沿流向增大的渐扩通道。",
  ov="叠层冷板结构；本项目为单相 PG25，关联度低。",
  av="本项目无沿流向渐扩的叠层通道，不落入。",
  note="v1.4 写“nozzle on hotspot”，但其权1 核心是渐扩通道，与描述有偏差。"),
"pat-2020-intel-us12133357b2": dict(
  t="器件液冷用冷板架构（射流入翅片通道、分流出口）", org="Intel Corp", rel="中",
  c1="相对的第一面（带翅片）与第二面（带壁）；壁沿第一通道两侧连续延伸并界定相邻第二通道；第一通道的第一开口位于两翅片之间的第二面上，并有第二开口；（摘要：流体经开口射向表面、横掠翅片、再离开表面，出口可分为翅片两侧的分流开口）。",
  ov="“从盖板开口向底板射流 → 横掠翅片 → 分流离开”与本项目射流 + 底板短槽回流思路接近。",
  av="权1 对壁/通道/开口相对翅片位置限定细；本项目喷嘴孔阵列 + 短槽布置需逐项比对第一开口与两翅片关系。"),
"pat-2021-nvidia-us12477696b2": dict(
  t="数据中心冷却用主动/被动智能冷板系统（微通道 + 热管）", org="Nvidia Corp", rel="低",
  c1="冷板第一腔内设微通道（主动模式，经服务器歧管流量控制器驱动），第二腔内设热管（被动模式）；两路冷却环路；处理器用神经网络依据传感器控制流量控制器。",
  ov="同属 GPU 冷板；但核心是热管 + AI 控制。",
  av="本项目冷板无内嵌热管、无神经网络流量控制，不落入。⑨孪生在环 AI 控制阶段可参考。",
  note="本件 Google Patents 未提供 B2 PDF，下载的是同族公开文本 US20220232739A1。"),
"pat-2019-intel-us11804418b2": dict(
  t="有限流量条件下的直接液体微射流（DLMJ）结构", org="Intel Corp", rel="中",
  c1="冷板上的微通道阵列（第一方向）；第一、第二歧管；在微通道上方叠置正交的第一、第二流体分配通道阵列，二者平行交错，分别从第一、第二歧管伸出并终止于两歧管之间；分配通道间侧壁下方设挡板伸入微通道阵列。",
  ov="属于“歧管微通道 / 交错进出”结构，与本项目 HBM 区平行微通道、Grace CPU 微通道冷板相关。",
  av="本项目 HBM / CPU 微通道若为端进端出（无正交交错分配层、无伸入微通道的挡板），即不落入。",
  note="v1.4 列为 US20200227341A1（申请公开），已于 2023-10-31 授权为 US11804418B2，本条按授权文本登记。"),
"pat-2018-avic-cn109104844b": dict(
  t="一种微通道冷板（多级流量分配）", org="中国航空工业集团公司雷华电子技术研究所", rel="中",
  c1="盖板 + 分流板 + 散热板；散热板上有多组平行翅片形成微通道；分流板朝盖板侧开平行的进液槽、出液槽，朝散热板侧开交替排列的进液收集槽与出液收集槽，形成多级流量分配并行冷却通道。",
  ov="分流板交替进/出液收集槽 = 歧管微通道，适用于 Grace CPU / HBM 微通道冷板比对。",
  av="本项目微通道区若采用常规端进端出，不设交替进/出液收集槽的分流板，即可规避。",
  note="申请人为中航雷华所；v1.4 示例 id 中写的 'cas' 不准确，本条用 'avic'。"),
"pat-2025-lanrui-cn120597664b": dict(
  t="一种集成旁通控制的液冷散热器微通道构建方法及装置", org="广东蓝锐科技集团股份有限公司", rel="低",
  c1="（方法）建立含主通道、旁通通道及其中 SMA 形状记忆合金微执行器的三维模型；划分流体/固体/执行器域并配置 SMA 本构；构建双向耦合数字孪生模型；施加随时间变化的热负荷后迭代优化设计参数。",
  ov="与本项目⑧数字孪生 / ⑨孪生在环思路相关，但与冷板结构关联弱。",
  av="本项目不含 SMA 执行器旁通通道。",
  note="A 公开（2025-09-05）后 25 天即授权 B（2025-09-30）。Google Patents 无 PDF，仅登记元数据。"),
"pat-2024-huawei-wo2026103052a1": dict(
  t="冷板构件、芯片组件、电路板组件及液冷散热系统（分区混构冷板）", org="Huawei Technologies Co Ltd", rel="高",
  c1="进液腔（进液口）+ 回液腔（出液口）+ 至少一个板式换热腔；每个换热腔有连通进液腔的注入口和连通回液腔的回流口；换热腔含多个换热分区，各分区换热能力与发热器件热流密度分布相匹配，且至少两个分区采用不同换热构造形式。",
  ov="与本项目“GPU 区微射流 + HBM 区平行微通道”的分区混构思路几乎一一对应，且进液腔/回液腔结构与静压箱相近。权1 很宽。",
  av="PCT 处于申请阶段，最终保护范围取决于各国国家阶段审查；建议：①检索本项目方案的最早公开/内部记录日期，与优先权日 2024-11-14 比较；②准备现有技术（如 IBM US8413712B2、JetCool 非均匀喷嘴、Asetek EP4578252B1 分区聚焦）用于异议或无效；③跟踪 CN 国家阶段公开。",
  note="v1.4 写“Patsnap Eureka 公开页”，实际 Google Patents 已收录（无 PDF）；PDF 可从 WIPO Patentscope 获取（需交互页面）。"),
"pat-2021-inspur-cn113871359b": dict(
  t="一种用于 CPU 散热的离心微通道结构及其使用方法", org="苏州浪潮智能科技有限公司（现 苏州元脑智能科技有限公司）", rel="低",
  c1="基板 + 侧面为阿基米德曲线的散热壳体；壳体下环形阵列弧形离心肋片（泡沫金属）形成离心通道；肋片内缘围成对应 CPU 中心的喷射空间；壳体上的喷嘴向喷射空间喷液，形成单相淹没射流；外缘导流通道末端为出口。",
  ov="中心淹没射流 + 径向流出，与“中心进液、向外回流”思路接近。",
  av="本项目为多孔阵列射流 + 短槽，无离心弧形泡沫金属肋片和阿基米德曲线壳体，不落入。",
  note="v1.4 列 A 公开号，已于 2023-11-03 授权为 CN113871359B，本条按 B 登记。"),
"pat-2007-coolit-us8746330b2": dict(
  t="提供分流（split flow）的流体换热器", org="CoolIT Systems Inc", rel="高",
  c1="散热底板上的翅片形成平行微通道（每条通道两端之间连续）；盖在翅片顶端的板上开一条细长进液口，横跨所有微通道且位于通道两端之间（中部）；该板在每条微通道两端各形成出液口，使流体从中部进入后向两个方向沿全长流出。",
  ov="“中心进液、两侧回流”的 split-flow 拓扑；若本项目喷嘴孔落在底板短槽中部、液体沿短槽向两端流出，结构上与权1 很接近。",
  av="可能的区别：①本项目为离散圆孔阵列（216 孔）而非“一条细长进液口横跨全部通道”；②底板为短槽/分段结构而非连续贯通的平行微通道；③回流方式若经喷嘴板上的回流孔而非通道两端。建议请专利代理人对照 IPR 证书确认存续权利要求。",
  note="IPR2015-01276（Asetek 请求）：2015-12-09 立案审查权利要求 1–4、6–8、12、14、15、18–28；2016-12-08 作出最终书面决定；2018-02-14 发布 IPR 证书。存续权利要求须以证书原文为准。Google 显示 Active，预计 2032-04-17 到期。"),
"pat-2007-coolit-us9603284b2": dict(
  t="提供分流（split flow）的流体换热器（续案）", org="CoolIT Systems Inc", rel="高",
  c1="间隔壁形成微通道；板部分封闭微通道；细长进液口位于通道两端之间；出液流道在板外侧；中间微通道端部出口流道大于靠近最外侧壁的出口流道；外壳有间隔的进、出液口。",
  ov="中心进液两侧回流 + 中间通道出口扩大（流量均衡），与本项目回流设计相关。",
  av="本项目若各短槽出口截面一致（不按中间/边缘区分大小），或非细长进液口，可规避。",
  note="同属 2007 优先权家族，与 US8746330B2 同期到期可能性高（以官方为准）。"),
"pat-2007-coolit-us12101906b2": dict(
  t="流体换热器（split-flow 家族 2024 授权）", org="CoolIT Systems Inc", rel="中",
  c1="散热底板中心区域 + 壁形成微通道；第二板盖在壁上封闭通道，在中心区域正上方开第一开孔，两侧为对置边缘；第二板上设凸起密封部顶到顶盖；第一流体通道经第一开孔连通微通道，第二流体通道在两边缘外侧连通第二端口。",
  ov="中心开孔供液、两侧回流，凸起密封分隔进/回液，与本项目“静压箱 + 喷嘴板”分隔进回液思路接近。",
  av="区别点在“第二板上的凸起密封部延伸至顶盖”和“单个中心开孔”；本项目为多孔喷嘴板 + 静压箱，需核对密封方式。",
  note="2007 优先权家族的最新授权，说明 CoolIT 持续以续案扩展保护范围。"),
"pat-2007-coolit-us9453691b2": dict(
  t="流体换热系统（split-flow + 集成泵）", org="CoolIT Systems Inc", rel="低",
  c1="翅片间微通道，带横向凹槽；柔性歧管插件压在斜切的翅片顶缘上形成进液歧管；外壳含泵蜗壳和叶轮；泵出口通道连到细长凹槽。",
  ov="split-flow 进液歧管形式。",
  av="本项目冷板不集成泵、无柔性歧管插件，不落入。"),
"pat-2005-ibm-us8413712b2": dict(
  t="冷却装置（分布回流的分级交错射流冲击冷却器，Brunschwiler）", org="International Business Machines Corp", rel="高",
  c1="第一级结构紧邻冲击间隙：并行入口与出口分布式阵列（出口直径比入口大 25–30%），射流直接冲击热源表面；通道层为交错分叉通道，分别给入口供液、从出口回液；第二级结构是第一级的放大复制（按预定倍数）。",
  ov="分布回流（每个喷嘴旁设回流孔）+ 分级交错歧管，是微射流冷板分布回流架构的奠基专利；冲击间隙中的表面强化结构形成 U 形微通道，与底板短槽相似。",
  av="该专利已失效（未缴年费），可自由实施；更重要的价值是作为针对 Google、CSU、西交大、华为等后续分布回流 / 分区专利的现有技术。",
  note="Google 显示 Expired - Fee Related；配套论文 Brunschwiler et al., ITherm 2006。"),
"pat-1992-hughes-us5316075a": dict(
  t="冲击冷却用液体射流冷板", org="Hughes Aircraft Co（现 Raytheon）", rel="高",
  c1="进液歧管（进液道、废液出口道、喷嘴板面下的进液腔与出液腔）；平板喷嘴板上的喷嘴孔位于进液腔上方、排液孔位于出液腔上方；安装板空腔覆盖喷嘴与排液孔，射流冲击安装板冷却面；冷却面上设多根针肋。",
  ov="“进液歧管（静压箱）+ 平板喷嘴板 + 被冲击的安装板（底板）+ 底板表面强化结构”与本项目基本结构一致。",
  av="已失效（1992 申请），属公有领域，是本项目 FTO 最重要的基础现有技术之一。",
  note="Google 显示 Expired - Fee Related。"),
"pat-2023-jetcool-us12432878b2": dict(
  t="内部再循环冷却模块（分段喷嘴板 + 多静压腔）", org="JetCool Technologies Inc", rel="中",
  c1="喷嘴板分第一、第二区段，各有微射流喷嘴阵列；外壳与喷嘴板之间的顶板设顶板边界，底板冷却面设冷却面边界，围成第一/第二进液静压腔和第一/第二冲击腔；（权1 后续）第一冲击腔的流体再进入第二静压腔，多次冲击后才流出。",
  ov="分区段喷嘴板 + 多个静压腔 + 底板冷却面，与本项目按区域分配喷嘴（GPU 热点区）相关。",
  av="核心是同一流体在模块内多次再循环冲击；本项目为单次冲击后经短槽回流，可规避。",
  note="Google Patents 无 B2 PDF，下载的是同族公开文本 US20250031342A1；同族 WO2025019707A1、CN119631587B、EP4533919A1。"),
"pat-2020-jetcool-us11963341b2": dict(
  t="高温电子器件热管理系统（高温工质 + 旁通控制）", org="JetCool Technologies Inc", rel="低",
  c1="第一冷却回路含升压部件和换热接口；设旁通换热接口的旁通路径；流量控制元件；管理系统依据工质温度、器件温度和环境周期最高温度调节回路流量与旁通流量。",
  ov="系统级控制，与⑨孪生在环 AI 控制有关。",
  av="冷板结构不涉及。"),
"pat-2022-jetcool-us12324126b2": dict(
  t="计算机处理器用主动冷却散热盖", org="JetCool Technologies Inc", rel="低",
  c1="导热第一板接触发热器件，第一凸起侧壁将盖子固定在 PCB 上形成器件腔；第二侧壁 + 第二板形成流体腔；第三板位于两板之间（喷嘴板），将流体腔分隔。",
  ov="盖板一体化射流（Lid 级），与本项目冷板分层类似但应用层级不同。",
  av="本项目为独立冷板，不作为封装盖、不形成器件腔，不落入。"),
"pat-2020-nvidia-us11343940b2": dict(
  t="数据中心冷却系统的可配置冷板（可更换中间层）", org="Nvidia Corp", rel="中",
  c1="冷板含第一部分、第二部分和可更换的中间层；中间层有使冷却液流过的第一通道，以及至少一个调整过的第二通道，用于把冷却液集中到对应计算器件发热部位的区域。",
  ov="本项目喷嘴板夹在静压箱与底板之间，按 GPU 热点布孔，形式上接近“将冷却液集中到发热部位的中间层”。",
  av="权1 要求中间层“可更换”（changeable）；本项目喷嘴板与底板钎焊一体、不可更换，可作为区别点；需关注续案 US12185495B2、US12213281B2。",
  note="同族 CN114126342B、GB2600226B、DE102021121518A1。"),
"pat-2022-onsemi-cn117529012a": dict(
  t="用于半导体器件的射流冲击冷却组件及其制造方法、射流板组件", org="半导体元件工业有限责任公司（onsemi）", rel="中",
  c1="进液腔 → 射流板喷嘴 → 出液腔；至少一个旁通喷嘴把进液腔的旁通流体直接导入出液腔，与射流流体汇合为出口流。",
  ov="同 US12255124B2；在中国申请中，对国内量产 FTO 更直接。",
  av="不设静压箱到出液侧的旁通孔。",
  note="Google 显示 Pending（申请中）；可到 CNIPA 公布公告网 epub.cnipa.gov.cn 核实。"),
"pat-2023-jijia-cn117032426a": dict(
  t="一种射流水冷板（渐宽射流槽）", org="东莞市吉佳热控科技有限公司", rel="中",
  c1="进出水部件（进水口、贯穿出水口、底部进水槽）；冷板上盖开射流槽和容纳槽，射流槽位于进水槽正下方且宽度沿远离进水口方向逐级增大；冷板下盖上的散热器置于容纳槽中；容纳槽经连接孔通出水口。",
  ov="射流 + 底部散热器（翅片），与喷嘴板 + 底板短槽相近。",
  av="本项目为圆孔阵列、非宽度渐变的射流槽，可规避。",
  note="Google 显示 Pending。"),
"pat-2019-pennstate-us12029008b2": dict(
  t="混合微射流液冷均热板 / 散热器", org="Penn State Research Foundation", rel="中",
  c1="进液歧管从进液管经多级分形分叉通道均匀分配到射流平面上的微射流阵列；换热板平行于射流面，表面有圆/方/矩形针肋；射流面与换热板之间为淹没腔；出液歧管与外壳一体。",
  ov="微射流阵列 + 淹没冲击腔 + 底板表面强化，与本项目相近。",
  av="权1 要求分形多级分叉进液歧管；本项目采用静压箱（单腔均压）而非分形树状分配，可规避。底板短槽是否属于“针肋”需注意。"),
"pat-2020-csu-us20230063534a1": dict(
  t="射流冲击冷却装置、系统和方法（分布式注入/抽取孔板）", org="Colorado State University Research Foundation", rel="中",
  c1="分配板上贯穿设置多个注入孔和多个抽取孔；歧管有进流容积、出流容积及在分配板第一侧将二者分隔的结构；冲击靶顶面有凸起表面特征，与分配板第二侧相对，并与覆盖被冷却物的均热板耦合。",
  ov="分配板上注入孔与回流孔共存（分布回流）+ 冲击靶表面特征（类似底板短槽）+ 进/出流容积分隔，与本项目分布回流方案相近。",
  av="若本项目回流不经喷嘴板（例如从底板短槽侧向流出），即可规避“分配板含抽取孔”；该件仍处申请中，需跟踪授权范围。",
  note="Google 显示 Pending。"),
"pat-2022-asetek-ep4578252b1": dict(
  t="电子器件液冷用冷板组件（分区聚焦 + split flow）", org="Asetek A/S", rel="高",
  c1="冷板内表面设导流结构，使冷却液按预设图案集中流经一个或多个区域；分配层装在冷板内表面上，含进液口（接进液通道）和出液口（接出液通道）；至少第一区域采用 split flow（从进液通道分成多通道、向至少两个方向流走）或 uniting flow 等流型；（说明书）进液通道至少部分覆盖器件高强度热区。",
  ov="“进液通道对准高热流区 + split flow 分流 + 按热区分区”与本项目中心进液、GPU 热点微射流、HBM 区微通道分区布局高度相关。",
  av="EP 已授权；US20240074100A1 仍在审。区别点可能在“分配层 + 冷板内表面导流结构”的具体形式，以及流型定义（本项目为射流冲击而非通道 split flow）。建议做逐项特征比对。",
  note="Google Patents 未提供 EP B1 PDF，下载的是同族 WO2024042182A1 公开文本；同族 CN120092494A。"),
"pat-2018-hust-cn109524376b": dict(
  t="一种多歧式射流微通道芯片液冷散热装置", org="华中科技大学", rel="中",
  c1="进/出液管 + 多歧式射流微通道腔体，腔体由进出口层、回收层、回收孔层、射流喷嘴层、微通道层依次叠层粘合；冷却液经射流喷嘴层进入平行等距微通道层，吸热后经射流喷嘴层、回收孔层、回收层由出液管导出。",
  ov="射流 + 微通道 + 经喷嘴层回流（分布回流）的多层叠构，与本项目喷嘴板 + 底板短槽相似。",
  av="本项目若无独立回收孔层/回收层，回流也不穿过喷嘴层，即可规避。",
  note="专利号 ZL201811088661.9；2026 年华科成果转化公示涉及本件（可能涉及许可或转让）。"),
"pat-2020-xjtu-cn111328245b": dict(
  t="折返式射流微通道散热器及散热方法", org="西安交通大学", rel="中",
  c1="微通道基板；射流孔板叠在基板上，射流入口孔与回流出口孔交替布置；分配器含进液管、第一分配腔、多个第二分配腔（工质水平进入后垂直冲入射流孔冲击微通道底面）、多个第二回液腔与第一回液腔，折返工质经回流孔排出。",
  ov="射流孔与回流孔交替的分布回流 + 两级分配腔（类似静压箱）+ 微通道底板，结构接近。",
  av="本项目若回流不穿过喷嘴板（无交替回流孔），且静压箱为单腔而非两级分配腔，可规避。"),
}

META_ONLY = [
 dict(id="pat-2025-inspur-cn122699237a", no="CN122699237A", title="射流冷板、机箱及电子设备", org="浪潮电子信息产业股份有限公司", year=2025,
      url="https://eureka.patsnap.com/patent/CN122699237A", rel="中", status="pending_user",
      c1="（据公开摘要）冷板本体腔体内放置翅片部件；射流板把腔体分成第一腔和第二腔，翅片位于第二腔；射流孔轴线与翅片底板表面夹角为锐角（斜射流，用于冲刷翅片间沉积物）。",
      ov="射流板 + 静压腔 + 翅片底板，与本项目基本拓扑一致；浪潮另宣称有 4 种射流冷板架构（中置扩散式等）已获发明专利。",
      av="本项目采用垂直射流（90°），不满足“锐角”特征。",
      note="2025-02 申请，约 2026-09 公开；Google Patents 尚未收录（404）。来源为 CNIPA 公开信息的二手报道及 Patsnap 公开页（全文需登录）。可到 CNIPA 公布公告网 http://epub.cnipa.gov.cn/ 检索获取官方 PDF。浪潮“中置扩散式 / 太阳花式 / 上下腔斜板式 / 环形腔式”4 件授权号本轮未查到，见 notes.md。"),
 dict(id="pat-2026-huawei-cn122160990a", no="CN122160990A", title="散热器、电路板组件及电子设备（射流板 + 翅片）", org="华为技术有限公司", year=2026,
      url="https://eureka.patsnap.com/patent/CN122160990A", rel="中", status="pending_user",
      c1="（据公开摘要）壳体顶壁、射流板与固定架围成第一腔；射流板远离顶壁一侧为第二腔；第一散热翅片设在射流板远离顶壁的一侧；射流区开射流孔连通两腔。",
      ov="射流板 + 静压腔；但翅片长在射流板上而非底板上。",
      av="本项目短槽 / 翅片在紫铜底板上，喷嘴板无翅片，可规避。",
      note="2026-06-05 公开；Google Patents 404；优先权日未核实（id 年份暂用公开年）。官方文本请到 epub.cnipa.gov.cn 获取。"),
 dict(id="pat-2025-sugon-cn202521432906", no="CN202521432906.0（申请号，实用新型）", title="射流微通道冷板", org="曙光信息产业股份有限公司", year=2025,
      url="http://epub.cnipa.gov.cn/", rel="中", status="pending_user",
      c1="（据公开摘要）盖板（第一进液孔、第一排液孔、集液槽）+ 射流板 + 翅片组件（沿第一方向排布）+ 基板依次连接；射流板上同时有射流缝（长度方向平行于翅片）与多个射流孔，均连通集液槽；第二排液孔连通第一排液孔。",
      ov="射流孔 + 翅片 + 基板 + 盖板集液槽（静压箱），与本项目拓扑相近。",
      av="本项目无“与翅片方向平行的射流缝 + 射流孔”组合，可规避；实用新型未经实质审查，稳定性较低。",
      note="据证券之星（引天眼查）报道，2026-06-19 授权；授权公告号本轮未查到，Google Patents 无记录。需在 CNIPA 以申请号检索。"),
]

def ev_status(x):
    exp = [e for e in x.get("events", []) if "expiration" in e.lower()]
    return (exp[-1].replace(" | ", " ") if exp else "")

def kd(c1, ov, av, src):
    return [
        {"quantity": "权利要求1核心技术特征", "value": c1, "locator": "claim 1", "verified_from": src},
        {"quantity": "与本项目结构重合点", "value": ov, "locator": "claim 1 / 摘要", "verified_from": src},
        {"quantity": "可能的规避点", "value": av, "locator": "claim 1", "verified_from": src},
    ]

entries = []
for eid, ann in A.items():
    _, no, pdf_no, grp = plan[eid]
    x = pages[no]
    fr = fetched.get(eid)
    lang = "zh" if no.startswith("CN") else "en"
    status = x.get("legal_status")
    expiry = ev_status(x)
    e = {
        "id": eid, "type": "patent", "title": x["title"], "title_zh": ann["t"],
        "authors": x.get("inventors", [])[:6], "org": ann["org"],
        "year": int(eid.split("-")[1]), "venue": {"US": "USPTO", "CN": "CNIPA", "WO": "WIPO PCT", "EP": "EPO"}[no[:2]],
        "identifiers": {"patent_no": no},
        "url": f"https://patents.google.com/patent/{no}/en", "language": lang,
        "access": {"status": "downloaded" if fr and fr.get("sha256") else "metadata_only",
                   "license": "专利公开文本", "redistributable": False,
                   "copyright_note": "专利公开文本（官方公开）；仅内部研究使用"},
        "trust_level": "L4",
        "trust_reason": "专利局官方公开文本（经 Google Patents 公开存储获取）；法律状态取自 Google Patents 页面推定，非法律结论",
        "stages": [2, 3, 6],
        "topics": ["patents", "jet-impingement" if any(k in (x["title"] + ann["t"]).lower() for k in ("jet", "射流", "split", "分流", "impinge")) else "cold-plate"],
        "summary_zh": f"{ann['t']}。优先权日 {x.get('priorityDate')}，申请日 {x.get('filingDate')}，公开/公告日 {x.get('publicationDate')}。"
                      f"法律状态（Google Patents，{TODAY} 查看）：{status}{('；' + expiry) if expiry else ''}。与本项目重合度：{ann['rel']}。",
        "key_data": kd(ann["c1"], ann["ov"], ann["av"], "landing_page") + [
            {"quantity": "法律状态", "value": f"{status}", "condition": f"Google Patents 推定，{TODAY} 查看，以官方为准", "locator": "landing_page: Legal status", "verified_from": "landing_page"},
            {"quantity": "优先权日", "value": x.get("priorityDate"), "locator": "landing_page: Priority date", "verified_from": "landing_page"},
            {"quantity": "与本项目重合度", "value": ann["rel"], "locator": "claim 1", "verified_from": "landing_page"},
        ],
        "related_internal": ["coolingplate/patent/appendix_核心专利清单_20260907.md"] if grp.startswith("v1.4") else [],
        "retrieved_by": "kb-v0.1-patents-subagent",
        "last_verified": TODAY, "valid_until": "2027-04-02", "status": "active",
        "notes": "；".join(filter(None, [
            f"来源分组：{grp}" + ("（v1.4 清单已收录）" if grp.startswith("v1.4") else "（v1.4 未收录，本轮新增）"),
            f"当前权利人（Google）：{', '.join(x.get('assignee_current') or [])}",
            f"同族：{', '.join(x.get('family_pubs', [])[:10])}" if x.get("family_pubs") else "",
            ann.get("note", ""),
            "权1 摘录基于 Google Patents 页面文本（中文专利为机器翻译转述），FTO 结论须由专利代理人基于官方文本确认；法律状态不构成法律意见，以官方为准。"]))
    }
    if fr and fr.get("sha256"):
        e["file"] = {"path": fr["path"], "sha256": fr["sha256"], "bytes": fr["bytes"], "pages": fr.get("pages"),
                     "source_url": fr["source_url"], "downloaded_at": fr["downloaded_at"]}
        if fr.get("pdf_from") != no:
            e["notes"] += f"；本地 PDF 为同族公开文本 {fr['pdf_from']}"
    else:
        e["access"]["how_to_get"] = "Google Patents 未提供 PDF；可从 CNIPA 公布公告网 / WIPO Patentscope / Espacenet 官方页面获取"
    entries.append(e)

for m in META_ONLY:
    entries.append({
        "id": m["id"], "type": "patent", "title": m["title"], "title_zh": m["title"], "org": m["org"], "year": m["year"],
        "venue": "CNIPA", "identifiers": {"patent_no": m["no"]}, "url": m["url"], "language": "zh",
        "access": {"status": m["status"], "license": "专利公开文本", "redistributable": False,
                   "how_to_get": "到 CNIPA 公布公告网 http://epub.cnipa.gov.cn/ 按号检索下载官方 PDF；Patsnap 全文需登录（login_required），不使用"},
        "trust_level": "L4", "trust_reason": "官方公开信息的二手转述（摘要级），未取得官方全文，可信度待升级",
        "stages": [2, 3, 6], "topics": ["patents", "jet-impingement"],
        "summary_zh": f"{m['title']}（{m['org']}）。与本项目重合度：{m['rel']}。仅摘要级信息。",
        "key_data": kd(m["c1"], m["ov"], m["av"], "secondary") + [
            {"quantity": "与本项目重合度", "value": m["rel"], "locator": "摘要", "verified_from": "secondary"}],
        "retrieved_by": "kb-v0.1-patents-subagent", "last_verified": TODAY, "valid_until": "2027-04-02", "status": "active",
        "notes": "v1.4 未收录，本轮新增；" + m["note"] + "；法律状态不构成法律意见，以官方为准。",
    })

ID_RE = re.compile(r"^(pap|hbk|std|ven|pat|dat|int)-[0-9]{4}-[a-z0-9]+(-[a-z0-9]+)*$")
assert all(ID_RE.match(e["id"]) for e in entries)
(HERE / "entries.json").write_text(json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(entries), "entries;", sum(e["access"]["status"] == "downloaded" for e in entries), "downloaded")
for e in entries:
    print(e["id"], "|", e["access"]["status"], "|", e["key_data"][3]["value"] if e["key_data"][3]["quantity"] == "法律状态" else "-")
