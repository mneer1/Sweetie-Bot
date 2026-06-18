import discord
from discord.ext import commands
import config  # لاستدعاء وتعديل المصفوفات مباشرة

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # أمر لإضافة تاغ مطلوب
    @commands.command(name="add_tag")
    @commands.has_permissions(administrator=True)
    async def add_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()
        if tag not in config.INCLUDE_TAGS:
            config.INCLUDE_TAGS.append(tag)
            await ctx.send(f"تم اضافة التاغ: `{tag}`")
        else:
            await ctx.send("هاذا التاغ موجود بالفعل")

    # أمر لإضافة تاغ ممنوع (مثل الفيريز)
    @commands.command(name="block_tag")
    @commands.has_permissions(administrator=True)
    async def block_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()
        if tag not in config.EXCLUDE_TAGS:
            config.EXCLUDE_TAGS.append(tag)
            await ctx.send(f" تم حظر التاغ `{tag}` بنجاح.")
        else:
            await ctx.send("هاذا التاغ محظور بالفعل.")

    # أمر لعرض التاغات الحالية في السيرفر
    @commands.command(name="show_tags")
    @commands.has_permissions(manage_messages=True)
    async def show_tags(self, ctx):
        embed = discord.Embed(title="📋 قائمة فلاتر المحتوى الحالية", color=discord.Color.blue())
        embed.add_field(name="🟢 التاغات المطلوبة", value=", ".join(config.INCLUDE_TAGS) or "لا يوجد", inline=False)
        embed.add_field(name="🔴 التاغات الممنوعة", value=", ".join(config.EXCLUDE_TAGS) or "لا يوجد", inline=False)
        await ctx.send(embed=embed)

# دالة أساسية ليتعرف البوت على الملف عند استدعائه
async def setup(bot):
    await bot.add_cog(Tags(bot))