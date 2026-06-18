import discord
from discord.ext import tasks, commands
import aiohttp
import json
import datetime

#  تحميل الإحصائيات و عمل ملف ستاس مؤقت على الاستضافة فقط (مهم جدا) يجب تعديله عن توافر داتا بيس 
def load_stats():
    try:
        with open("stats.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"total": 0, "accepted": 0, "rejected": 0, "admins": {}}

#  حفظ الإحصائيات
def save_stats(stats):
    with open("stats.json", "w") as f:
        json.dump(stats, f)

stats_data = load_stats()

# من config 
from config import TOKEN, WEBHOOK_URL, ADMIN_CHANNEL_ID
from derpibooru import get_api_url
# ================= إعدادات البوت ================
#TOKEN = os.getenv("DISCORD_BOT_TOKEN")
#WEBHOOK_URL = os.getenv("WEBHOOK_URL")
#ADMIN_CHANNEL_ID = 1516219570694652006 # استبدله بـ ID قناة الإدارة
API_URL = 'https://derpibooru.org/api/v1/json/search/images?q=safe&sf=created_at&sd=desc'
# =================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# لتخزين أرقام الصور (IDs) التي تم إرسالها لتجنب التكرار
sent_images = set()

# واجهة أزرار التحكم (القبول والرفض)
class ApprovalView(discord.ui.View):
    def __init__(self, image_url, post_url, uploader, description, created_at):
        super().__init__(timeout=None)
        self.image_url = image_url
        self.post_url = post_url
        self.uploader = uploader
        self.description = description
        self.created_at = created_at # استلام تاريخ النشر

    @discord.ui.button(label="قبول ✅", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        admin_id = str(interaction.user.id)
        admin_name = interaction.user.display_name
        
        # تحديث الإحصائيات
        stats_data["total"] += 1
        stats_data["accepted"] += 1
        if admin_id not in stats_data["admins"]:
            stats_data["admins"][admin_id] = {"name": admin_name, "accepted": 0, "rejected": 0}
        stats_data["admins"][admin_id]["accepted"] += 1
        save_stats(stats_data)

        # تجهيز رسالة العامة
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
            embed = discord.Embed(
                title=f"منشور بواسطة: {self.uploader}", 
                description=self.description,
                color=discord.Color.green()
            )
            embed.add_field(name="📅 تاريخ النشر", value=self.created_at)
            embed.set_image(url=self.image_url)
            
            # إنشاء زر التنزيل للمستخديمن
            public_view = discord.ui.View()
            public_view.add_item(discord.ui.Button(label="📥 تنزيل الرسمة", url=self.image_url))
            
            await webhook.send(embed=embed, view=public_view)
        
        # تحويل رسالة الإدارة إلى سجل (Log)
        for child in self.children:
            child.disabled = True
        
        log_embed = interaction.message.embeds[0]
        log_embed.color = discord.Color.green()
        log_embed.set_footer(text=f"✅ تم القبول بواسطة: {admin_name}")
        
        await interaction.message.edit(embed=log_embed, view=self)
        await interaction.response.send_message("تم إرسال الصورة للقناة العامة.", ephemeral=True)

    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        admin_id = str(interaction.user.id)
        admin_name = interaction.user.display_name
        
        stats_data["total"] += 1
        stats_data["rejected"] += 1
        if admin_id not in stats_data["admins"]:
            stats_data["admins"][admin_id] = {"name": admin_name, "accepted": 0, "rejected": 0}
        stats_data["admins"][admin_id]["rejected"] += 1
        save_stats(stats_data)

        for child in self.children:
            child.disabled = True
            
        log_embed = interaction.message.embeds[0]
        log_embed.color = discord.Color.red()
        log_embed.set_footer(text=f"❌ تم الرفض بواسطة: {admin_name}")
        
        await interaction.message.edit(embed=log_embed, view=self)
        await interaction.response.send_message("تم الرفض وتحديث السجل.", ephemeral=True)

# مهمة دورية لفحص الموقع كل 5 دقيقة
@tasks.loop(minutes=5)
async def fetch_derpibooru():
    await bot.wait_until_ready() # 👈 انتظار البوت حتى يحمل القنوات بالكامل
    
    # 👈 تحويل الـ ID إلى رقم (int) تحسباً لوجود علامات تنصيص بالخطأ في config
    channel = bot.get_channel(int(ADMIN_CHANNEL_ID)) 
    if not channel:
        print(f"⚠️ تحذير: لم يتم العثور على القناة رقم {ADMIN_CHANNEL_ID}. تأكد من الرقم وصلاحيات البوت.")
        return
        
    current_api_url = get_api_url()
    async with aiohttp.ClientSession() as session:
        async with session.get(current_api_url) as response:
            if response.status == 200:
                data = await response.json()
                images = data.get('images', [])
                
                # نأخذ أحدث 3 صور ومعالجتها من الأقدم للأحدث داخل الثلاثة
                for img in reversed(images[:3]):
                    img_id = img['id']
                    
                    if img_id not in sent_images:
                        sent_images.add(img_id)
                        
                        # جلب الروابط وتأمين جودة الصورة
                        image_url = img['representations'].get('large') or img['view_url']
                        post_url = f"https://derpibooru.org/images/{img_id}"
                        
                        # سحب اسم الناشر والوصف مع التعامل مع حالات عدم وجودهما
                        uploader = img.get('uploader') or "مجهول"
                        description = img.get('description') or "لا يوجد وصف."
                        created_at = img.get('created_at', 'غير معروف')[:10]
                        
                        if len(description) > 1000:
                            description = description[:1000] + "... [مقتطع]"
                        
                        embed = discord.Embed(
                            title=f"مراجعة صورة جديدة | الناشر: {uploader}", 
                            description=description,
                            color=discord.Color.orange()
                        )
                        embed.set_image(url=image_url)
                        embed.add_field(name=" تاريخ النشر", value=created_at)
                        
                        view = ApprovalView(image_url, post_url, uploader, description, created_at)
                        await channel.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f'البوت {bot.user} يعمل الآن!')
    fetch_derpibooru.start()

# اختبار البنق ping 
@bot.command()
async def test(ctx):
    await ctx.send("سويتي بوت تعمل بنجاح!")
    print(get_api_url())

#ربط الملفات
@bot.event
async def setup_hook():
    await bot.load_extension("commands.tags")
    await bot.load_extension("commands.admin")
    await bot.load_extension("commands.stats_and_legendary")
    print("تم تحميل ملفات الأوامر بنجاح!")
bot.run(TOKEN)