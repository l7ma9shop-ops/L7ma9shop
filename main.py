import os
import discord
from discord.ext import commands
from discord.ui import Button, View
from telethon import TelegramClient, events
import asyncio
import json

# --- [ سحب البيانات السرية من الاستضافة ] ---
API_ID = int(os.getenv('TG_API_ID', '0'))
API_HASH = os.getenv('TG_API_HASH', 'none')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'none')
OWNER_ID = 990047184328204348 
RIGHTS = "L7MA9 SHOP © 2026"
TICKET_PREFIX = "ticket-"

# --- [ إعدادات البوت ] ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)
tele_client = TelegramClient('l7ma9_session', API_ID, API_HASH)

# نظام النقاط
stats = {}
try:
    with open('stats.json', 'r') as f: stats = json.load(f)
except: stats = {}

def save_stats():
    with open('stats.json', 'w') as f: json.dump(stats, f)

# --- [ واجهة الأزرار التفاعلية ] ---
class L7MA9Control(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="طلب حساب جديد", style=discord.ButtonStyle.success, custom_id="get_acc", emoji="📧")
    async def get_account(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.channel.name.startswith(TICKET_PREFIX):
            return await interaction.response.send_message("❌ في التذاكر فقط!", ephemeral=True)
        await interaction.response.send_message("⏳ جاري سحب البيانات...", ephemeral=True)
        async with tele_client:
            await tele_client.send_message('@GmailFarmerBot', '/start')
            await asyncio.sleep(1)
            msgs = await tele_client.get_messages('@GmailFarmerBot', limit=1)
            await msgs[0].click(text='➕ تسجيل حساب جديد')

    @discord.ui.button(label="إحصائياتي", style=discord.ButtonStyle.primary, custom_id="my_stats", emoji="📊")
    async def view_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        pts = stats.get(str(interaction.user.id), 0)
        await interaction.response.send_message(f"✅ إنجازاتك: `{pts}` حساب مستخرج.", ephemeral=True)

# --- [ الأوامر ] ---
@bot.command()
async def setup(ctx):
    if ctx.author.id != OWNER_ID: return
    embed = discord.Embed(title=f"🏢 إدارة {RIGHTS}", description="نظام سحب الحسابات الآلي.\nاضغط الزر لبدء العمل.", color=0x5865F2)
    await ctx.send(embed=embed, view=L7MA9Control())

@bot.command()
async def top(ctx):
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    leaderboard = "🏆 **المتصدرين:**\n" + "\n".join([f"<@{u}>: `{p}`" for u, p in sorted_stats[:5]])
    await ctx.send(embed=discord.Embed(description=leaderboard, color=0xF1C40F))

# --- [ معالجة الرسائل ] ---
@tele_client.on(events.NewMessage(chats='@GmailFarmerBot'))
async def handle_tg_msg(event):
    if "البريد:" in event.raw_text:
        for channel in bot.get_all_channels():
            if channel.name.startswith(TICKET_PREFIX):
                await channel.send(f"📥 **حساب جديد:**\n```\n{event.raw_text}\n```")
                break

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if message.attachments and message.channel.name.startswith(TICKET_PREFIX):
        uid = str(message.author.id)
        stats[uid] = stats.get(uid, 0) + 1
        save_stats()
        async with tele_client:
            msgs = await tele_client.get_messages('@GmailFarmerBot', limit=1)
            if msgs: await msgs[0].click(text='تم')
        await message.add_reaction("✔️")
        owner = await bot.fetch_user(OWNER_ID)
        await message.channel.send(f"🔔 {owner.mention} تم استلام عمل جديد!")
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'🚀 {RIGHTS} Online!')
    bot.add_view(L7MA9Control())

async def main():
    await asyncio.gather(tele_client.start(), bot.start(DISCORD_TOKEN))

if __name__ == '__main__':
    asyncio.run(main())

    @discord.ui.button(label="إحصائياتي", style=discord.ButtonStyle.primary, custom_id="my_stats", emoji="📊")
    async def view_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        points = stats.get(user_id, 0)
        await interaction.response.send_message(f"👤 **الموظف:** {interaction.user.mention}\n✅ **عدد الحسابات المستخرجة:** `{points}`", ephemeral=True)

# --- [ الأوامر الإدارية ] ---

@bot.command()
async def setup(ctx):
    """إرسال لوحة التحكم الرئيسية"""
    if ctx.author.id != OWNER_ID: return
    embed = discord.Embed(
        title=f"🏢 مركز إدارة {RIGHTS}",
        description="مرحباً بك في النظام المؤتمت لبيع واستخراج الحسابات.\n\n**التعليمات:**\n1️⃣ افتح تذكرة عمل.\n2️⃣ اضغط على زر طلب حساب.\n3️⃣ بعد إتمام العمل، ارفع صورة الإثبات.",
        color=0x5865F2
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"Admin: {ctx.author.name}")
    await ctx.send(embed=embed, view=L7MA9Control())

@bot.command()
async def top(ctx):
    """عرض قائمة المتصدرين للموظفين"""
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    leaderboard = "🏆 **قائمة أفضل الموظفين:**\n"
    for i, (uid, pts) in enumerate(sorted_stats[:10], 1):
        leaderboard += f"{i}. <@{uid}> - `{pts}` حساب\n"
    await ctx.send(embed=discord.Embed(description=leaderboard, color=0xF1C40F))

# --- [ معالجة الرسائل والتلجرام ] ---

@tele_client.on(events.NewMessage(chats='@GmailFarmerBot'))
async def handle_tg_msg(event):
    if "البريد:" in event.raw_text:
        # إرسال الحساب لأول تذكرة نشطة
        for channel in bot.get_all_channels():
            if channel.name.startswith(TICKET_PREFIX):
                embed = discord.Embed(title="📥 تم استخراج بيانات جديدة", color=0x2ECC71)
                embed.description = f"```\n{event.raw_text}\n```"
                embed.set_footer(text="يرجى رفع صورة الإثبات فور الانتهاء.")
                await channel.send(embed=embed)
                break

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # احتساب النقاط عند رفع الصور في التذاكر
    if message.attachments and message.channel.name.startswith(TICKET_PREFIX):
        uid = str(message.author.id)
        stats[uid] = stats.get(uid, 0) + 1
        save_stats()
        
        async with tele_client:
            msgs = await tele_client.get_messages('@GmailFarmerBot', limit=1)
            if msgs: await msgs[0].click(text='تم')
        
        await message.add_reaction("⭐")
        owner = await bot.fetch_user(OWNER_ID)
        report = discord.Embed(title="💰 إشعار تسليم", color=0x3498DB)
        report.add_field(name="الموظف", value=message.author.mention)
        report.set_image(url=message.attachments[0].url)
        await message.channel.send(content=f"🔔 {owner.mention}", embed=report)

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'🚀 {RIGHTS} Online!')
    if not tele_client.is_connected(): await tele_client.start()
    bot.add_view(L7MA9Control())
    await bot.change_presence(activity=discord.Game(name=f"Managing {RIGHTS}"))

async def start_all():
    await asyncio.gather(tele_client.start(), bot.start(DISCORD_TOKEN))

if __name__ == '__main__':
    asyncio.run(start_all())
  
