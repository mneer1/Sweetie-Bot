import discord
from discord.ext import tasks, commands
import aiohttp
import json

from config import TOKEN, WEBHOOK_URL, ADMIN_CHANNEL_ID
from derpibooru import get_api_url

API_BASE_URL = "https://derpibooru.org/api/v1/json/search/images"

def load_stats():
    try:
        with open("stats.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"total": 0, "accepted": 0, "rejected": 0, "admins": {}}


def save_stats(stats):
    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


stats_data = load_stats()

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

        # 1. تحميل البيانات طازجة من الملف قبل التعديل
        current_stats = load_stats() 
        
        admin_id = str(interaction.user.id)
        admin_name = interaction.user.display_name

        current_stats["total"] += 1
        current_stats["accepted"] += 1

        if admin_id not in current_stats["admins"]:
            current_stats["admins"][admin_id] = {"name": admin_name, "accepted": 0, "rejected": 0}

        current_stats["admins"][admin_id]["accepted"] += 1
        
        # 2. حفظ البيانات المحدثة
        save_stats(current_stats)

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
            admin_name=admin_name,
            public_text=f"✅ تم قبول هذا المنشور بواسطة {admin_name}",
        )


    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        admin_id = str(interaction.user.id)
        admin_name = interaction.user.display_name

        stats_data["total"] += 1
        stats_data["rejected"] += 1

        if admin_id not in stats_data["admins"]:
            stats_data["admins"][admin_id] = {"name": admin_name, "accepted": 0, "rejected": 0}

        stats_data["admins"][admin_id]["rejected"] += 1
        save_stats(stats_data)

        await self._finalize(
            interaction,
            accepted=False,
            admin_name=admin_name,
            public_text=f"❌ تم رفض هذا المنشور بواسطة {admin_name}",
        )



@tasks.loop(minutes=5)
async def fetch_derpibooru():
    await bot.wait_until_ready()

    try:
        channel_id = int(ADMIN_CHANNEL_ID)
    except ValueError:
        print(f"❌ خطأ: معرّف القناة ADMIN_CHANNEL_ID الممرر ليس رقماً صالحاً.")
        return

    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as exc:
            print(f"⚠️ تحذير: تعذر الوصول إلى القناة {channel_id}: {exc}")
            return

    # تحميل التاغات ديناميكياً من ملف tags.json
    try:
        with open("tags.json", "r", encoding="utf-8") as f:
            tags = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tags = {"include": ["safe"], "exclude": []}

    # بناء الاستعلام بشكل ديناميكي
    query_string = ",".join(tags.get("include", ["safe"]) + [f"-{t}" for t in tags.get("exclude", [])])

    params = {
        "q": query_string,
        "sf": "created_at",
        "sd": "desc",
        "per_page": 3
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(API_BASE_URL, params=params) as response:

            if response.status != 200:
                print(f"⚠️ فشل جلب الصور من API. كود الخطأ: {response.status}")
                return

            data = await response.json()
            images = data.get("images", [])

            if not images:
                print("⚠️ لا توجد صور مطابقة للفلاتر الحالية.")
                return

            for img in reversed(images):
                img_id = img.get("id")
                if img_id is None or img_id in sent_images:
                    continue

                sent_images.add(img_id)

                image_url = img.get("representations", {}).get("large") or img.get("view_url")
                uploader = img.get("uploader") or "مجهول"
                description = img.get("description") or "لا يوجد وصف."

                if len(description) > 1000:
                    description = description[:1000] + "... [مقتطع]"

                embed = discord.Embed(
                    title=f"مراجعة صورة جديدة | الناشر: {uploader}",
                    description=description,
                    color=discord.Color.orange(),
                )
                embed.set_image(url=image_url)

                view = ApprovalView(image_url, uploader, description)
                await channel.send(embed=embed, view=view)


@bot.event
async def on_ready():
    print(f"البوت {bot.user} يعمل الآن!")
    if not fetch_derpibooru.is_running():
        fetch_derpibooru.start()


@bot.command()
async def test(ctx):
    await ctx.send("سويتي بوت تعمل بنجاح!")
    print(get_api_url())


@bot.event
async def setup_hook():
    await bot.load_extension("commands.tags")
    await bot.load_extension("commands.admin")
    await bot.load_extension("commands.stats")
    await bot.load_extension("commands.legendary")
    print("تم تحميل ملفات الأوامر بنجاح!")


bot.run(TOKEN)