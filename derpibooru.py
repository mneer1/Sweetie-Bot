import urllib.parse
import db

async def get_api_url():
    tags = await db.get_tags()
    include = tags.get("include", ["safe"])
    exclude = tags.get("exclude", [])

    # تأكد من وجود safe إذا كانت القائمة فارغة
    if not include:
        include = ["safe"]

    query_parts = include + [f"-{tag}" for tag in exclude]
    query = ",".join(query_parts)
    safe_query = urllib.parse.quote(query)

    return (
        "https://derpibooru.org/api/v1/json/search/images"
        f"?q={safe_query}&sf=created_at&sd=desc"
    )