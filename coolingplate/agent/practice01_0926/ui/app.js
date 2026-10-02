const FIELDS = [
  ["jets.diameter", "孔径 D mm", 0.5, 0.01],
  ["jets.pitch", "节距 S mm", 3, 0.1],
  ["jets.count_x", "X 向孔数 / die", 8, 1],
  ["jets.count_y", "Y 向孔数 / die", 8, 1],
  ["plate.jet_standoff", "喷距 H mm", 2, 0.1],
  ["hydraulics.split.gpu", "GPU 流量 L/min", 1.6, 0.05],
  ["hydraulics.split.hbm", "HBM 流量 L/min", 0.4, 0.05],
  ["gpu_grooves.width", "短槽宽 mm", 0.4, 0.05],
];

const PRESETS = {
  "preset-v1": {},
  "preset-d40": { "jets.diameter": 0.4 },
  "preset-bad": { "jets.diameter": 0.25 },
  "preset-v2": { "jets.diameter": 0.4, "jets.count_x": 9, "jets.count_y": 12, "jets.pitch": 3 },
};

const form = document.querySelector("#form");
const findings = document.querySelector("#findings");
const gateEl = document.querySelector("#gate");
const gateNote = document.querySelector("#gate-note");
const derivedEl = document.querySelector("#derived");
const buildBtn = document.querySelector("#btn-build");
let lastGate = "block";

for (const [path, label, value, step] of FIELDS) {
  const el = document.createElement("label");
  el.innerHTML = `${label}<input type="number" step="${step}" value="${value}" data-path="${path}">`;
  form.append(el);
}

function overlay() {
  const body = {};
  for (const input of form.querySelectorAll("input")) {
    body[input.dataset.path] = Number(input.value);
  }
  return body;
}

function fill(values) {
  const map = {
    "jets.diameter": 0.5, "jets.pitch": 3, "jets.count_x": 8, "jets.count_y": 8,
    "plate.jet_standoff": 2, "hydraulics.split.gpu": 1.6, "hydraulics.split.hbm": 0.4,
    "gpu_grooves.width": 0.4, ...values,
  };
  for (const input of form.querySelectorAll("input")) input.value = map[input.dataset.path];
}

async function api(path, options) {
  const res = await fetch(path, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || res.statusText);
  return data;
}

function showInspect(data) {
  lastGate = data.gate;
  const counts = data.counts;
  gateEl.textContent = `门 ${data.gate} · ERROR ${counts.ERROR} · WARN ${counts.WARN} · INFO ${counts.INFO}`;
  gateEl.className = data.gate === "pass" ? "ok" : data.gate === "warn" ? "warn" : "bad";
  const rejected = (data.overlay_rejected || []).map((r) => r.path + " " + r.reason).join("；");
  gateNote.textContent = rejected || `来源 ${data.source}。孔数 ${data.derived.jet_count}，Re ${data.derived.jet_reynolds}，孔速 ${data.derived.jet_velocity_m_s} m/s。`;
  derivedEl.innerHTML = `<p>短槽 ${data.derived.groove_count_total} 条 · 槽速 ${data.derived.groove_velocity_m_s} m/s · 温升 ${data.derived.fluid_temp_rise_k} K · 腔厚 ${data.stack_mm.cavity} mm</p>`;
  findings.textContent = data.findings
    .filter((f) => f.level !== "INFO")
    .map((f) => `${f.level} [${f.code}] ${f.message}`)
    .join("\n") || "没有 ERROR / WARN。";
  const warnOk = data.gate !== "warn" || document.querySelector("#allow-warn").checked;
  buildBtn.disabled = !(data.gate !== "block" && warnOk && document.querySelector("#confirm").checked);
}

document.querySelector("#btn-inspect").onclick = async () => {
  gateNote.textContent = "校验中…";
  try {
    showInspect(await api("/api/cad/inspect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ overlay: overlay() }),
    }));
  } catch (err) {
    gateEl.textContent = "校验失败";
    gateNote.textContent = String(err.message || err);
    buildBtn.disabled = true;
  }
};

document.querySelector("#btn-build").onclick = async () => {
  buildBtn.disabled = true;
  gateNote.textContent = "建模中，OCC 偶发失败时可再点一次。";
  try {
    const data = await api("/api/cad/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        overlay: overlay(),
        backend: "preview",
        allow_warn: document.querySelector("#allow-warn").checked,
        confirm: true,
      }),
    });
    gateNote.textContent = data.message + (data.files ? " 文件 " + data.files.length + " 个，目录 " + data.run : "");
    findings.textContent = (data.log_tail || "").slice(-1500);
  } catch (err) {
    gateNote.textContent = String(err.message || err);
  }
};

for (const [id, values] of Object.entries(PRESETS)) {
  document.getElementById(id).onclick = () => fill(values);
}
document.querySelector("#confirm").onchange = () => {
  const warnOk = lastGate !== "warn" || document.querySelector("#allow-warn").checked;
  buildBtn.disabled = !(lastGate !== "block" && warnOk && document.querySelector("#confirm").checked);
};
document.querySelector("#allow-warn").onchange = () => document.querySelector("#confirm").onchange();

document.querySelectorAll("nav button").forEach((btn) => {
  btn.onclick = () => {
    document.querySelectorAll("nav button").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll("main section").forEach((s) => s.classList.remove("on"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.page).classList.add("on");
  };
});

function tracksHtml(data) {
  document.querySelector("#tracks").innerHTML = data.tracks.map((t) => `
    <article class="card">
      <b>${t.name}</b>
      <p><span class="tag ${t.agentized === true ? "ok" : "warn"}">${t.status}</span></p>
      <p style="margin-top:8px">${t.geometry}</p>
    </article>`).join("");
}

function catalogHtml(data) {
  document.querySelector("#catalog").innerHTML = data.groups.map((g) => `
    <h2 style="margin-top:16px;font-size:16px">${g.title}</h2>
    <table><tbody>${g.items.map((it) => `<tr><td>${it.title}</td><td><code>${it.path}</code></td><td>${it.note || ""}</td></tr>`).join("")}</tbody></table>
  `).join("");
}

function memoryHtml(data) {
  document.querySelector("#memory").innerHTML = `<table><tbody>${data.semantic.map((m) => `
    <tr><td>${m.title}</td><td>${m.meta.confidence || ""}</td><td>${m.meta.valid_until || ""}</td><td><code>${m.file}</code></td></tr>
  `).join("")}</tbody></table>`;
}

function onedPayload() {
  return {
    point: document.querySelector("#oned-point").value,
    D_mm: Number(document.querySelector("#oned-D").value),
    Q_lpm: Number(document.querySelector("#oned-Q").value),
    N: Number(document.querySelector("#oned-N").value),
    H_mm: Number(document.querySelector("#oned-H").value),
    Sx_mm: Number(document.querySelector("#oned-Sx").value),
    Sy_mm: Number(document.querySelector("#oned-Sy").value),
  };
}

function fillOned(values) {
  document.querySelector("#oned-point").value = values.point;
  document.querySelector("#oned-D").value = values.D_mm;
  document.querySelector("#oned-Q").value = values.Q_lpm;
  document.querySelector("#oned-N").value = values.N;
  document.querySelector("#oned-H").value = values.H_mm;
  document.querySelector("#oned-Sx").value = values.Sx_mm;
  document.querySelector("#oned-Sy").value = values.Sy_mm;
}

function showOned(data) {
  const regime = document.querySelector("#oned-regime");
  regime.textContent = data.regime === "martin" ? "采用 Martin 1977" : "低 Re 准则";
  regime.className = data.regime === "martin" ? "ok" : "warn";
  document.querySelector("#oned-head").textContent = data.headline;
  const a = data.adopted;
  const m = data.martin;
  const j = data.jet;
  document.querySelector("#oned-numbers").innerHTML = `
    <p>保证值 ${a.name}：壳–进液 ${a.R_lo.toFixed(4)}–${a.R_hi.toFixed(4)} °C/W，目标 ${data.target_R}。
    孔速 ${j.V.toFixed(3)} m/s，Re ${j.Re.toFixed(0)}，开孔率 f ${data.open_area_f.toFixed(4)}，H/D ${data.HD.toFixed(2)}。</p>
    <p>Martin 外推：Nu ${m.Nu.toFixed(2)}，h ${m.h.toFixed(0)} W/m²K，对流热阻 ${m.R_conv.toFixed(4)} °C/W。
    ${m.applied ? "已进入保证值下限。" : "未进入保证值。"}
    低 Re 对流热阻 ${data.low_re.R_conv.toFixed(4)} °C/W，短槽 Nu ${data.low_re.Nu_ch.toFixed(2)}。
    混合温升 ${data.dTf_K.toFixed(2)} K，板内压降 ${data.dp_kPa.lo.toFixed(2)}–${data.dp_kPa.hi.toFixed(2)} kPa。</p>
    <p>Re 提到 2000 约需孔径 ${data.lever.D_re2000_mm.toFixed(3)} mm。该孔径 f=${data.lever.f_at_D.toFixed(4)}，H/D=${data.lever.HD_at_D.toFixed(2)}。</p>`;
  document.querySelector("#oned-criteria").innerHTML =
    "<thead><tr><th>准则</th><th></th><th>判定</th></tr></thead><tbody>" +
    data.criteria.map((c) => `<tr><td><code>${c.code}</code></td><td><span class="tag ${c.ok ? "ok" : c.level}">${c.ok ? "通过" : c.level}</span></td><td>${c.message}</td></tr>`).join("") +
    "</tbody>";
}

document.querySelector("#oned-dpa").onclick = () => fillOned({point:"DP-A", D_mm:0.5, Q_lpm:2.0, N:216, H_mm:2, Sx_mm:3, Sy_mm:2.4});
document.querySelector("#oned-dpb").onclick = () => fillOned({point:"DP-B", D_mm:0.5, Q_lpm:2.4, N:216, H_mm:2, Sx_mm:3, Sy_mm:2.4});
document.querySelector("#oned-d40").onclick = () => fillOned({point:"DP-A", D_mm:0.4, Q_lpm:2.0, N:216, H_mm:2, Sx_mm:3, Sy_mm:2.4});
document.querySelector("#btn-oned").onclick = async () => {
  document.querySelector("#oned-head").textContent = "计算中…";
  try {
    showOned(await api("/api/oned/design", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(onedPayload()),
    }));
  } catch (err) {
    document.querySelector("#oned-regime").textContent = "计算失败";
    document.querySelector("#oned-head").textContent = String(err.message || err);
  }
};

function criteriaTable(id, rows) {
  document.querySelector(id).innerHTML =
    "<thead><tr><th>准则</th><th></th><th>判定</th></tr></thead><tbody>" +
    rows.map((c) => `<tr><td><code>${c.code}</code></td><td><span class="tag ${c.ok ? "ok" : c.level}">${c.ok ? "通过" : c.level}</span></td><td>${c.message}</td></tr>`).join("") +
    "</tbody>";
}

function hbmPayload() {
  return {
    point: document.querySelector("#hbm-point").value,
    Q_hbm_lpm: Number(document.querySelector("#hbm-Q").value),
    n_per_side: Number(document.querySelector("#hbm-n").value),
    w_mm: Number(document.querySelector("#hbm-w").value),
    d_mm: Number(document.querySelector("#hbm-d").value),
    pitch_mm: Number(document.querySelector("#hbm-p").value),
    L_mm: Number(document.querySelector("#hbm-L").value),
  };
}

function showHbm(data) {
  const f = data.flow;
  const t = data.thermal;
  document.querySelector("#hbm-title").textContent = "HBM 平槽 · " + data.point;
  document.querySelector("#hbm-head").textContent = data.headline;
  document.querySelector("#hbm-numbers").innerHTML =
    `<p>流量 ${data.inputs.Q_hbm_lpm.toFixed(3)} L/min，${data.inputs.n} 条并联。流速 ${f.V.toFixed(3)} m/s，Re ${f.Re.toFixed(0)}，水力直径 ${f.Dh_mm.toFixed(3)} mm，压降 ${f.dP_kPa.toFixed(3)} kPa。</p>
     <p>热流 ${f.q_W_cm2.toFixed(2)} W/cm²。Nu ${t.Nu.toFixed(2)}，h ${t.h.toFixed(0)} W/m²K，对流热阻 ${t.R_conv.toFixed(4)} °C/W，对流温升 ${t.dT_conv_K.toFixed(2)} K。</p>`;
  criteriaTable("#hbm-criteria", data.criteria);
}

function gracePayload() {
  return {
    Q_lpm: Number(document.querySelector("#grace-Q").value),
    n_cpu: Number(document.querySelector("#grace-n").value),
    w_cpu_mm: Number(document.querySelector("#grace-w").value),
    d_cpu_mm: Number(document.querySelector("#grace-d").value),
    L_cpu_mm: Number(document.querySelector("#grace-L").value),
    pitch_cpu_mm: Number(document.querySelector("#grace-p").value),
  };
}

function showGrace(data) {
  const c = data.cpu;
  const m = data.mem_one_side;
  const o = data.orifice;
  document.querySelector("#grace-title").textContent = data.model;
  document.querySelector("#grace-head").textContent = data.headline;
  document.querySelector("#grace-numbers").innerHTML =
    `<p>流量 ${data.inputs.Q_lpm.toFixed(4)} L/min（8 K 闭合约 ${data.inputs.Q_energy_lpm.toFixed(4)}）。CPU：${c.Q_lpm.toFixed(4)} L/min，${c.V.toFixed(3)} m/s，Re ${c.Re.toFixed(0)}，压降 ${c.dP_kPa.toFixed(3)} kPa，对流热阻 ${c.R.toFixed(4)} °C/W，温升 ${c.dT_K.toFixed(2)} K。</p>
     <p>单侧内存：${m.Q_lpm.toFixed(4)} L/min，${m.V.toFixed(3)} m/s，Re ${m.Re.toFixed(0)}，压降 ${m.dP_kPa.toFixed(3)} kPa。入口孔板 4×Ø${o.four_hole_mm.toFixed(2)} mm，把 CPU 支路配到约 ${o.target_branch_kPa.toFixed(0)} kPa。</p>
     <p>面热流 CPU ${data.q_cpu_W_cm2.toFixed(2)} W/cm²，单侧内存 ${data.q_mem_W_cm2.toFixed(2)} W/cm²。</p>`;
  criteriaTable("#grace-criteria", data.criteria);
}

document.querySelector("#hbm-dpa").onclick = () => {
  document.querySelector("#hbm-point").value = "DP-A";
  document.querySelector("#hbm-Q").value = "0.40";
};
document.querySelector("#hbm-dpb").onclick = () => {
  document.querySelector("#hbm-point").value = "DP-B";
  document.querySelector("#hbm-Q").value = "0.48";
};
document.querySelector("#btn-hbm").onclick = async () => {
  try { showHbm(await api("/api/hbm/design", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(hbmPayload())})); }
  catch (err) { document.querySelector("#hbm-head").textContent = String(err.message || err); }
};
document.querySelector("#grace-base").onclick = () => { document.querySelector("#grace-Q").value = "0.5427"; };
document.querySelector("#grace-env").onclick = () => { document.querySelector("#grace-Q").value = "0.70"; };
document.querySelector("#btn-grace").onclick = async () => {
  try { showGrace(await api("/api/grace/design", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(gracePayload())})); }
  catch (err) { document.querySelector("#grace-head").textContent = String(err.message || err); }
};

async function boot() {
  const health = document.querySelector("#health");
  try {
    const h = await api("/api/health");
    health.textContent = h.venv ? "服务已连接 · CAD venv 可用" : "服务已连接 · 未找到 cad/.venv";
    tracksHtml(await api("/api/cad/tracks"));
    catalogHtml(await api("/api/catalog"));
    memoryHtml(await api("/api/memory"));
    try {
      showOned(await api("/api/oned/design", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({point: "DP-A"}),
      }));
    } catch (err) {
      document.querySelector("#oned-head").textContent = String(err.message || err);
    }
    try {
      showHbm(await api("/api/hbm/design", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({point: "DP-A"}),
      }));
    } catch (err) {
      document.querySelector("#hbm-head").textContent = String(err.message || err);
    }
    try {
      showGrace(await api("/api/grace/design", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({}),
      }));
    } catch (err) {
      document.querySelector("#grace-head").textContent = String(err.message || err);
    }
    showInspect(await api("/api/cad/inspect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    }));
  } catch (err) {
    health.textContent = "未连接服务。请运行 agent/practice01_0926/启动冷板设计台.ps1";
    gateNote.textContent = String(err.message || err);
  }
}
boot();
