# UC-01b ICEM Tcl — geometry + tetra/prism attempt (hex blocking is a later GUI gold replay)
# Units: mm. Fluid-only coupon. D=0.40, Sx=3.0, Sy=2.4, H=2.0, slits 0.80 shared.
# Run: icemcfd.bat -batch -script build_uc01b.rpl

proc uc01b_log {m} { puts "UC01b: $m" }

set SX 3.0
set SY 2.4
set D  0.40
set H  2.0
set CHH 1.50
set TLID 2.5
set HPLEN 2.0
set SLIT_HALF 0.40
set R [expr {$D / 2.0}]

set X0 [expr {-$SX / 2.0}]
set X1 [expr {$SX / 2.0}]
set Y0 [expr {-$SY / 2.0}]
set Y1 [expr {$SY / 2.0}]
set XL [expr {$X0 + $SLIT_HALF}]
set XR [expr {$X1 - $SLIT_HALF}]

set Z0 0.0
set Z1 $CHH
set Z2 [expr {$CHH + $H}]
set Z3 [expr {$Z2 + $TLID}]
set Z4 [expr {$Z3 + $HPLEN}]

set OUTDIR [file normalize [file join [file dirname [info script]] ..]]
if {$OUTDIR eq ".."} { set OUTDIR [pwd] }
set ICEMDIR [file join $OUTDIR icem]
set MESHDIR [file join $OUTDIR mesh]
file mkdir $ICEMDIR
file mkdir $MESHDIR

uc01b_log "project dir $OUTDIR"
uc01b_log "D=$D H=$H Sx=$SX Sy=$SY Z=0..$Z4"

catch { ic_uns_new }
catch { ic_geo_delete_all }
catch { ic_hex_delete_all }

foreach fam {
    fluid inlet_jet wall_orifice wall_lid wall_imp fin return_slot SYM
} {
    catch { ic_geo_new_family $fam }
}

# --- points (mm) ---
set pts {
    p_xmin_ymin_z0  {X0 Y0 Z0}
    p_xmax_ymin_z0  {X1 Y0 Z0}
    p_xmax_ymax_z0  {X1 Y1 Z0}
    p_xmin_ymax_z0  {X0 Y1 Z0}
    p_xmin_ymin_z4  {X0 Y0 Z4}
    p_xmax_ymin_z4  {X1 Y0 Z4}
    p_xmax_ymax_z4  {X1 Y1 Z4}
    p_xmin_ymax_z4  {X0 Y1 Z4}
}
# Build key corners via ic_point
foreach {name xyz} {
    c000 {X0 Y0 Z0} c100 {X1 Y0 Z0} c110 {X1 Y1 Z0} c010 {X0 Y1 Z0}
    c001 {X0 Y0 Z4} c101 {X1 Y0 Z4} c111 {X1 Y1 Z4} c011 {X0 Y1 Z4}
} {
    lassign $xyz xv yv zv
    set xv [expr $xv]; set yv [expr $yv]; set zv [expr $zv]
    catch { ic_point {} POINT $name $xv,$yv,$zv }
}

# Bounding-box surfaces as four-point patches (helps tetin / family)
proc uc_quad {name fam a b c d} {
    catch { ic_surface 4-pt SRFS $name [list $a $b $c $d] }
    catch { ic_geo_set_part surface $name $fam 0 }
}

# If 4-pt surface creator is unavailable, still leave families + material point.
catch { ic_geo_new_family GEOM }

# Material point at domain center (gap, off-axis so not inside copper rib)
set mx 0.0
set my 0.0
set mz [expr {$Z1 + $H * 0.5}]
catch { ic_point {} POINT p_mat $mx,$my,$mz }
catch { ic_geo_set_part point p_mat fluid 0 }

# Cylinder axis points for orifice
catch { ic_point {} POINT p_orif_b 0,0,$Z2 }
catch { ic_point {} POINT p_orif_t 0,0,$Z3 }
catch { ic_point {} POINT p_pl_t 0,0,$Z4 }

# Curves: orifice axis
catch { ic_curve point CRV axis_orif {p_orif_b p_orif_t} }
catch { ic_curve point CRV axis_pl   {p_orif_t p_pl_t} }

# Try primitive cylinder + boxes via geo create (version-dependent).
# These commands are best-effort; failure is logged, Python hex is the Fluent path.
foreach cmd {
    {ic_geo_cre_geom_cyl cylinder_orif 0 0 $Z2 0 0 $Z3 $R}
} {
    if {[catch {eval $cmd} err]} {
        uc01b_log "skip primitive: $err"
    }
}

# Size field (mm)
catch { ic_set_meshing_params global 0 hgt 0.08 }
catch { ic_set_meshing_params wall_imp 0 hgt 0.02 }
catch { ic_set_meshing_params fin 0 hgt 0.03 }
catch { ic_set_meshing_params wall_orifice 0 hgt 0.02 }
catch { ic_set_meshing_params prism 0 nlayers 8 hrat 1.2 h1 0.003 }

# Tetra / prism — only if a body exists
set tet_ok 0
if {![catch { ic_run_tetra {} {} {} } err]} {
    set tet_ok 1
    uc01b_log "ic_run_tetra returned ok"
} else {
    uc01b_log "ic_run_tetra failed: $err"
}

set msh [file join $MESHDIR uc01b_icem.msh]
set prj [file join $ICEMDIR uc01b]
catch { ic_save_unstruct [file join $ICEMDIR uc01b.uns] }
catch { ic_save_tetin [file join $ICEMDIR uc01b.tin] }
if {$tet_ok} {
    if {[catch { ic_uns_write $msh 1 } err]} {
        uc01b_log "ic_uns_write failed: $err"
        catch { ic_boco_save_ansys $msh }
    } else {
        uc01b_log "wrote $msh"
    }
} else {
    uc01b_log "no mesh from ICEM tetra — use mesh/write_hex_msh.py"
}

catch { ic_save_project $prj }
uc01b_log "done"
