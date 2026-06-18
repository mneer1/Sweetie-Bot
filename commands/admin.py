import discord
from discord.ext import commands
import db  # تأكد أن ملف db.py موجود في نفس المجلد

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # أمر المسح
    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            await ctx.send("❌ عذراً، يمكنك مسح عدد رسائل بين 1 و 100 فقط في المرة الواحدة.")
            return

        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 تم تنظيف وإزالة {len(deleted) - 1} رسالة بنجاح.", delete_after=5)

    # أمر فحص السرعة
    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"ping: `{latency}ms`")

    # أمر لتشغيل البحث فوراً
    @commands.command(name="test_fetch")
    @commands.has_permissions(administrator=True)
    async def test_fetch(self, ctx):
        await ctx.send("جاري فحص الاتصال بالـ API وقاعدة البيانات...")
        try:
            # نتأكد أن الدالة تعمل
            await self.bot.fetch_derpibooru.callback(self.bot) 
            await ctx.send("تم تشغيل عملية البحث، راجع الـ Console (Logs) للنتائج!")
        except Exception as e:
            await ctx.send(f"حدث خطأ: {e}")

    # أمر فحص قاعدة البيانات
    @commands.command(name="check_db")
    @commands.has_permissions(administrator=True)
    async def check_db(self, ctx):
        """أمر للتأكد مما يقرأه البوت من قاعدة البيانات"""
        try:
            tags = await db.get_tags()
            await ctx.send(f"التاغات التي يراها البوت حالياً: \n`{tags}`")
        except Exception as e:
            await ctx.send(f"حدث خطأ أثناء قراءة القاعدة: {e}")

async def setup(bot):
    await bot.add_cog(Admin(bot))