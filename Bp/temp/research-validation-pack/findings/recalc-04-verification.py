import re, collections, math, os, sys

# findings/ -> research-validation-pack/ -> temp/ -> Bp/
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
HTML = os.path.join(BASE, '算力冷却_验证与决策包_v1.0_20260905.html')

print('=' * 70)
print('PART 1  HTML STRUCTURE / ENCODING / ANCHORS / LINT')
print('=' * 70)
raw = open(HTML, 'rb').read()
print('file bytes        :', len(raw))
print('has UTF-8 BOM     :', raw[:3] == b'\xef\xbb\xbf', '(should be False)')
s = raw.decode('utf-8')
print('utf-8 decode      : OK, chars =', len(s))
print('doctype first     :', s.lstrip().startswith('<!DOCTYPE html>'))
print('charset meta      :', 'charset="utf-8"' in s)
print('lang attr         :', 'lang="zh-CN"' in s)
print('viewport meta     :', 'name="viewport"' in s)
print('title present     :', '<title>' in s and '</title>' in s)

ids = re.findall(r'\sid="([^"]+)"', s)
dup = [k for k, v in collections.Counter(ids).items() if v > 1]
print('ids total/unique  :', len(ids), '/', len(set(ids)))
print('DUPLICATE IDS     :', dup if dup else 'none')

anchors = set(a[1:] for a in re.findall(r'href="(#[^"]+)"', s))
missing = sorted(a for a in anchors if a not in ids)
print('internal anchors  :', len(anchors))
print('MISSING TARGETS   :', missing if missing else 'none')
orphan = sorted(i for i in set(ids) if i not in anchors)
print('ids not linked    :', orphan)

print('-' * 70)
bad = False
for t in ['html', 'head', 'body', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
          'section', 'div', 'main', 'nav', 'header', 'ol', 'ul', 'li', 'p',
          'h2', 'h3', 'h4', 'code', 'span', 'a', 'style']:
    o = len(re.findall(r'<' + t + r'(?=[\s>])', s))
    c = len(re.findall(r'</' + t + r'>', s))
    if o != c:
        bad = True
        print(f'  MISMATCH {t:8} open={o:4} close={c:4}')
print('tag balance       :', 'FAIL (see above)' if bad else 'all balanced')

stray = set(re.findall(r'&(?!amp;|lt;|gt;|quot;|apos;|nbsp;|#\d+;|#x[0-9a-fA-F]+;)[A-Za-z#]{0,10}', s))
print('unescaped &       :', stray if stray else 'none')

# every table must have thead + tbody and consistent column counts per row group
tables = re.findall(r'<table>(.*?)</table>', s, re.S)
print('tables            :', len(tables))
prob = []
for i, t in enumerate(tables, 1):
    if '<thead>' not in t or '<tbody>' not in t:
        prob.append((i, 'missing thead/tbody'))
    head = re.search(r'<thead>(.*?)</thead>', t, re.S)
    if head:
        ncol = sum(int(re.search(r'colspan="(\d+)"', c).group(1)) if 'colspan=' in c else 1
                   for c in re.findall(r'<th[^>]*>', head.group(1)))
        for r in re.findall(r'<tr[^>]*>(.*?)</tr>', re.search(r'<tbody>(.*?)</tbody>', t, re.S).group(1), re.S):
            n = 0
            for cell in re.findall(r'<t[dh][^>]*>', r):
                m = re.search(r'colspan="(\d+)"', cell)
                n += int(m.group(1)) if m else 1
            rs = len(re.findall(r'rowspan="(\d+)"', r))
            if n != ncol and n + 1 != ncol:
                prob.append((i, f'row cols {n} vs head {ncol}'))
print('table col issues  :', prob if prob else 'none')
print('scope= on th      :', len(re.findall(r'<th[^>]*scope=', s)), '/', len(re.findall(r'<th', s)))

print()
print('=' * 70)
print('PART 2  INDEPENDENT RECALCULATION OF EVERY PUBLISHED FIGURE')
print('=' * 70)
fails = []


def chk(label, got, want, tol=0.006):
    ok = abs(got - want) <= tol * max(1.0, abs(want))
    if not ok:
        fails.append((label, got, want))
    print(f'{"OK " if ok else "FAIL"}  {label:<58} calc={got:>14,.4f}  doc={want:>14,.4f}')


print('\n-- 1.2 / 3.6  margin anchor A1 -------------------------------------')
rev, cost = 298639495.45, 267702360.46
chk('Sugon coldplate gross profit (yuan)', rev - cost, 30937134.99, 1e-9)
chk('Sugon coldplate GM %', (rev - cost) / rev * 100, 10.36, 0.001)
chk('Yingweike overseas-domestic GM gap (pct)', 52.64 - 23.83, 28.81, 1e-9)
chk('Shenling service-equipment GM gap (pct)', 31.63 - 21.46, 10.17, 1e-9)
chk('Sugon service-coldplate GM gap (pct)', 51.02 - 10.36, 40.66, 1e-9)

print('\n-- 1.5  unit-capacity price -----------------------------------------')
fs, fs_kw = 1725576.99, 6 * 420
nj, nj_kw = 4290000.0, 12 * 500
P_FS, P_NJ = fs / fs_kw, nj / nj_kw
chk('Foshan yuan/kW', P_FS, 684.75, 0.0001)
chk('Nanjing yuan/kW', P_NJ, 715.00, 1e-9)
chk('Foshan wan/unit', fs / 6 / 1e4, 28.76, 0.001)
chk('Nanjing wan/unit', nj / 12 / 1e4, 35.75, 1e-9)
chk('two-sample divergence %', (P_NJ / P_FS - 1) * 100, 4.4, 0.02)

print('\n-- 3.1  fixed cost F1 / F2 ------------------------------------------')
chk('F1 (wan/yr)', 800 - 110, 690, 1e-9)
chk('F2 (wan/yr)', 220 + 50 + 20 + 30, 320, 1e-9)
chk('F1 components sum', 220 + 115 + 130 + 95 + 50 + 30 + 50, 690, 1e-9)
chk('budget table total', 220 + 115 + 130 + 95 + 50 + 110 + 30 + 50, 800, 1e-9)
chk('NRE+prototype gated spend', 115 + 130, 245, 1e-9)

print('\n-- 3.2  cost structure ----------------------------------------------')
NONBOM = 100 + 150 + 50 + 40 + 70 + 30
chk('non-BOM yuan/kW', NONBOM, 440, 1e-9)
for b, w in ((400, 840), (650, 1090), (900, 1340)):
    chk(f'C_total @BOM={b}', b + NONBOM, w, 1e-9)
C_MID = 650 + NONBOM

print('\n-- 3.3  BOM engineering sanity range --------------------------------')
lo = 8000 + 12000 + 4000 + 5000 + 5000 + 8000 + 10000 + 5000 + 3000
hi = 20000 + 40000 + 10000 + 15000 + 15000 + 20000 + 25000 + 12000 + 10000
chk('BOM bottom-up low (yuan)', lo, 60000, 1e-9)
chk('BOM bottom-up high (yuan)', hi, 167000, 1e-9)
chk('BOM bottom-up low yuan/kW', lo / 200, 300, 1e-9)
chk('BOM bottom-up high yuan/kW', hi / 200, 835, 1e-9)

print('\n-- 3.4  contradiction #1 --------------------------------------------')
chk('840 / 715 ratio', 840 / P_NJ, 1.175, 0.001)
chk('840 / 684.75 ratio', 840 / P_FS, 1.227, 0.001)
chk('1090 / 715 ratio', 1090 / P_NJ, 1.524, 0.001)
chk('1090 / 684.75 ratio', 1090 / P_FS, 1.592, 0.001)
chk('1340 / 715 ratio', 1340 / P_NJ, 1.874, 0.001)
chk('1340 / 684.75 ratio', 1340 / P_FS, 1.957, 0.001)
chk('BOM ceiling @715 (yuan/kW)', P_NJ - NONBOM, 275, 1e-9)
chk('BOM ceiling vs mid assumption cut %', (1 - 275 / 650) * 100, 57.7, 0.01)
chk('incumbent implied cost @715 (10.36% GM)', P_NJ * (1 - 0.1036), 640.9, 0.01)
chk('incumbent implied cost @684.75', P_FS * (1 - 0.1036), 613.6, 0.01)
chk('implied/assumed ratio @715 %', P_NJ * (1 - 0.1036) / 1090 * 100, 58.8, 0.01)
chk('implied/assumed ratio @684.75 %', P_FS * (1 - 0.1036) / 1090 * 100, 56.3, 0.01)

print('\n-- 3.5  breakeven table (C_total=1090) ------------------------------')
tbl = {684.75: (-405, None, None), 715.00: (-375, None, None), 840: (-250, None, None),
       1090: (0, None, None), 1200: (110, 29.09, 62.73), 1440: (350, 9.14, 19.71),
       1500: (410, 7.80, 16.83), 1730: (640, 5.00, 10.78), 1800: (710, 4.51, 9.72)}
for p, (cm_d, be2_d, be1_d) in tbl.items():
    cm = p - C_MID
    chk(f'CM @P={p}', cm, cm_d, 0.002)
    if be2_d:
        chk(f'  BE_F2 MW @P={p}', 3.2e6 / cm / 1000, be2_d, 0.002)
        chk(f'  BE_F1 MW @P={p}', 6.9e6 / cm / 1000, be1_d, 0.002)
chk('CM rate @1200 %', 110 / 1200 * 100, 9.2, 0.01)
chk('CM rate @1440 %', 350 / 1440 * 100, 24.3, 0.01)
chk('CM rate @1500 %', 410 / 1500 * 100, 27.3, 0.01)
chk('CM rate @1730 %', 640 / 1730 * 100, 37.0, 0.01)
chk('CM rate @1800 %', 710 / 1800 * 100, 39.4, 0.01)
chk('O4: BE MW if F2 halved to 160', 1.6e6 / 410 / 1000, 3.90, 0.005)

print('\n-- 3.7  sensitivity (tornado) ---------------------------------------')
chk('ASP -20% value', 1500 * 0.8, 1200, 1e-9)
chk('ASP +20% value', 1500 * 1.2, 1800, 1e-9)
chk('ASP -20% CM', 1200 - C_MID, 110, 1e-9)
chk('ASP +20% CM', 1800 - C_MID, 710, 1e-9)
chk('ASP -20% delta %', (110 / 410 - 1) * 100, -73.2, 0.01)
chk('ASP +20% delta %', (710 / 410 - 1) * 100, 73.2, 0.01)
chk('BOM +15% value', 650 * 1.15, 747.5, 1e-9)
chk('BOM -15% value', 650 * 0.85, 552.5, 1e-9)
chk('BOM +15% CM', 1500 - (747.5 + NONBOM), 312.5, 1e-9)
chk('BOM -15% CM', 1500 - (552.5 + NONBOM), 507.5, 1e-9)
chk('BOM +15% delta %', (312.5 / 410 - 1) * 100, -23.8, 0.01)
chk('BOM -15% delta %', (507.5 / 410 - 1) * 100, 23.8, 0.01)
chk('BOM +15% BE MW', 3.2e6 / 312.5 / 1000, 10.24, 0.002)
chk('BOM -15% BE MW', 3.2e6 / 507.5 / 1000, 6.31, 0.002)
chk('ASP influence / BOM influence', 73.17 / 23.78, 3.1, 0.02)
chk('annual CM @4MW (wan)', 4000 * 410 / 1e4, 164, 1e-9)
chk('gap @4MW (wan)', 4000 * 410 / 1e4 - 320, -156, 1e-9)
chk('gap @2MW (wan)', 2000 * 410 / 1e4 - 320, -238, 1e-9)
chk('gap @6MW (wan)', 6000 * 410 / 1e4 - 320, -74, 1e-9)

print('\n-- 3.8  feasibility domain ------------------------------------------')
chk('cost above price @715 %', (840 / P_NJ - 1) * 100, 17.5, 0.02)
chk('price below floor @715 %', (1 - P_NJ / 840) * 100, 14.9, 0.02)
chk('price below floor @684.75 %', (1 - P_FS / 840) * 100, 18.5, 0.02)
chk('BE MW @P=840..1090 lower bound', 3.2e6 / 250 / 1000, 12.8, 0.01)

print('\n-- 3.9  volume reachability -----------------------------------------')
chk('Foshan MW', fs_kw / 1000, 2.52, 1e-9)
chk('Nanjing MW', nj_kw / 1000, 6.00, 1e-9)
chk('Zhejiang framework MW', 50 * 300 / 1000, 15.00, 1e-9)
chk('Zhejiang 68% share MW', 15 * 0.68, 10.2, 0.001)
chk('Zhejiang 68% annualised MW/yr', 10.2 / 2.25, 4.53, 0.01)
chk('Unicom Zhongwei MW', 48 * 500 / 1000, 24.0, 1e-9)
chk('29.09 / Nanjing', 29.09 / 6.0, 4.85, 0.002)
chk('29.09 / Zhejiang annual', 29.09 / 4.5, 6.46, 0.002)
chk('1200 above tender ceiling %', (1200 / P_NJ - 1) * 100, 67.8, 0.02)
chk('7.80 / Nanjing', 7.80 / 6.0, 1.30, 0.002)
chk('7.80 / Zhejiang annual', 7.80 / 4.5, 1.73, 0.002)

print('\n-- 4.2  liability exposure ------------------------------------------')
LIQ = 135 * 0.90
chk('liquid load per rack kW', LIQ, 121.5, 1e-9)
usd_rack = 21.2 * 135000
chk('rack server value USD', usd_rack, 2862000, 1e-9)
RACK_WAN = usd_rack * 7.2 / 1e4
chk('rack server value wan CNY', RACK_WAN, 2060.64, 0.0001)
RACKS = 200 / LIQ
chk('racks per 200kW CDU', RACKS, 1.6461, 0.001)
EXP = RACKS * RACK_WAN
chk('exposure per 200kW CDU wan', EXP, 3392.0, 0.001)
LOW = 40000 * 5 * 7.2 / 1e4
chk('low-density rack value wan', LOW, 144, 1e-9)
chk('low-density 5 racks wan', LOW * 5, 720, 1e-9)
chk('exposure reduction factor', EXP / (LOW * 5), 4.71, 0.003)

print('\n-- 4.3  ratios ------------------------------------------------------')
CV = P_NJ * 200 / 1e4
chk('contract value wan @715', CV, 14.30, 1e-9)
GPF = CV * 0.1036
chk('project gross profit wan', GPF, 1.48, 0.005)
bb_lo, bb_hi = 35000 * 7.2 / 1e4, 50000 * 7.2 / 1e4
chk('baseboard low wan', bb_lo, 25.2, 1e-9)
chk('baseboard high wan', bb_hi, 36.0, 1e-9)
chk('baseboard/contract low x', bb_lo / CV, 1.76, 0.005)
chk('baseboard/contract high x', bb_hi / CV, 2.52, 0.005)
chk('baseboard/GP low x', bb_lo / GPF, 17.0, 0.005)
chk('baseboard/GP high x', bb_hi / GPF, 24.3, 0.005)
chk('cap10 as pct of high baseboard', CV * 0.10 / bb_hi * 100, 4.0, 0.02)
chk('cap20 as pct of low baseboard', CV * 0.20 / bb_lo * 100, 11.0, 0.04)
chk('rack/contract x', RACK_WAN / CV, 144.0, 0.002)
chk('rack/GP x', RACK_WAN / GPF, 1391, 0.002)
chk('exposure/contract x', EXP / CV, 237.0, 0.002)
chk('exposure/GP x', EXP / GPF, 2290, 0.002)
chk('POD32 exposure yi', RACK_WAN * 32 / 1e4, 6.59, 0.005)
chk('POD72 exposure yi', RACK_WAN * 72 / 1e4, 14.84, 0.005)
chk('cap 10% wan', CV * 0.10, 1.43, 0.005)
chk('cap 20% wan', CV * 0.20, 2.86, 0.005)
chk('cap10/GP x', CV * 0.10 / GPF, 0.97, 0.005)
chk('cap20/GP x', CV * 0.20 / GPF, 1.93, 0.005)
chk('rack loss / stage-1 budget x', RACK_WAN / 800, 2.58, 0.005)

print('\n-- 5.2  peak cash ---------------------------------------------------')
for p, cvw, sec, pk in ((715, 71.5, 3.58, 88.6), (1200, 120.0, 6.00, 91.0), (1500, 150.0, 7.50, 92.5)):
    chk(f'contract wan/MW @P={p}', p * 1000 / 1e4, cvw, 0.001)
    chk(f'  security 5% @P={p}', 0.05 * cvw, sec, 0.005)
    chk(f'  peak cash wan/MW @P={p}', 65 + 15 + 5 + 0.05 * cvw, pk, 0.002)
PEAK = 91.0
chk('30% advance wan/MW @1200', 0.30 * 120, 36, 1e-9)
chk('peak with 30% advance', PEAK - 36, 55.0, 1e-9)
chk('peak reduction %', 36 / PEAK * 100, 39.6, 0.01)

print('\n-- 5.3  parallel capacity & throughput ------------------------------')
chk('parallel MW @110 wan', 110 / PEAK, 1.21, 0.005)
chk('parallel MW @160 wan', 160 / PEAK, 1.76, 0.005)
chk('parallel MW @800 wan', 800 / PEAK, 8.79, 0.005)
THRU = 1 * (52 / 28)
chk('annual throughput MW/yr', THRU, 1.86, 0.005)
chk('throughput / BE(7.80) %', THRU / 7.80 * 100, 23.8, 0.02)

print('\n-- 5.4 / 5.5  three cash floors ------------------------------------')
chk('B1 min cash wan', PEAK * 1 + 320 / 4, 171, 0.001)
chk('B1 board recommend wan', 171 * 1.17, 200, 0.01)
chk('B2 max parallel', math.floor(160 / PEAK), 1, 1e-9)
WK = 320 / 52
chk('recurring wan/week', WK, 6.154, 0.001)
chk('B3 delay tolerance weeks', (160 - PEAK) / WK, 11.2, 0.005)
chk('B3 with 30% advance weeks', (160 - 55) / WK, 17.1, 0.005)

print('\n-- 6.3  gate protection ratio ---------------------------------------')
chk('protection ratio', (115 + 130) / 5, 49.0, 1e-9)

print()
print('=' * 70)
if fails:
    print('RECALC FAILURES:', len(fails))
    for f in fails:
        print('   ', f)
    sys.exit(1)
print('ALL RECALCULATIONS CONSISTENT WITH PUBLISHED FIGURES')
print('=' * 70)
