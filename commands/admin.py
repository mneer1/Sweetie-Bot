import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # أمر مسح الرسائل (الحد الأقصى 100)
    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            await ctx.send("❌ عذراً، يمكنك مسح عدد رسائل بين 1 و 100 فقط في المرة الواحدة.")
            return

        # ميزة إضافية: حذف رسالة الأمر نفسها مع عملية المسح
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        # إرسال تأكيد يختفي تلقائياً بعد 5 ثوانٍ ليبقى الشات نظيفاً
        await ctx.send(f"🧹 تم تنظيف وإزالة {len(deleted) - 1} رسالة بنجاح.", delete_after=5)

    # أمر إضافي مفيد: فحص حالة اتصال البوت وسرعته
    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000) # تحويل لملي ثانية
        await ctx.send(f"🏓 بونغ! سرعة الاستجابة الحالية هي: `{latency}ms`")

async def setup(bot):
    await bot.add_cog(Admin(bot))