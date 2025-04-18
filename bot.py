import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} としてログインしました！")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

keep_alive()
bot.run(TOKEN)