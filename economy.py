import discord
from discord.ext import commands

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Economy Cog has been loaded for {self.bot.user}')
        
    @commands.slash_command(name="prices", description="Get the current prices of all you are watching.")
    async def prices(self, ctx):
        await ctx.respond("Here are your current watched item prices!")

    @commands.slash_command(name="watch", description="Watch an item for price changes.")
    async def watch(self, ctx, item_name: str):
        await ctx.respond(f"You are now watching {item_name} for price changes!")
    
    @commands.slash_command(name="unwatch", description="Stop watching an item.")
    async def unwatch(self, ctx, item_name: str):
        await ctx.respond(f"You have stopped watching {item_name}.")
    
    @commands.slash_command(name="summary", description="Get a summary of the current market. IE. top gainers/losers.")
    async def summary(self, ctx):
        await ctx.respond("Here is a summary of the current market!")
        
def setup(bot):
    bot.add_cog(Economy(bot))