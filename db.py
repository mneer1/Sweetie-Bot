import aiomysql
from aiomysql.cursors import DictCursor
import os

db_config = {
    'host': os.getenv('MYSQLHOST'),
    'port': int(os.getenv('MYSQLPORT', 3306)),
    'user': os.getenv('MYSQLUSER'),
    'password': os.getenv('MYSQLPASSWORD'),
    'db': os.getenv('MYSQLDATABASE'),
    'autocommit': True
}

async def run_query(sql, params=(), fetch=None):
    conn = await aiomysql.connect(**db_config)
    try:
        # الحل: لا نمرر متغيرات للدالة cursor، بل نستدعيها مباشرة بناءً على الحالة
        if fetch:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(sql, params)
                if fetch == 'one':
                    result = await cur.fetchone()
                else:
                    result = await cur.fetchall()
        else:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                result = None
        
        await conn.commit()
        return result
    finally:
        conn.close()

# --- بقية الدوال كما هي ---

async def get_stats():
    result = await run_query("SELECT total, accepted, rejected FROM stats WHERE id = 1", fetch='one')
    return result if result else {"total": 0, "accepted": 0, "rejected": 0}

async def get_global_stats():
    return await get_stats()

async def get_user_stats(user_id):
    result = await run_query("SELECT total, accepted, rejected FROM stats_user WHERE user_id = %s", (user_id,), fetch='one')
    return result if result else {"total": 0, "accepted": 0, "rejected": 0}

async def update_both_stats(user_id, field):
    # تحديث العام
    await run_query(f"UPDATE stats SET total = total + 1, {field} = {field} + 1 WHERE id = 1")
    # تحديث المستخدم
    await run_query(f"""
        INSERT INTO stats_user (user_id, total, {field})
        VALUES (%s, 1, 1)
        ON DUPLICATE KEY UPDATE
        total = total + 1, {field} = {field} + 1
    """, (user_id,))

async def get_tags():
    rows = await run_query("SELECT tag_name, tag_type FROM tags", fetch='all')
    tags = {"include": [], "exclude": []}
    if rows:
        for row in rows:
            if row['tag_type'] == 'include':
                tags['include'].append(row['tag_name'])
            elif row['tag_type'] == 'exclude':
                tags['exclude'].append(row['tag_name'])
    if not tags['include']:
        tags['include'] = ["safe"]
    return tags

async def insert_tag(tag_name, tag_type):
    await run_query("INSERT INTO tags (tag_name, tag_type) VALUES (%s, %s)", (tag_name, tag_type))