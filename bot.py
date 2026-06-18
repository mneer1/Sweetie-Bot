import discord
from discord.ext import tasks, commands
import aiohttp
import json
import datetime

#  تحميل الإحصائيات
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
    def __init__(self, image_url, post_url, uploader, description):
        super().__init__(timeout=None)
        self.image_url = image_url
        self.post_url = post_url
        self.uploader = uploader
        self.description = description

    @discord.ui.button(label="قبول ✅", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        # إرسال الصورة للقناة العامة عبر الويبهوك مع اسم الناشر والوصف الأصلين
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
            embed = discord.Embed(
                title=f"منشور بواسطة: {self.uploader}", 
               # url=self.post_url, 
                description=self.description,
                color=discord.Color.green()
            )
            embed.set_image(url=self.image_url)
            await webhook.send(embed=embed)
        
        # تعطيل الأزرار بعد الضغط لمنع التكرار
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message("تم إرسال الصورة للقناة العامة.", ephemeral=False)

    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message("تم رفض الصورة وإلغاء النشر.", ephemeral=False)

# مهمة دورية لفحص الموقع كل 5 دقيقة
@tasks.loop(minutes=5)
async def fetch_derpibooru():
    channel = bot.get_channel(ADMIN_CHANNEL_ID)
    if not channel:
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
                        
                        # اقتطاع الوصف إذا تجاوز الحد الأقصى المسموح به في ديسكورد
                        if len(description) > 1000:
                            description = description[:1000] + "... [مقتطع]"
                        
                        embed = discord.Embed(
                            title=f"مراجعة صورة جديدة | الناشر: {uploader}", 
                          #  url=post_url, 
                            description=description,
                            color=discord.Color.orange()
                        )
                        embed.set_image(url=image_url)
                        
                        view = ApprovalView(image_url, post_url, uploader, description)
                        await channel.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f'البوت {bot.user} يعمل الآن!')
    fetch_derpibooru.start()

# اختبار البنق ping 
@bot.command()
async def test(ctx):
    await ctx.send("سويتي بوت تعمل بنجاح!")

#ربط الملفات
@bot.event
async def setup_hook():
    await bot.load_extension("commands.tags")
    await bot.load_extension("commands.admin")
    print("تم تحميل ملفات الأوامر بنجاح!")
bot.run(TOKEN)