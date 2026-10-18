import json
import sqlite3
import os

db_path = 'backend/cdata.db'
if not os.path.exists(db_path):
    print('DB not found:', db_path)
    exit()

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check count before
cur.execute('SELECT COUNT(*) FROM jobs')
print('Old jobs in DB:', cur.fetchone()[0])

# Delete synthetic and broken jobs from DB
cur.execute("DELETE FROM jobs WHERE id LIKE 'local_ent_%' OR source_platform LIKE '%Facebook%' OR source_url LIKE '%tuyendung.sungroup%' OR source_url LIKE '%tuyendung.viettel%' OR source_url LIKE '%tuyendung.vingroup%'")
conn.commit()

cur.execute('SELECT COUNT(*) FROM jobs')
print('Remaining jobs in DB after purge:', cur.fetchone()[0])

with open('frontend/public/data/jobs.json', 'r', encoding='utf-8') as f:
    clean_jobs = json.load(f)

for j in clean_jobs:
    jid = j['id']
    s_url = j.get('source_url')
    cur.execute('SELECT id FROM jobs WHERE id = ? OR source_url = ?', (jid, s_url))
    row = cur.fetchone()
    if row:
        cur.execute('''
            UPDATE jobs SET
                title = ?, company_name = ?, location_province = ?, location_district = ?,
                location_full = ?, salary_text = ?, job_type = ?, category = ?, experience_level = ?,
                source_platform = ?, source_name = ?, apply_url = ?, is_active = 1,
                status = 'active_confirmed', last_verified_at = ?
            WHERE id = ?
        ''', (
            j.get('title'), j.get('company_name'), j.get('location_province'), j.get('location_district'),
            j.get('location_full'), j.get('salary_text'), j.get('job_type'), j.get('category'), j.get('experience_level'),
            j.get('source_platform'), j.get('source_name'), j.get('apply_url'),
            j.get('last_verified_at'), row[0]
        ))
    else:
        cur.execute('''
            INSERT INTO jobs (
                id, title, company_name, location_province, location_district,
                location_full, salary_text, job_type, category, experience_level,
                source_platform, source_name, source_url, apply_url, is_active,
                status, last_verified_at, posted_at, crawled_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'active_confirmed', ?, ?, ?)
        ''', (
            jid, j.get('title'), j.get('company_name'), j.get('location_province'), j.get('location_district'),
            j.get('location_full'), j.get('salary_text'), j.get('job_type'), j.get('category'), j.get('experience_level'),
            j.get('source_platform'), j.get('source_name'), s_url, j.get('apply_url'),
            j.get('last_verified_at'), j.get('posted_at'), j.get('posted_at')
        ))

conn.commit()
cur.execute('SELECT COUNT(*) FROM jobs WHERE is_active = 1')
print('Final active clean jobs in DB:', cur.fetchone()[0])
conn.close()
