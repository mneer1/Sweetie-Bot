import aiomysql
import os

db_config = {
    'host': os.getenv('MYSQLHOST'),
    'port': int(os.getenv('MYSQLPORT', 3306)),
    'user': os.getenv('MYSQLUSER'),
    'password': os.getenv('MYSQLPASSWORD'),
    'db': os.getenv('MYSQLDATABASE')
}

async def update_stats(accepted_inc, rejected_inc):
    conn = await aiomysql.connect(**db_config)
    async with conn.cursor() as cur:
        await cur.execute(
            "UPDATE stats SET total = total + %s, accepted = accepted + %s, rejected = rejected + %s WHERE id = 1",
            (accepted_inc + rejected_inc, accepted_inc, rejected_inc)
        )
        await conn.commit()
    conn.close()

async def get_stats():
    conn = await aiomysql.connect(**db_config)
    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute("SELECT * FROM stats WHERE id = 1")
        result = await cur.fetchone()
    conn.close()
    return result

async def insert_tag(tag_name, tag_type):
    conn = await aiomysql.connect(**db_config)
    async with conn.cursor() as cur:
        await cur.execute("INSERT INTO tags (tag_name, tag_type) VALUES (%s, %s)", (tag_name, tag_type))
        await conn.commit()
    conn.close()