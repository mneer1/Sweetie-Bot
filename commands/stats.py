import discord
from discord.ext import commands
import json
import os

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.filepath = "stats.json"
        self.ensure_file_exists()

    def ensure_file_exists(self):
        # التحقق من وجود الملف وصحة محتواه
        if not os.path.exists(self.filepath):
            self.reset_stats()
        else:
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # التحقق من وجود المفاتيح المطلوبة
                    if not all(key in data for key in ["total", "accepted", "rejected"]):
                        self.reset_stats()
            except json.JSONDecodeError:
                self.reset_stats()

    def reset_stats(self):
        # إنشاء الملف بالقيم الافتراضية
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump({"total": 0, "accepted": 0, "rejected": 0}, f, indent=4)

    @commands.command(name="stats")
    @commands.has_permissions(manage_messages=True)
    async def view_stats(self, ctx):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            await ctx.send("حدث خطأ في قراءة ملف الإحصائيات.")
            return

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