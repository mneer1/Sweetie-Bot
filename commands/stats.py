import discord
from discord.ext import commands
import db  # استيراد ملف الـ db الذي أنشأناه

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    @commands.has_permissions(manage_messages=True)
    async def view_stats(self, ctx):
        data = await db.get_stats() # جلب البيانات من قاعدة البيانات
        
        embed = discord.Embed(
            title="📊 Image review stats",
            color=discord.Color.blue()
        )
        embed.add_field(name="Total", value=data["total"])
        embed.add_field(name="✅ Accepted", value=data["accepted"])
        embed.add_field(name="❌ Rejected", value=data["rejected"])
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))