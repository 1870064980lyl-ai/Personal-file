import sqlite3, json

conn = sqlite3.connect(r'C:\Users\18700\.local\share\mimocode\mimocode.db')
cur = conn.cursor()

# Get full assistant message chains for the archival sessions
sessions_to_inspect = [
    'ses_11ed093ffffeTYgw7JTSluMdNB',  # 创建2026-6文件夹整理审稿文件
    'ses_11a5870c1ffe79ZBMv6QMTO4fS',  # TAML期刊审稿文件夹创建及文件整理
    'ses_0c34c2cc5ffeZQQzBPy2304yUQ',  # 证书文件整理及笔记链接
]

for sid in sessions_to_inspect:
    print(f"\n{'='*80}")
    print(f"SESSION: {sid}")
    print(f"{'='*80}")
    
    # Get all messages in order
    cur.execute("""
        SELECT m.id, json_extract(m.data, '$.role') as role, m.time_created
        FROM message m
        WHERE m.session_id = ?
        ORDER BY m.time_created
    """, (sid,))
    messages = cur.fetchall()
    
    for msg_id, role, ts in messages:
        # Get parts for this message
        cur.execute("""
            SELECT json_extract(p.data, '$.type') as ptype,
                   json_extract(p.data, '$.text') as text,
                   json_extract(p.data, '$.tool') as tool,
                   json_extract(p.data, '$.state.input') as tool_input,
                   json_extract(p.data, '$.state.output') as tool_output
            FROM part p
            WHERE p.message_id = ?
            ORDER BY p.time_created
        """, (msg_id,))
        parts = cur.fetchall()
        
        for ptype, text, tool, tool_input, tool_output in parts:
            if ptype == 'text' and text:
                preview = text[:300].replace('\n', ' ')
                print(f"\n  [{role}] {preview}")
            elif ptype == 'tool' and tool:
                inp_preview = (tool_input or '')[:200].replace('\n', ' ')
                print(f"  [{role}] TOOL:{tool} -> {inp_preview}")

conn.close()
