# الان داخل الموقع نقدر نضيف و نطرح تاغات المواضع من نفس الاي بي اي يعني تحكم افضل في المحتوى 
#في هذه التحديث تم انشاء هذه الملف من اجل الموقع  و ان لا يكون الي بي اي داخل الكود الرئيسي 
# و يجب ان يحتوي تحديث 0.1 على متغيرات تسمح لك بتعدل الي بي اي من دون تحديث الكود كل مرة 
import config

def get_api_url():
    # تجهيز التاغات المطلوبة
    query_parts = [tag.replace(" ", "+") for tag in config.INCLUDE_TAGS]
    
    # إضافة علامة السالب (-) للتاغات المراد استبعادها
    for tag in config.EXCLUDE_TAGS:
        query_parts.append(f"-{tag.replace(' ', '+')}")
    
    # ربط التاغات بترميز الفاصلة الخاص بالروابط %2C+
    query_string = "%2C+".join(query_parts)
    
    return f'https://derpibooru.org/api/v1/json/search/images?q={query_string}&sf=created_at&sd=desc'