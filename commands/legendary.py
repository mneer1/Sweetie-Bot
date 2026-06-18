import discord
from discord.ext import commands
import aiohttp
import random
import config

API_BASE_URL = "https://derpibooru.org/api/v1/json/search/images"

class Legendary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.used_ranks = set()  # ذاكرة لحفظ أرقام الصور التي تم عرضها

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    def build_query(self) -> str:
        query_parts = []

        include_tags = getattr(config, "INCLUDE_TAGS", ["safe"])
        exclude_tags = getattr(config, "EXCLUDE_TAGS", [])

        for tag in include_tags:
            tag = tag.strip()
            if tag:
                query_parts.append(tag)

        for tag in exclude_tags:
            tag = tag.strip()
            if tag:
                query_parts.append(f"-{tag}")

        return ",".join(query_parts)

    @commands.command(name="legendary")
    async def legendary_post(self, ctx):
        query_string = self.build_query()

        params = {
            "q": query_string,
            "sf": "upvotes",
            "sd": "desc",
            "per_page": 1,
            "page": 1,
        }

        async with self.session.get(API_BASE_URL, params=params) as response:
            if response.status != 200:
                await ctx.send(f"حدث خطأ في الاتصال بالموقع. كود الخطأ: {response.status}")
                return

            data = await response.json()
            total_images = data.get("total", 0)

            if total_images == 0 or not data.get("images"):
                await ctx.send("لم يتم العثور على صور تطابق الفلاتر الحالية.")
                return

            # توسيع النطاق لأفضل 5000 صورة
            max_limit = min(total_images, 5000)
            
            # إذا استهلكنا كل الأرقام المتاحة، نفرغ الذاكرة لنبدأ من جديد
            if len(self.used_ranks) >= max_limit:
                self.used_ranks.clear()

            # اختيار رقم عشوائي لم يسبق استخدامه
            while True:
                random_rank = random.randint(1, max_limit)
                if random_rank not in self.used_ranks:
                    self.used_ranks.add(random_rank)
                    break

            if random_rank == 1:
                img = data["images"][0]
            else:
                params["page"] = random_rank
                async with self.session.get(API_BASE_URL, params=params) as response2:
                    if response2.status != 200:
                        await ctx.send("حدث خطأ أثناء جلب الصورة العشوائية.")
                        return
                    
                    data2 = await response2.json()
                    img = data2["images"][0]

            image_url = img.get("representations", {}).get("large") or img.get("view_url")
            uploader = img.get("uploader") or "مجهول"
            upvotes = img.get("upvotes", 0)
            score = img.get("score", 0)
            post_url = f"https://derpibooru.org/images/{img.get('id')}"

            embed = discord.Embed(
                title=f"🌟 Legendary Post | الناشر: {uploader}",
                url=post_url,
                description=f"Upvotes: {upvotes} | Score: {score}",
                color=discord.Color.gold(),
            )
            embed.set_image(url=image_url)

            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Legendary(bot))