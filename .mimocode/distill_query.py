import sqlite3, json, sys

conn = sqlite3.connect(r'C:\Users\18700\.local\share\mimocode\mimocode.db')
cur = conn.cursor()

# 1. List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("=== TABLES ===")
print(tables)

# 2. Recent sessions
print("\n=== RECENT SESSIONS (last 30) ===")
cur.execute("SELECT id, title, time_created FROM session ORDER BY time_created DESC LIMIT 30")
for row in cur.fetchall():
    sid, title, ts = row
    print(f"  {sid} | {title} | ts={ts}")

# 3. Session schema
print("\n=== SCHEMA: session ===")
cur.execute("PRAGMA table_info(session)")
for row in cur.fetchall():
    print(f"  {row}")

print("\n=== SCHEMA: message ===")
cur.execute("PRAGMA table_info(message)")
for row in cur.fetchall():
    print(f"  {row}")

print("\n=== SCHEMA: part ===")
cur.execute("PRAGMA table_info(part)")
for row in cur.fetchall():
    print(f"  {row}")

conn.close()
