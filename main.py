import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
DISCORD_TOKEN = os.getenv('DISC_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    # await bot.tree.sync()
    print(f'We have logged in as {bot.user}')
    
@bot.slash_command(name="ping", description="Responds with Pong!")
async def ping(ctx):
    cog = bot.get_cog('Economy')
    commands = cog.get_commands()
    print([c.name for c in commands])

    await ctx.respond("Pong!")
        

async def main():
    bot.load_extension("commands.economy")
    await bot.start(DISCORD_TOKEN)

asyncio.run(main())
