import sqlite3, json

conn = sqlite3.connect(r'C:\Users\18700\.local\share\mimocode\mimocode.db')
cur = conn.cursor()

# Use 30-day cutoff (30 days * 24 * 60 * 60 * 1000 = 2592000000)
import time
now_ms = int(time.time() * 1000)
cutoff_ms = now_ms - (30 * 24 * 60 * 60 * 1000)

print("=== USER SESSIONS (non-system, last 30 days) ===")
cur.execute("""
    SELECT id, title, time_created
    FROM session
    WHERE time_created > ?
      AND title NOT LIKE '%checkpoint-writer%'
      AND title NOT LIKE '%Auto Dream%'
      AND title NOT LIKE '%Auto Distill%'
    ORDER BY time_created DESC
""", (cutoff_ms,))
sessions = cur.fetchall()
for row in sessions:
    print(f"  {row[0]} | {row[1]} | ts={row[2]}")

# Tool usage patterns across user sessions
session_ids = [s[0] for s in sessions]
if session_ids:
    placeholders = ','.join(['?' for _ in session_ids])
    print(f"\n=== TOOL USAGE PATTERNS (across {len(session_ids)} sessions) ===")
    cur.execute(f"""
        SELECT json_extract(p.data, '$.tool') as tool,
               substr(json_extract(p.data, '$.state.input'), 1, 200) as input_preview,
               count(*) as n
        FROM message m
        JOIN part p ON p.message_id = m.id
        WHERE json_extract(m.data, '$.role') = 'assistant'
          AND json_extract(p.data, '$.type') = 'tool'
          AND m.session_id IN ({placeholders})
        GROUP BY tool, input_preview
        ORDER BY n DESC
        LIMIT 50
    """, session_ids)
    for row in cur.fetchall():
        print(f"  [{row[2]}x] {row[0]}: {row[1][:120]}")

# Check message data structure
print("\n=== SAMPLE MESSAGE DATA (first user msg) ===")
cur.execute("""
    SELECT json_extract(data, '$') FROM message
    WHERE json_extract(data, '$.role') = 'user'
    LIMIT 1
""")
sample = cur.fetchone()
if sample:
    d = json.loads(sample[0]) if isinstance(sample[0], str) else sample[0]
    print(json.dumps(d, ensure_ascii=False, indent=2)[:1000])

# Check part data structure
print("\n=== SAMPLE PART DATA ===")
cur.execute("""
    SELECT json_extract(data, '$') FROM part
    LIMIT 1
""")
sample = cur.fetchone()
if sample:
    d = json.loads(sample[0]) if isinstance(sample[0], str) else sample[0]
    print(json.dumps(d, ensure_ascii=False, indent=2)[:1000])

conn.close()
