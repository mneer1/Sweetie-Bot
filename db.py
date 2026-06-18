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

# --- دوال الإحصائيات ---

async def get_stats():
    result = await run_query("SELECT total, accepted, rejected FROM stats WHERE id = 1", fetch='one')
    if result:
        return {
            "total": result.get("total") or 0,
            "accepted": result.get("accepted") or 0,
            "rejected": result.get("rejected") or 0
        }
    return {"total": 0, "accepted": 0, "rejected": 0}

async def get_global_stats():
    return await get_stats()

async def get_user_stats(user_id):
    result = await run_query("SELECT total, accepted, rejected FROM stats_user WHERE user_id = %s", (user_id,), fetch='one')
    if result:
        return {
            "total": result.get("total") or 0,
            "accepted": result.get("accepted") or 0,
            "rejected": result.get("rejected") or 0
        }
    return {"total": 0, "accepted": 0, "rejected": 0}

async def update_both_stats(user_id, field):
    # تحديث العام باستخدام COALESCE لتفادي مشكلة الـ NULL
    await run_query(f"UPDATE stats SET total = COALESCE(total, 0) + 1, {field} = COALESCE({field}, 0) + 1 WHERE id = 1")
    
    # تحديد القيم الافتراضية للإدخال الأول في الجدول لتجنب ظهور NULL
    accepted_val = 1 if field == "accepted" else 0
    rejected_val = 1 if field == "rejected" else 0
    
    # تحديث المستخدم
    await run_query(f"""
        INSERT INTO stats_user (user_id, total, accepted, rejected)
        VALUES (%s, 1, {accepted_val}, {rejected_val})
        ON DUPLICATE KEY UPDATE
        total = COALESCE(total, 0) + 1, {field} = COALESCE({field}, 0) + 1
    """, (user_id,))

# --- دوال التاغات (تم تحديثها) ---

async def get_tags():
    rows = await run_query("SELECT tag_name, tag_type FROM tags", fetch='all')
    tags = {"include": [], "exclude": []}
    if rows:
        for row in rows:
            if row['tag_type'] == 'include':
                tags['include'].append(row['tag_name'])
            elif row['tag_type'] == 'exclude':
                tags['exclude'].append(row['tag_name'])
    
    # وضع safe كافتراضي إذا لم يكن هناك تاغات مطلوبة
    if not tags['include']:
        tags['include'] = ["safe"]
    return tags

async def insert_tag(tag_name, tag_type):
    # نقوم بحذف التاغ أولاً إذا كان موجوداً لمنع تكراره في الجدول (لتفادي الأخطاء)
    await run_query("DELETE FROM tags WHERE tag_name = %s", (tag_name,))
    # ثم نقوم بإدخاله بالنوع الجديد (include أو exclude)
    await run_query("INSERT INTO tags (tag_name, tag_type) VALUES (%s, %s)", (tag_name, tag_type))

async def delete_tag(tag_name):
    # دالة جديدة لحذف التاغ كلياً من قاعدة البيانات عند الحاجة
    await run_query("DELETE FROM tags WHERE tag_name = %s", (tag_name,))