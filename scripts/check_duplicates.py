import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

c.execute("SELECT title, count(*) FROM jobs GROUP BY title HAVING count(*) > 1")
dups = c.fetchall()
print(f"Total duplicate title groups: {len(dups)}")
for title, cnt in dups:
    print(f"Title: {title} | Count: {cnt}")
    c.execute("SELECT id, source_url, company_id, is_active FROM jobs WHERE title = ?", (title,))
    for row in c.fetchall():
        print(f"   ID: {row[0]} | Active: {row[3]} | URL: {row[1]}")

conn.close()
