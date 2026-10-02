"""落地后端。

同一份参数集喂给不同 CAD 目标：
    neutral      STEP / STL，供应商与 CFD 的交换格式，本机可跑
    drawing      分层 DXF 顶视图，AutoCAD / 中望 / DWG TrueView 直接可开
    solidworks   COM 程序合成 + VBA 宏，需实机 SOLIDWORKS
"""
