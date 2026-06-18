import discord
from discord.ext import commands
import aiohttp
import random
import json
import config  # استيراد ملف الإعدادات لتطبيق الفلاتر الممنوعة

class StatsAndLegendary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # أمر عرض إحصائيات الإدارة
    @commands.command(name="stats")
    @commands.has_permissions(manage_messages=True)
    async def view_stats(self, ctx):
        try:
            with open("stats.json", "r") as f:
                data = json.load(f)
        except:
            await ctx.send("لم يتم تسجيل أي إحصائيات بعد.")
            return

        embed = discord.Embed(title=" إحصائيات مراجعة الصور", color=discord.Color.blue())
        embed.add_field(name="المجموع الكلي", value=data['total'], inline=True)
        embed.add_field(name="✅ المقبولة", value=data['accepted'], inline=True)
        embed.add_field(name="❌ المرفوضة", value=data['rejected'], inline=True)

        admin_text = ""
        for admin_id, stats in data['admins'].items():
            admin_text += f"**{stats['name']}**: ✅ {stats['accepted']} | ❌ {stats['rejected']}\n"
        
        if admin_text:
            embed.add_field(name="👥 أداء الإداريين", value=admin_text, inline=False)

        await ctx.send(embed=embed)

    # الأمر المحدث لحل الثغرة وتطبيق فلاتر الحجب
    @commands.command(name="legendary")
    async def legendary_post(self, ctx):
        # 🛠️ الحل: استخدام sf=random من الموقع مباشرة لتجنب أخطاء أرقام الصفحات الوهمية
        query_parts = ["safe"]
        for tag in config.EXCLUDE_TAGS:
            query_parts.append(f"-{tag.replace(' ', '+')}")
            
        query_string = "%2C+".join(query_parts)
        # الرابط الآن يجلب صورة عشوائية آمنة بدون الحاجة لتحديد رقم صفحة
        api_url = f'https://derpibooru.org/api/v1/json/search/images?q={query_string}&sf=random'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    images = data.get('images', [])
                    if images:
                        img = random.choice(images) # يختار واحدة من الصور العشوائية
                        image_url = img['representations'].get('large') or img['view_url']
                        uploader = img.get('uploader') or "مجهول"
                        score = img.get('score', 0)
                        
                        embed = discord.Embed(
                            title=f"🌟 منشور عشوائي | الناشر: {uploader}", 
                            description=f"التقييم (Upvotes): {score} ⬆️",
                            color=discord.Color.gold()
                        )
                        embed.set_image(url=image_url)
                        
                        view = discord.ui.View()
                        view.add_item(discord.ui.Button(label="📥 تنزيل الرسمة", url=image_url))
                        
                        await ctx.send(embed=embed, view=view)
                    else:
                        await ctx.send("لم يتم العثور على صور تطابق الفلاتر الحالية.")
                else:
                    await ctx.send(f"حدث خطأ في الاتصال. كود الخطأ: {response.status}")

async def setup(bot):
    await bot.add_cog(StatsAndLegendary(bot))