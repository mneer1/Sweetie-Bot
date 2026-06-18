# الان داخل الموقع نقدر نضيف و نطرح تاغات المواضع من نفس الاي بي اي يعني تحكم افضل في المحتوى 
#في هذه التحديث تم انشاء هذه الملف من اجل الموقع  و ان لا يكون الي بي اي داخل الكود الرئيسي 
# و يجب ان يحتوي تحديث 0.1 على متغيرات تسمح لك بتعدل الي بي اي من دون تحديث الكود كل مرة 
import config
import urllib.parse

def get_api_url():
    query_parts = []

    # التاغات المطلوبة
    query_parts.extend(config.INCLUDE_TAGS)

    # التاغات المستبعدة
    for tag in config.EXCLUDE_TAGS:
        query_parts.append(f"-{tag}")

    # يجب ألا يكون هناك مسافة بعد الفاصلة
    query = ",".join(query_parts)

    # تشفير الرابط لتجنب مشاكل المسافات والرموز
    safe_query = urllib.parse.quote(query)

    return (
        "https://derpibooru.org/api/v1/json/search/images"
        f"?q={safe_query}&sf=created_at&sd=desc"
    )