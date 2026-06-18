import discord
from discord.ext import commands
import db  # استيراد ملف قاعدة البيانات

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add_tag")
    @commands.has_permissions(administrator=True)
    async def add_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()
        
        # جلب التاغات الحالية للتأكد من عدم التكرار
        current_tags = await db.get_tags()
        
        if tag not in current_tags["include"]:
            await db.insert_tag(tag, 'include') # إضافة للـ DB
            await ctx.send(f"تم إضافة التاغ المطلوب: `{tag}`")
        else:
            await ctx.send("هذا التاغ موجود بالفعل في قائمة الطلبات.")

    @commands.command(name="block_tag")
    @commands.has_permissions(administrator=True)
    async def block_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()
        
        # جلب التاغات الحالية للتأكد من عدم التكرار
        current_tags = await db.get_tags()
        
        if tag not in current_tags["exclude"]:
            await db.insert_tag(tag, 'exclude') # إضافة للـ DB كـ exclude
            await ctx.send(f"تم حظر التاغ: `{tag}`")
        else:
            await ctx.send("هذا التاغ محظور بالفعل.")

async def setup(bot):
    await bot.add_cog(Tags(bot))