import discord
from discord.ext import tasks, commands
import aiohttp
import db  # نستدعي ملف قاعدة البيانات

from config import TOKEN, WEBHOOK_URL, ADMIN_CHANNEL_ID
from derpibooru import get_api_url

API_BASE_URL = "https://derpibooru.org/api/v1/json/search/images"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

sent_images = set()

class ApprovalView(discord.ui.View):
    def __init__(self, image_url, uploader, description):
        super().__init__(timeout=None)
        self.image_url = image_url
        self.uploader = uploader
        self.description = description

    async def _finalize(self, interaction: discord.Interaction, accepted: bool, admin_name: str, public_text: str):
        for child in self.children:
            child.disabled = True

        if interaction.message.embeds:
            log_embed = interaction.message.embeds[0]
            log_embed.color = discord.Color.green() if accepted else discord.Color.red()
            log_embed.set_footer(
                text=f"{'✅' if accepted else '❌'} تم {'القبول' if accepted else 'الرفض'} بواسطة: {admin_name}"
            )
            await interaction.message.edit(embed=log_embed, view=self)

        await interaction.message.reply(public_text, mention_author=False)

    @discord.ui.button(label="قبول ✅", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        # تحديث قاعدة البيانات بدلاً من الملف
        await db.update_stats(accepted_inc=1, rejected_inc=0)
        
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
            embed = discord.Embed(
                title=f"منشور بواسطة: {self.uploader}",
                description=self.description,
                color=discord.Color.green(),
            )
            embed.set_image(url=self.image_url)
            await webhook.send(embed=embed)

        await self._finalize(
            interaction,
            accepted=True,
            admin_name=interaction.user.display_name,
            public_text=f"✅ تم قبول هذا المنشور بواسطة {interaction.user.display_name}",
        )

    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        # تحديث قاعدة البيانات بدلاً من الملف
        await db.update_stats(accepted_inc=0, rejected_inc=1)

        await self._finalize(
            interaction,
            accepted=False,
            admin_name=interaction.user.display_name,
            public_text=f"❌ تم رفض هذا المنشور بواسطة {interaction.user.display_name}",
        )

@tasks.loop(minutes=5)
async def fetch_derpibooru():
    await bot.wait_until_ready()
    print("بدأ البحث عن صور جديدة...") # لنتأكد أنه يعمل

    try:
        # جلب التاغات
        tags = await db.get_tags()
        print(f"التاغات المسترجعة: {tags}") # للتأكد أن قاعدة البيانات ترسل بيانات

        query_string = ",".join(tags.get("include", ["safe"]) + [f"-{t}" for t in tags.get("exclude", [])])
        print(f"استعلام API: {query_string}")

        params = {"q": query_string, "sf": "created_at", "sd": "desc", "per_page": 3}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(API_BASE_URL, params=params) as response:
                print(f"حالة اتصال API: {response.status}")
                if response.status != 200:
                    print(f"فشل الاتصال بـ API: {await response.text()}")
                    return

                data = await response.json()
                images = data.get("images", [])
                print(f"عدد الصور المجلوبة: {len(images)}")

                for img in reversed(images):
                    # ... (باقي كود إرسال الصورة كما هو)
                    # تأكد أنك تستخدم نفس الكود الذي كان لديك في هذه الجزئية
                    img_id = img.get("id")
                    if img_id is None or img_id in sent_images:
                        continue
                    
                    sent_images.add(img_id)
                    image_url = img.get("representations", {}).get("large") or img.get("view_url")
                    uploader = img.get("uploader") or "مجهول"
                    description = (img.get("description") or "لا يوجد وصف.")[:1000]

                    channel = bot.get_channel(int(ADMIN_CHANNEL_ID)) or await bot.fetch_channel(int(ADMIN_CHANNEL_ID))
                    embed = discord.Embed(title=f"مراجعة: {uploader}", description=description, color=discord.Color.orange())
                    embed.set_image(url=image_url)
                    await channel.send(embed=embed, view=ApprovalView(image_url, uploader, description))

    except Exception as e:
        print(f"خطأ غير متوقع في fetch_derpibooru: {e}")

@bot.event
async def on_ready():
    print(f"البوت {bot.user} يعمل الآن!")
    if not fetch_derpibooru.is_running():
        fetch_derpibooru.start()

@bot.event
async def setup_hook():
    await bot.load_extension("commands.tags")
    await bot.load_extension("commands.admin")
    await bot.load_extension("commands.stats")
    await bot.load_extension("commands.legendary")
    print("تم تحميل ملفات الأوامر بنجاح!")

bot.run(TOKEN)