import urllib.parse
import db

async def get_api_url():
    # 1. جلب البيانات من القاعدة بدلاً من config
    tags = await db.get_tags()
    query_parts = []

    # 2. إضافة التاغات المطلوبة
    query_parts.extend(tags["include"])

    # 3. إضافة التاغات المحظورة مع علامة الناقص (-)
    for tag in tags["exclude"]:
        query_parts.append(f"-{tag}")

    query = ",".join(query_parts)
    safe_query = urllib.parse.quote(query)

    return (
        "https://derpibooru.org/api/v1/json/search/images"
        f"?q={safe_query}&sf=created_at&sd=desc"
    )