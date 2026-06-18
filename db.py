import aiomysql
import os

# إعدادات الاتصال (يتم سحبها من المتغيرات البيئية)
db_config = {
    'host': os.getenv('MYSQLHOST'),
    'port': int(os.getenv('MYSQLPORT', 3306)),
    'user': os.getenv('MYSQLUSER'),
    'password': os.getenv('MYSQLPASSWORD'),
    'db': os.getenv('MYSQLDATABASE'),
    'autocommit': True
}

# دالة مساعدة لتنفيذ الاستعلامات (تضمن إغلاق الاتصال بأمان)
async def run_query(sql, params=(), fetch=None):
    conn = await aiomysql.connect(**db_config)
    try:
        async with conn.cursor(aiomysql.DictCursor if fetch else None) as cur:
            await cur.execute(sql, params)
            # تحديد طريقة جلب البيانات
            if fetch == 'one':
                result = await cur.fetchone()
            elif fetch == 'all':
                result = await cur.fetchall()
            else:
                result = None
            await conn.commit()
            return result
    finally:
        # هذه الخطوة مهمة جداً لإغلاق الاتصال ومنع تعليق البوت
        conn.close()

# جلب الإحصائيات العامة
async def get_stats():
    result = await run_query("SELECT total, accepted, rejected FROM stats WHERE id = 1", fetch='one')
    return result if result else {"total": 0, "accepted": 0, "rejected": 0}

# دالة مطابقة للاسم الذي تستخدمه في الأوامر
async def get_global_stats():
    return await get_stats()

# جلب إحصائيات مستخدم محدد
async def get_user_stats(user_id):
    result = await run_query("SELECT total, accepted, rejected FROM stats_user WHERE user_id = %s", (user_id,), fetch='one')
    return result if result else {"total": 0, "accepted": 0, "rejected": 0}

# تحديث الإحصائيات (العامة + المستخدم)
async def update_both_stats(user_id, field):
    # تحديث الجدول العام
    # ملاحظة: field هنا سيكون إما "accepted" أو "rejected"
    await run_query(f"UPDATE stats SET total = total + 1, {field} = {field} + 1 WHERE id = 1")
    
    # تحديث جدول المستخدم
    await run_query(f"""
        INSERT INTO stats_user (user_id, total, {field})
        VALUES (%s, 1, 1)
        ON DUPLICATE KEY UPDATE
        total = total + 1, {field} = {field} + 1
    """, (user_id,))

# جلب التاغات
async def get_tags():
    rows = await run_query("SELECT tag_name, tag_type FROM tags", fetch='all')
    tags = {"include": [], "exclude": []}
    
    if rows:
        for row in rows:
            if row['tag_type'] == 'include':
                tags['include'].append(row['tag_name'])
            elif row['tag_type'] == 'exclude':
                tags['exclude'].append(row['tag_name'])
    
    # قيمة افتراضية في حال كانت فارغة
    if not tags['include']:
        tags['include'] = ["safe"]
        
    return tags

# إضافة تاغ جديد
async def insert_tag(tag_name, tag_type):
    await run_query("INSERT INTO tags (tag_name, tag_type) VALUES (%s, %s)", (tag_name, tag_type))