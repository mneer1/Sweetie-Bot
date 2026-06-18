import discord
from discord.ext import commands
import aiohttp
import random
import json
import config

class StatsAndLegendary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    @commands.has_permissions(manage_messages=True)
    async def view_stats(self, ctx):
        try:
            with open("stats.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            await ctx.send("No stats have been recorded yet.")
            return

        embed = discord.Embed(title="📊 Image review stats", color=discord.Color.blue())
        embed.add_field(name="Total", value=data["total"], inline=True)
        embed.add_field(name="✅ Accepted", value=data["accepted"], inline=True)
        embed.add_field(name="❌ Rejected", value=data["rejected"], inline=True)

        admin_text = ""
        for admin_id, stats in data["admins"].items():
            admin_text += f"**{stats['name']}**: ✅ {stats['accepted']} | ❌ {stats['rejected']}\n"

        if admin_text:
            embed.add_field(name="👥 Admin performance", value=admin_text, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="legendary")
    async def legendary_post(self, ctx):
        query_parts = ["safe"]

        for tag in config.EXCLUDE_TAGS:
            query_parts.append(f"-{tag}")

        query_string = ", ".join(query_parts)

        api_url = "https://derpibooru.org/api/v1/json/search/images"
        params = {
            "q": query_string,
            "sf": "created_at",
            "sd": "desc"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params) as response:
                if response.status != 200:
                    await ctx.send(f"API connection error. Status code: {response.status}")
                    return

                data = await response.json()
                images = data.get("images", [])

                if not images:
                    await ctx.send("No images matched the current filters.")
                    return

                img = random.choice(images)
                image_url = img["representations"].get("large") or img["view_url"]
                uploader = img.get("uploader") or "Unknown"
                score = img.get("score", 0)

                embed = discord.Embed(
                    title=f"🌟 Random post | Uploader: {uploader}",
                    description=f"Score: {score}",
                    color=discord.Color.gold()
                )
                embed.set_image(url=image_url)

                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="📥 Download image", url=image_url))

                await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(StatsAndLegendary(bot))