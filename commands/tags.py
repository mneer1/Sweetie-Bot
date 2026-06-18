import discord
from discord.ext import commands
import json
import os

TAGS_FILE = "tags.json"

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_file()

    def ensure_file(self):
        if not os.path.exists(TAGS_FILE):
            with open(TAGS_FILE, "w", encoding="utf-8") as f:
                json.dump({"include": ["safe"], "exclude": []}, f, indent=4)

    def load_tags(self):
        with open(TAGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_tags(self, data):
        with open(TAGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @commands.command(name="add_tag")
    @commands.has_permissions(administrator=True)
    async def add_tag(self, ctx, *, tag: str):
        data = self.load_tags()
        tag = tag.strip().lower()
        if tag not in data["include"]:
            data["include"].append(tag)
            self.save_tags(data)
            await ctx.send(f"تم إضافة التاغ: `{tag}`")
        else:
            await ctx.send("هذا التاغ موجود بالفعل.")

    @commands.command(name="block_tag")
    @commands.has_permissions(administrator=True)
    async def block_tag(self, ctx, *, tag: str):
        data = self.load_tags()
        tag = tag.strip().lower()
        if tag not in data["exclude"]:
            data["exclude"].append(tag)
            self.save_tags(data)
            await ctx.send(f"تم حظر التاغ `{tag}`.")
        else:
            await ctx.send("هذا التاغ محظور بالفعل.")

    @commands.command(name="show_tags")
    async def show_tags(self, ctx):
        data = self.load_tags()
        embed = discord.Embed(title="📋 الفلاتر الحالية", color=discord.Color.blue())
        embed.add_field(name="🟢 المطلوب", value=", ".join(data["include"]) or "لا يوجد", inline=False)
        embed.add_field(name="🔴 المحظور", value=", ".join(data["exclude"]) or "لا يوجد", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Tags(bot))