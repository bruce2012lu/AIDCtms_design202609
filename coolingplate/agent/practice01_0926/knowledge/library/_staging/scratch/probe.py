import sqlite3
print(sqlite3.sqlite_version)
c = sqlite3.connect(':memory:')
c.execute("create virtual table t using fts5(x, tokenize='trigram')")
c.execute("insert into t values('微射流冲击冷板 jet impingement')")
print(c.execute("select x from t where t match '射流冲'").fetchall())
print(c.execute("select x from t where t match 'impinge'").fetchall())
try:
    import jsonschema
    print('jsonschema', jsonschema.__version__)
except Exception:
    print('no jsonschema')
import fitz
print('find_tables', hasattr(fitz.Page, 'find_tables'))
