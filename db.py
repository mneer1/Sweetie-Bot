import aiomysql
import os

db_config = {
    'host': os.getenv('MYSQLHOST'),
    'port': int(os.getenv('MYSQLPORT', 3306)),
    'user': os.getenv('MYSQLUSER'),
    'password': os.getenv('MYSQLPASSWORD'),
    'db': os.getenv('MYSQLDATABASE')
}

async def get_connection():
    return await aiomysql.connect(**db_config)

async def update_stats(accepted_inc, rejected_inc):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            "UPDATE stats SET total = total + %s, accepted = accepted + %s, rejected = rejected + %s WHERE id = 1",
            (accepted_inc + rejected_inc, accepted_inc, rejected_inc)
        )
        await conn.commit()
    conn.close()

async def get_tags():
    # نبدأ بقائمة فارغة، والـ API سيتولى البحث إذا لم نرسل شيئاً، أو نضع default واحد
    tags = {"include": [], "exclude": []}
    conn = await get_connection()
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute("SELECT tag_name, tag_type FROM tags")
        rows = await cur.fetchall()
        for row in rows:
            if row['tag_type'] == 'include':
                tags['include'].append(row['tag_name'])
            elif row['tag_type'] == 'exclude':
                tags['exclude'].append(row['tag_name'])
    conn.close()
    
    # إضافة safe إذا كانت القائمة فارغة
    if not tags['include']:
        tags['include'] = ["safe"]
        
    return tags

async def insert_tag(tag_name, tag_type):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute("INSERT INTO tags (tag_name, tag_type) VALUES (%s, %s)", (tag_name, tag_type))
        await conn.commit()
    conn.close()