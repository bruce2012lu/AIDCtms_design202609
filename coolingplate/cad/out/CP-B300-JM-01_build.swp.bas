' CP-B300-JM-01 · NVIDIA B300 微通道 + 冲击换热冷板
' 由 coldplate/backends/solidworks.py 自动生成 · 参数源 cp_b300_jm01.yaml
' 单位：常量用 mm，调用 API 前统一乘 MM 换成米。
' 状态：几何为候选，待订单 ICD 冻结。本宏未经实机验证。

Option Explicit

Const MM As Double = 0.001
Const PLATE_W As Double = 95
Const PLATE_H As Double = 75
Const BASE_T As Double = 3.5
Const BASE_REM As Double = 2
Const NOZZLE_T As Double = 2.5
Const STANDOFF As Double = 2
Const JET_D As Double = 0.5
Const JET_S As Double = 3
Const SUCTION_D As Double = 0.8
Const G_W As Double = 0.4
Const G_D As Double = 1.5
Const G_PITCH As Double = 0.8
Const G_SEGLEN As Double = 6
Const G_LAND As Double = 1
Const DIE_W As Double = 27
Const DIE_H As Double = 28
Const GROOVE_SPAN As Double = 23.6
Const HBM_CH_W As Double = 0.6
Const HBM_CH_D As Double = 1.5
Const HBM_CH_PITCH As Double = 1.3
Const HBM_SPAN As Double = 9.7
Const HBM_W As Double = 11
Const RIB_W As Double = 2

Const N_JET_X As Long = 8
Const N_JET_Y As Long = 8
Const N_GROOVE As Long = 30
Const N_SEG As Long = 4
Const N_HBM_CH As Long = 8

Dim swApp As Object
Dim swModel As Object
Dim swSketch As Object

Sub main()
    Set swApp = Application.SldWorks
    BuildBasePlate
    BuildNozzlePlate
End Sub

' ---- 换热底板：余铜 + 短槽 + HBM 平槽 + 隔离肋 ----
Sub BuildBasePlate()
    Dim dieX(1) As Double, dieY(1) As Double
    Dim i As Long, j As Long, k As Long
    LoadPairs dieX, dieY, Array(19, 23.5, 49, 23.5)

    Set swModel = swApp.NewPart
    swModel.SketchManager.InsertSketch True
    swModel.SketchManager.CreateCornerRectangle 0, 0, 0, PLATE_W * MM, PLATE_H * MM, 0
    swModel.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, _
        BASE_T * MM, 0, False, False, False, False, 0, 0, _
        False, False, False, False, True, True, True, 0, 0, False

    ' 所有槽画在同一张草图里，一次切除，避免 250 个特征拖垮重建
    swModel.SketchManager.Insert3DSketch False
    SelectTopFace
    swModel.SketchManager.InsertSketch True
    For i = 0 To UBound(dieX)
        Dim y0 As Double
        y0 = dieY(i) + (DIE_H - GROOVE_SPAN) / 2
        For j = 0 To N_GROOVE - 1
            Dim gy As Double
            gy = y0 + j * G_PITCH
            For k = 0 To N_SEG - 1
                Dim gx As Double
                gx = dieX(i) + k * (G_SEGLEN + G_LAND)
                swModel.SketchManager.CreateCornerRectangle _
                    gx * MM, gy * MM, 0, (gx + G_SEGLEN) * MM, (gy + G_W) * MM, 0
            Next k
        Next j
    Next i
    AddHbmChannelRects
    swModel.FeatureManager.FeatureCut4 True, False, False, 0, 0, _
        G_D * MM, 0, False, False, False, False, 0, 0, _
        False, False, False, False, False, True, True, 0, 0, False, False

    AddIsolationRibs
    swModel.ViewZoomtofit2
End Sub

' HBM 两侧平槽：贯通整列，流程沿列长边
Sub AddHbmChannelRects()
    Dim colX(1) As Double
    colX(0) = 5: colX(1) = 79
    Const COL_LO As Double = 12.5
    Const COL_HI As Double = 62.5
    Dim c As Long, k As Long, x0 As Double
    For c = 0 To 1
        x0 = colX(c) + (HBM_W - HBM_SPAN) / 2
        For k = 0 To N_HBM_CH - 1
            Dim cx As Double
            cx = x0 + k * HBM_CH_PITCH
            swModel.SketchManager.CreateCornerRectangle _
                cx * MM, COL_LO * MM, 0, (cx + HBM_CH_W) * MM, COL_HI * MM, 0
        Next k
    Next c
End Sub

' 隔离肋填满 H 间隙，从槽底连到盖板，切断 GPU 区横流
Sub AddIsolationRibs()
    Dim ribX(1) As Double
    ribX(0) = 16.5: ribX(1) = 76.5
    Dim r As Long
    SelectTopFace
    swModel.SketchManager.InsertSketch True
    For r = 0 To 1
        swModel.SketchManager.CreateCornerRectangle _
            ribX(r) * MM, 0, 0, (ribX(r) + RIB_W) * MM, PLATE_H * MM, 0
    Next r
    swModel.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, _
        STANDOFF * MM, 0, False, False, False, False, 0, 0, _
        False, False, False, False, True, True, True, 0, 0, False
End Sub

' ---- 喷嘴盖板：128 个喷嘴 + 错排抽吸孔，HBM 区不开孔 ----
Sub BuildNozzlePlate()
    Dim jetX(1) As Double, jetY(1) As Double
    Dim i As Long, j As Long, k As Long
    LoadPairs jetX, jetY, Array(22, 27, 52, 27)

    Set swModel = swApp.NewPart
    swModel.SketchManager.InsertSketch True
    swModel.SketchManager.CreateCornerRectangle 0, 0, 0, PLATE_W * MM, PLATE_H * MM, 0
    swModel.FeatureManager.FeatureExtrusion3 True, False, False, 0, 0, _
        NOZZLE_T * MM, 0, False, False, False, False, 0, 0, _
        False, False, False, False, True, True, True, 0, 0, False

    SelectTopFace
    swModel.SketchManager.InsertSketch True
    For i = 0 To UBound(jetX)
        For j = 0 To N_JET_X - 1
            For k = 0 To N_JET_Y - 1
                swModel.SketchManager.CreateCircleByRadius _
                    (jetX(i) + j * JET_S) * MM, (jetY(i) + k * JET_S) * MM, 0, JET_D / 2 * MM
            Next k
        Next j
        For j = 0 To N_JET_X - 2
            For k = 0 To N_JET_Y - 2
                swModel.SketchManager.CreateCircleByRadius _
                    (jetX(i) + (j + 0.5) * JET_S) * MM, _
                    (jetY(i) + (k + 0.5) * JET_S) * MM, 0, SUCTION_D / 2 * MM
            Next k
        Next j
    Next i
    ' 通孔：ThroughAll
    swModel.FeatureManager.FeatureCut4 True, False, False, 1, 0, _
        NOZZLE_T * MM, 0, False, False, False, False, 0, 0, _
        False, False, False, False, False, True, True, 0, 0, False, False
    swModel.ViewZoomtofit2
End Sub

Sub SelectTopFace()
    swModel.Extension.SelectByRay 0.001, BASE_T * MM * 2, 0.001, _
        0, -1, 0, 0.0005, 2, False, 0, 0
End Sub

Sub LoadPairs(xs() As Double, ys() As Double, flat As Variant)
    Dim n As Long, i As Long
    n = (UBound(flat) + 1) \ 2
    For i = 0 To n - 1
        xs(i) = flat(i * 2)
        ys(i) = flat(i * 2 + 1)
    Next i
End Sub

