import discord
from discord.ext import commands
import db


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _chunk_text(self, items, max_len=900):
        chunks = []
        current = ""

        for item in items:
            item = str(item).strip()
            if not item:
                continue

            candidate = item if not current else f"{current}, {item}"

            if len(candidate) > max_len:
                if current:
                    chunks.append(current)
                current = item
            else:
                current = candidate

        if current:
            chunks.append(current)

        return chunks

    @commands.command(name="add_tag")
    @commands.has_permissions(administrator=True)
    async def add_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()

        if not tag:
            await ctx.send("⚠️ يجب كتابة التاغ أولاً.")
            return

        current_tags = await db.get_tags()
        included = set(current_tags.get("include", []))
        excluded = set(current_tags.get("exclude", []))

        if tag in included:
            await ctx.send("❌ هذا التاغ موجود بالفعل في قائمة الطلبات.")
            return

        if tag in excluded:
            await db.delete_tag(tag)

        await db.insert_tag(tag, "include")
        await ctx.send(f"✅ تم إضافة التاغ المطلوب: `{tag}`")

    @commands.command(name="block_tag")
    @commands.has_permissions(administrator=True)
    async def block_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()

        if not tag:
            await ctx.send("⚠️ يجب كتابة التاغ أولاً.")
            return

        current_tags = await db.get_tags()
        included = set(current_tags.get("include", []))
        excluded = set(current_tags.get("exclude", []))

        if tag in excluded:
            await ctx.send("❌ هذا التاغ محظور بالفعل.")
            return

        if tag in included:
            await db.delete_tag(tag)

        await db.insert_tag(tag, "exclude")
        await ctx.send(f"🚫 تم حظر التاغ: `{tag}`")

    @commands.command(name="remove_tag")
    @commands.has_permissions(administrator=True)
    async def remove_tag(self, ctx, *, tag: str):
        tag = tag.strip().lower()

        if not tag:
            await ctx.send("⚠️ يجب كتابة التاغ أولاً.")
            return

        current_tags = await db.get_tags()
        included = set(current_tags.get("include", []))
        excluded = set(current_tags.get("exclude", []))

        if tag not in included and tag not in excluded:
            await ctx.send("⚠️ هذا التاغ غير موجود في قاعدة البيانات أصلاً.")
            return

        await db.delete_tag(tag)
        await ctx.send(f"🗑️ تم مسح التاغ `{tag}` نهائياً من قاعدة البيانات.")

    @commands.command(name="show_tags")
    @commands.has_permissions(administrator=True)
    async def show_tags(self, ctx):
        tags = await db.get_tags()

        included = tags.get("include", [])
        excluded = tags.get("exclude", [])

        embed = discord.Embed(
            title="🏷️ قائمة التاغات الحالية",
            color=discord.Color.blurple()
        )

        if included:
            include_chunks = self._chunk_text(included)
            for i, chunk in enumerate(include_chunks, start=1):
                field_name = "✅ التاغات المطلوبة" if len(include_chunks) == 1 else f"✅ التاغات المطلوبة ({i})"
                embed.add_field(name=field_name, value=chunk, inline=False)
        else:
            embed.add_field(name="✅ التاغات المطلوبة", value="لا يوجد", inline=False)

        if excluded:
            exclude_chunks = self._chunk_text(excluded)
            for i, chunk in enumerate(exclude_chunks, start=1):
                field_name = "🚫 التاغات المحظورة" if len(exclude_chunks) == 1 else f"🚫 التاغات المحظورة ({i})"
                embed.add_field(name=field_name, value=chunk, inline=False)
        else:
            embed.add_field(name="🚫 التاغات المحظورة", value="لا يوجد", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="block_bulk")
    @commands.has_permissions(administrator=True)
    async def block_bulk(self, ctx, *, tags_input: str):
        tags = [t.strip().lower() for t in tags_input.split(",") if t.strip()]
        if not tags:
            await ctx.send("⚠️ لم يتم العثور على تاغات صالحة.")
            return

        current_tags = await db.get_tags()
        included = set(current_tags.get("include", []))
        excluded = set(current_tags.get("exclude", []))

        blocked_count = 0

        for tag in tags:
            if tag in excluded:
                continue

            if tag in included:
                await db.delete_tag(tag)

            await db.insert_tag(tag, "exclude")
            excluded.add(tag)
            included.discard(tag)
            blocked_count += 1

        await ctx.send(f"🚫 تم حظر {blocked_count} تاغ دفعة واحدة.")


async def setup(bot):
    await bot.add_cog(Tags(bot))