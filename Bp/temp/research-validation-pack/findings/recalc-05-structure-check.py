import re, os, glob

BASE = r'D:\agents2026\agents2026\agents\AIDCtms\Bp'
HTML = os.path.join(BASE, '算力冷却_验证与决策包_v1.0_20260905.html')

print('=' * 68)
print('CSS CLASS INTEGRITY (every class used must be defined)')
print('=' * 68)
s = open(HTML, encoding='utf-8').read()
style = re.search(r'<style>(.*?)</style>', s, re.S).group(1)
defined = set(re.findall(r'\.([a-zA-Z][\w-]*)', style))
body = s[s.index('</style>'):]
used = set()
for attr in re.findall(r'class="([^"]+)"', body):
    used.update(attr.split())
undef = sorted(used - defined)
print('classes defined :', len(defined))
print('classes used    :', len(used))
print('UNDEFINED USED  :', undef if undef else 'none')
print('unused defined  :', sorted(defined - used - {'page-break'}))

print()
print('=' * 68)
print('MARKDOWN TOOLKIT + FINDINGS CHECK')
print('=' * 68)
files = sorted(glob.glob(os.path.join(BASE, 'tools', '*.md'))) + \
        sorted(glob.glob(os.path.join(BASE, 'temp', 'research-validation-pack', 'findings', '*.md')))
allok = True
for f in files:
    raw = open(f, 'rb').read()
    t = raw.decode('utf-8')
    lines = t.split('\n')
    # markdown table integrity: header row followed by separator with matching pipe count
    tbl_bad = []
    for i, ln in enumerate(lines):
        if re.match(r'^\s*\|.*\|\s*$', ln) and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
            ncol = ln.count('|') - 1
            sep = lines[i + 1].count('|') - 1
            if ncol != sep:
                tbl_bad.append((i + 1, ncol, sep))
            j = i + 2
            while j < len(lines) and re.match(r'^\s*\|.*\|\s*$', lines[j]):
                if lines[j].count('|') - 1 != ncol:
                    tbl_bad.append((j + 1, lines[j].count('|') - 1, ncol))
                j += 1
    fences = t.count('```')
    h1 = len([l for l in lines if l.startswith('# ')])
    ok = (not tbl_bad) and fences % 2 == 0 and raw[:3] != b'\xef\xbb\xbf'
    allok &= ok
    ntbl = len(re.findall(r'\n\|[^\n]*\|\n\s*\|[-: |]+\|', t))
    nobom = raw[:3] != b'\xef\xbb\xbf'
    print()
    print(os.path.basename(f))
    print('  bytes=%7d  lines=%5d  h1=%d  tables=%d' % (len(raw), len(lines), h1, ntbl))
    print('  utf8 no BOM   :', nobom)
    print('  code fences   : %d (%s)' % (fences, 'balanced' if fences % 2 == 0 else 'UNBALANCED'))
    print('  table issues  :', tbl_bad if tbl_bad else 'none')
    print('  RESULT        :', 'OK' if ok else 'FAIL')

print()
print('=' * 68)
print('ALL MARKDOWN OK' if allok else 'MARKDOWN PROBLEMS FOUND')
print('=' * 68)
