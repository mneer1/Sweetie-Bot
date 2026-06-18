import discord
from discord.ext import commands
import db  # استيراد ملف قاعدة البيانات الذي يحتوي على الدوال

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    @commands.has_permissions(administrator=True) # هذا السطر يضمن أن الإدارة فقط يمكنها استخدام الأمر
    async def view_stats(self, ctx, member: discord.Member = None):
        """عرض الإحصائيات العامة أو إحصائيات مستخدم محدد"""
        try:
            # إذا لم يتم تحديد عضو، نجلب الإحصائيات العامة
            if member is None:
                data = await db.get_stats()
                title = "📊 الإحصائيات العامة للبوت"
            else:
                # إذا تم تحديد عضو، نجلب إحصائياته الخاصة من جدول المستخدمين
                data = await db.get_user_stats(member.id)
                title = f"📊 إحصائيات {member.display_name}"

            # التحقق من أن البيانات تم جلبها بنجاح
            if not data:
                await ctx.send("⚠️ لا توجد إحصائيات مسجلة لهذا الطلب حالياً.")
                return

            # إنشاء رسالة الـ Embed لعرض البيانات بشكل منظم
            embed = discord.Embed(
                title=title, 
                color=discord.Color.blue()
            )
            embed.add_field(name="إجمالي", value=data["total"], inline=True)
            embed.add_field(name="✅ مقبول", value=data["accepted"], inline=True)
            embed.add_field(name="❌ مرفوض", value=data["rejected"], inline=True)
            
            # إرسال الرسالة
            await ctx.send(embed=embed)

        except Exception as e:
            # في حال حدوث أي خطأ برمجي، نقوم بإظهاره هنا
            await ctx.send(f"حدث خطأ أثناء جلب الإحصائيات: {e}")

# دالة إعداد الـ Cog لتحميلها في البوت
async def setup(bot):
    await bot.add_cog(Stats(bot))