import os
import discord
from discord.ext import commands

from Data import api
from dotenv import load_dotenv
TEST_GUILD_ID = 1169059604370575381  # Replace with your test server's guild ID

load_dotenv()
TCG_KEY = os.getenv('TCGAPI_KEY_TEST')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tcg_api = None

    async def is_ready(self, ctx) -> bool:
        if self.tcg_api is None:
            await ctx.respond(
                "⚠️ Bot is still starting up. Please try again in a moment."
            )
            return False
        return True
    
    @commands.Cog.listener()
    async def on_ready(self):
        if self.tcg_api is None:
            print("Connecting to TCG API and Supabase...")
            self.tcg_api = api.TCG_API(
                api_key=TCG_KEY,
                supabase_key=SUPABASE_KEY
            )
            await self.tcg_api.connect()
            print("Connected to TCG API and Supabase.")
        
    @commands.slash_command(name="prices", description="Get the current prices of all you are watching.", guild_ids=[TEST_GUILD_ID])
    async def prices(self, ctx: discord.ApplicationContext):
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
        
    @commands.slash_command(name="update_cards", description="Get list of cards",guild_ids=[TEST_GUILD_ID])
    async def update_cards(self, ctx):
        if not await self.is_ready(ctx):
            return

        await ctx.defer(ephemeral=True)

        message = await ctx.followup.send(
            "🔄 Loading cards...",
            ephemeral=True,
            wait=True
        )
        
        self.tcg_api.update_cards()
        await message.edit(content="✅ Finished!")
        
    @commands.slash_command(name="find", description="Find a card and show its price changes", guild_ids=[TEST_GUILD_ID])
    async def find(self, ctx, card_name: str, condition: str = "Near Mint"):
        if not await self.is_ready(ctx):
            return

        await ctx.defer()
        card_data = await self.tcg_api.find_card(card_name, condition)
        
        if card_data:
            await ctx.followup.send(f"Found card: {card_data}")
        else:
            await ctx.followup.send("Card not found.")
    
    @commands.slash_command(name="test", description="Testing specific features", guild_ids=[TEST_GUILD_ID])
    async def testing(self, ctx):
        await ctx.defer()
            
        await ctx.send("Testing command executed.")
        
    
def setup(bot):
    bot.add_cog(Economy(bot))
    
    