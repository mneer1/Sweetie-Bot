import discord
from discord.ext import commands
import db  

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add_tag")
    @commands.has_permissions(administrator=True)
    async def add_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()
        current_tags = await db.get_tags()
        
        if tag in current_tags["include"]:
            await ctx.send("❌ هذا التاغ موجود بالفعل في قائمة الطلبات.")
        else:
            await db.insert_tag(tag, 'include') 
            if tag in current_tags["exclude"]:
                await ctx.send(f"🔄 تم نقل التاغ `{tag}` من الحظر إلى الطلبات.")
            else:
                await ctx.send(f"✅ تم إضافة التاغ المطلوب: `{tag}`")

    @commands.command(name="block_tag")
    @commands.has_permissions(administrator=True)
    async def block_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()
        current_tags = await db.get_tags()
        
        if tag in current_tags["exclude"]:
            await ctx.send("❌ هذا التاغ محظور بالفعل.")
        else:
            await db.insert_tag(tag, 'exclude') 
            if tag in current_tags["include"]:
                await ctx.send(f"🔄 تم نقل التاغ `{tag}` من الطلبات إلى الحظر.")
            else:
                await ctx.send(f"🚫 تم حظر التاغ: `{tag}`")

    @commands.command(name="remove_tag")
    @commands.has_permissions(administrator=True)
    async def remove_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()
        current_tags = await db.get_tags()
        
        if tag not in current_tags["include"] and tag not in current_tags["exclude"]:
            await ctx.send("⚠️ هذا التاغ غير موجود في قاعدة البيانات أصلاً.")
        else:
            await db.delete_tag(tag)
            await ctx.send(f"🗑️ تم مسح التاغ `{tag}` نهائياً من قاعدة البيانات.")

    # ------ الحل لمشكلة العرض ------
    @commands.command(name="show_tags")
    @commands.has_permissions(administrator=True)
    async def show_tags(self, ctx):
        """عرض جميع التاغات المسجلة في قاعدة البيانات"""
        tags = await db.get_tags()
        
        included = ", ".join(tags["include"]) if tags["include"] else "لا يوجد"
        excluded = ", ".join(tags["exclude"]) if tags["exclude"] else "لا يوجد"
        
        embed = discord.Embed(title="🏷️ قائمة التاغات الحالية", color=discord.Color.blurple())
        embed.add_field(name="✅ التاغات المطلوبة", value=f"`{included}`", inline=False)
        embed.add_field(name="🚫 التاغات المحظورة", value=f"`{excluded}`", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Tags(bot))