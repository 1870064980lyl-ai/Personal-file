import sqlite3, json

conn = sqlite3.connect(r'C:\Users\18700\.local\share\mimocode\mimocode.db')
cur = conn.cursor()

# Check task table
print("=== TASKS ===")
cur.execute("SELECT id, session_id, title, status FROM task ORDER BY time_created DESC LIMIT 20")
for row in cur.fetchall():
    print(f"  {row}")

# Check task_event table
print("\n=== TASK EVENTS ===")
cur.execute("SELECT id, task_id, type, substr(data, 1, 200) FROM task_event ORDER BY time_created DESC LIMIT 20")
for row in cur.fetchall():
    print(f"  {row}")

# Check all sessions (not just 30-day) for patterns
print("\n=== ALL SESSIONS (chronological) ===")
cur.execute("SELECT id, title, datetime(time_created/1000, 'unixepoch', 'localtime') as created FROM session WHERE title NOT LIKE '%checkpoint-writer%' ORDER BY time_created")
for row in cur.fetchall():
    print(f"  {row[2]} | {row[0]} | {row[1]}")

# Check workflow_run
print("\n=== WORKFLOW RUNS ===")
cur.execute("SELECT id, session_id, name, status FROM workflow_run LIMIT 10")
for row in cur.fetchall():
    print(f"  {row}")

conn.close()
