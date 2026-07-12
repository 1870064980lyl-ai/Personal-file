import sqlite3, json

conn = sqlite3.connect(r'C:\Users\18700\.local\share\mimocode\mimocode.db')
cur = conn.cursor()

import time
now_ms = int(time.time() * 1000)
cutoff_ms = now_ms - (30 * 24 * 60 * 60 * 1000)

# Get all user session IDs
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
session_ids = [s[0] for s in sessions]
placeholders = ','.join(['?' for _ in session_ids])

# 1. User messages per session (to understand what tasks were asked)
print("=== USER TASK DESCRIPTIONS (per session) ===")
for sid, title, ts in sessions:
    cur.execute(f"""
        SELECT substr(json_extract(p.data, '$.text'), 1, 300)
        FROM message m
        JOIN part p ON p.message_id = m.id
        WHERE m.session_id = ?
          AND json_extract(m.data, '$.role') = 'user'
          AND json_extract(p.data, '$.type') = 'text'
        LIMIT 3
    """, (sid,))
    msgs = cur.fetchall()
    print(f"\n[{title}]")
    for msg in msgs:
        if msg[0]:
            print(f"  -> {msg[0][:250]}")

# 2. Repeated bash command patterns (deduplicated)
print("\n\n=== DEDUPLICATED BASH COMMANDS ===")
cur.execute(f"""
    SELECT substr(json_extract(p.data, '$.state.input'), 1, 300) as cmd,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') = 'bash'
      AND m.session_id IN ({placeholders})
    GROUP BY cmd
    ORDER BY n DESC
    LIMIT 30
""", session_ids)
for row in cur.fetchall():
    print(f"  [{row[1]}x] {row[0][:200]}")

# 3. Repeated file operations (write/edit)
print("\n\n=== REPEATED WRITE/EDIT TARGETS ===")
cur.execute(f"""
    SELECT json_extract(p.data, '$.tool') as tool,
           substr(json_extract(p.data, '$.state.input'), 1, 300) as input,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') IN ('write', 'edit')
      AND m.session_id IN ({placeholders})
    GROUP BY tool, input
    HAVING n > 1
    ORDER BY n DESC
""", session_ids)
for row in cur.fetchall():
    print(f"  [{row[2]}x] {row[0]}: {row[1][:200]}")

# 4. Repeated file read targets
print("\n\n=== REPEATED FILE READS ===")
cur.execute(f"""
    SELECT substr(json_extract(p.data, '$.state.input'), 1, 300) as input,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') = 'read'
      AND m.session_id IN ({placeholders})
    GROUP BY input
    HAVING n > 2
    ORDER BY n DESC
""", session_ids)
for row in cur.fetchall():
    print(f"  [{row[1]}x] {row[0][:200]}")

conn.close()
