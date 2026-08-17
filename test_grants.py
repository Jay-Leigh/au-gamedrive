import psycopg

conn = psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname="universal-signal-gateway-db",
    user="jay-leigh",
    password="PF[5+Ec|7%[@pP-T",
)
cur = conn.cursor()
for table in ("audit_logs", "checkpoint_logs", "conversion_logs"):
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        print(table, "OK", cur.fetchone())
    except Exception as e:
        print(table, "FAILED:", e)
    conn.rollback()