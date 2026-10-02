# UC-01b: import Python Cartesian hex (Fluent .msh) into ICEM and present it.
# Mesh is SI meters. No ICEM blocking (.blk) — this is unstructured HEXA_8.
# Geometry tin (mm) is NOT loaded with the mesh (unit mismatch).
# Batch: icemcfd.bat -batch -script import_uc01b_mesh.rpl
# GUI:   icemcfd.bat -script view_uc01b.rpl
#        or File > Open Project > icem/uc01b.prj

proc ucv_log {m} {
    puts "UC01b-VIEW: $m"
}

proc ucv_try {label cmd} {
    if {[catch {uplevel 1 $cmd} err]} {
        ucv_log "$label FAILED: $err"
        return 0
    }
    return 1
}

set OUTDIR {D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd/uc01b_2.4x3.0}
if {![file isdirectory $OUTDIR]} {
    set OUTDIR [file normalize [file join [file dirname [info script]] ..]]
}
set ICEMDIR [file join $OUTDIR icem]
set MESHDIR [file join $OUTDIR mesh]
set VIEWDIR [file join $ICEMDIR views]
set LOGDIR  [file join $OUTDIR logs]
file mkdir $ICEMDIR
file mkdir $VIEWDIR
file mkdir $LOGDIR

set msh [file join $MESHDIR uc01b_classic.msh]
if {![file exists $msh]} { set msh [file join $MESHDIR uc01b.msh] }
set nas [file join $ICEMDIR uc01b.nas]
set uns [file join $ICEMDIR uc01b.uns]
set prj [file join $ICEMDIR uc01b.prj]
set qlog [file join $VIEWDIR quality.txt]
set slog [file join $LOGDIR icem_view.log]

ucv_log "OUTDIR=$OUTDIR"
ucv_log "msh exists=[file exists $msh] size=[expr {[file exists $msh] ? [file size $msh] : 0}]"
ucv_log "batch_mode=[expr {[info exists batch_mode] ? $batch_mode : {unset}}]"

# --- unload leftover ---
catch { ic_unload_mesh }
catch { ic_hex_unload_blocking }
# do not load tin (mm) with this mesh (meters)

# --- import Fluent msh ---
set imported 0
if {[file exists $uns] && [file size $uns] > 1000 && ![info exists ::UC01B_FORCE_REIMPORT]} {
    ucv_log "loading existing uns $uns"
    if {[ucv_try load_uns { ic_uns_load $uns }]} {
        set imported 1
    }
}

if {!$imported} {
    set rf ""
    if {[info exists env(ICEM_ACN)]} {
        set rf [file join $env(ICEM_ACN) icemcfd result-interfaces readfluent.exe]
        if {![file exists $rf]} {
            set rf [file join $env(ICEM_ACN) icemcfd result-interfaces readfluent]
        }
    }
    if {$rf eq "" || ![file exists $rf]} {
        set rf {E:/cae/programfiles/Ansys2026/ANSYS Inc261/v261/icemcfd/win64_amd/icemcfd/result-interfaces/readfluent.exe}
    }
    ucv_log "readfluent=$rf exists=[file exists $rf] msh=$msh exists=[file exists $msh]"
    if {[file exists $rf] && [file exists $msh]} {
        ucv_log "importing Fluent msh via ic_read_external prec=2"
        if {[ucv_try read_ext { ic_read_external $rf $msh 1 2 0 "" }]} {
            set imported 1
        }
    }
    if {!$imported && [file exists $nas]} {
        set iced ""
        if {[info exists env(ICEM_ACN)]} {
            set iced [file join $env(ICEM_ACN) icemcfd output-interfaces IcedNastran.exe]
        }
        if {$iced eq "" || ![file exists $iced]} {
            set iced {E:/cae/programfiles/Ansys2026/ANSYS Inc261/v261/icemcfd/win64_amd/icemcfd/output-interfaces/IcedNastran.exe}
        }
        set nasproj [file join $ICEMDIR uc01b]
        ucv_log "fallback IcedNastran $iced nas=$nas"
        if {[ucv_try nastran { ic_import_nastran $iced $nas 0 0 0 $nasproj }]} {
            if {[file exists ${nasproj}.uns]} {
                ucv_try load_nas_uns { ic_uns_load ${nasproj}.uns }
                if {[ic_uns_is_loaded]} { set imported 1 }
            }
        }
    }
}

if {![ic_uns_is_loaded]} {
    ucv_log "ERROR: no unstructured mesh loaded"
    return
}

# --- inventory (only numbers ICEM actually returns) ---
set ncell "?"
set nnode "?"
set types "?"
set fams "?"
catch { set ncell [ic_count_elements 3d] }
catch { set nhex  [ic_count_elements hexa] }
catch { set ntet  [ic_count_elements tetra] }
catch { set nquad [ic_count_elements quad] }
catch { set nnode [ic_count_nodes] }
catch { set types [ic_uns_list_types] }
catch { set fams  [ic_uns_list_families] }
ucv_log "loaded cells_3d=$ncell hexa=$nhex tetra=$ntet quad=$nquad nodes=$nnode"
ucv_log "types=$types"
ucv_log "families=$fams"
catch { ic_uns_print_info summary }

# --- save uns ---
ucv_try save_uns { ic_save_unstruct $uns }
if {[file exists $uns]} {
    ucv_log "saved uns size=[file size $uns] $uns"
} else {
    ucv_log "WARNING: uns not written"
}

# --- quality (do not invent numbers) ---
set qfp [open $qlog w]
puts $qfp "UC-01b ICEM quality — only values ICEM computed"
puts $qfp "source: Python Cartesian hex Fluent msh (NOT ICEM tetra, NOT ICEM blocking)"
puts $qfp "msh $msh"
puts $qfp "uns $uns"
puts $qfp "cells_3d $ncell"
puts $qfp "hexa $nhex"
puts $qfp "tetra $ntet"
puts $qfp "quad $nquad"
puts $qfp "nodes $nnode"
puts $qfp "types $types"
puts $qfp "families $fams"
set qok 0
if {[catch { set st [ic_uns_subset_metric "" "" Quality 1] } qerr]} {
    puts $qfp "Quality metric: NOT computed ($qerr)"
    ucv_log "quality metric failed: $qerr"
} else {
    if {$st eq ""} {
        puts $qfp "Quality metric: empty return (not defined)"
        ucv_log "quality metric empty"
    } else {
        set qok 1
        puts $qfp "Quality metric raw: $st"
        puts $qfp "  n_defined [lindex $st 0]"
        puts $qfp "  n_undef   [lindex $st 1]"
        puts $qfp "  n_bad     [lindex $st 2]"
        puts $qfp "  min       [lindex $st 3]"
        puts $qfp "  max       [lindex $st 4]"
        puts $qfp "  sum       [lindex $st 5]"
        ucv_log "Quality $st"
        # histogram on HEXA_8 after compute_diagnostic
        if {[catch {
            global uns_cur
            set hname [ic_uns_subset_create histo_hex 0]
            set parts [ic_uns_list_families]
            ic_uns_update_family_type $hname $parts HEXA_8 update 1
            set hmap [$uns_cur get_map $hname]
            set hst [$hmap compute_diagnostic Quality ""]
            set hmin [lindex $hst 3]
            set hmax [lindex $hst 4]
            if {![string is double $hmin]} { set hmin 0 }
            if {![string is double $hmax]} { set hmax 1 }
            if {$hmax <= $hmin} { set hmax [expr {$hmin + 1.0}] }
            set histo [$hmap diagnostic_histogram $hmin $hmax 20]
            puts $qfp "histogram_range $hmin $hmax"
            puts $qfp "histogram $histo"
            ucv_log "histogram $histo"
            catch { ic_uns_subset_delete $hname }
        } herr]} {
            puts $qfp "histogram: NOT computed ($herr)"
            ucv_log "histogram failed: $herr"
        }
    }
}
close $qfp
ucv_log "wrote $qlog"

# --- project file (File > Open Project) ---
# Relative names so the folder can move. No .blk (not ICEM hex blocking).
set prjfp [open $prj w]
puts $prjfp "# ICEM CFD Project Settings"
puts $prjfp "# UC-01b view project — Python Cartesian hex imported from Fluent msh"
puts $prjfp "# Units: meters (Fluent). Official circle geom is icem/uc01b.tin (mm) — do not overlay."
puts $prjfp ""
puts $prjfp "array set file_name \{"
puts $prjfp "    domain uc01b.uns"
puts $prjfp "    tetin \{\}"
puts $prjfp "    settings uc01b.prj"
puts $prjfp "    project_dir ."
puts $prjfp "    family_boco \{\}"
puts $prjfp "    attributes \{\}"
puts $prjfp "    blocking \{\}"
puts $prjfp "    domains_dir ."
puts $prjfp "\}"
close $prjfp
ucv_log "wrote project $prj"
catch {
    global file_name
    set file_name(domain) $uns
    set file_name(settings) $prj
    set file_name(project_dir) $ICEMDIR
    set file_name(tetin) ""
    set file_name(blocking) ""
}

# --- display (GUI only) ---
proc ucv_snap {stem} {
    global VIEWDIR tdv_default
    set ppm [file join $VIEWDIR ${stem}.ppm]
    set png [file join $VIEWDIR ${stem}.png]
    if {![info exists tdv_default] || $tdv_default eq ""} {
        ucv_log "snap $stem skipped: no viewer"
        return 0
    }
    if {[catch {
        set fp [open $ppm w]
        $tdv_default write_ppm $fp portrait 0 0 0 0 0
        close $fp
    } err]} {
        ucv_log "snap $stem write_ppm failed: $err"
        return 0
    }
    ucv_log "wrote $ppm size=[file size $ppm]"
    # optional jpeg via ICEM bindir
    catch {
        global env
        set cjpeg [file join $env(ICEM_ACN) bin cjpeg.exe]
        if {[file exists $cjpeg]} {
            exec $cjpeg -outfile [file join $VIEWDIR ${stem}.jpg] $ppm
        }
    }
    return 1
}

set is_batch 0
if {[info exists batch_mode] && $batch_mode} { set is_batch 1 }

if {!$is_batch} {
    ucv_log "GUI display: hex + quads, fit"
    catch { update }
    after 1500
    catch { ic_visible unstruct HEXA_8 1 }
    catch { ic_visible unstruct QUAD_4 1 }
    catch { ic_visible unstruct TETRA_4 0 }
    catch { ic_uns_subset_visible All 1 }
    catch { ic_display_update unstruct }
    catch { ic_view home }
    catch { update }
    after 800
    ucv_snap iso

    # X=0 through jet (meters)
    ucv_log "section X=0 (jet + 3 slots in YZ)"
    catch { ic_uns_subset_cut All plane 1 1 {0 0 0.004} {1 0 0} }
    catch { ic_display_update unstruct }
    after 300
    ucv_snap section_jet_x0

    # Z = 0.75 mm through slots (plan)
    ucv_log "section Z=0.00075 m (3 slots in XY)"
    catch { ic_uns_subset_cut All plane 1 1 {0 0 0.00075} {0 0 1} }
    catch { ic_display_update unstruct }
    after 300
    ucv_snap section_slots_z075

    # restore uncut iso
    catch { ic_uns_subset_cut All plane 0 1 {0 0 0} {1 0 0} }
    catch { ic_view home }
    catch { ic_display_update all }
    ucv_log "GUI ready — look at 3 slots, jet, return slits"
} else {
    ucv_log "batch: skip GUI fit/screenshots (no viewer)"
}

ucv_log "done project=$prj uns=$uns"
