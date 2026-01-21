import asyncio
import datetime
import os
import discord
from discord.ext import commands, tasks
import pytz

from Data import api
from dotenv import load_dotenv

from components.follow_view import FollowView
TEST_GUILD_ID = 1169059604370575381  # Replace with your test server's guild ID
TEST_GUILD_ID2 = 1148122592293699584
DEBUG = False
load_dotenv()
TCG_KEY = os.getenv('TCGAPI_KEY')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
TCGPLAYER_BASE_URL = "https://www.tcgplayer.com/product/"
TCGPLAYER_IMG_BASE_URL = "https://tcgplayer-cdn.tcgplayer.com/product/"


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = None
        self.tcg_api = None

    async def is_ready(self, ctx) -> bool:
        if self.tcg_api is None:
            await ctx.respond(
                "⚠️ Bot is still starting up. Please try again in a moment."
            )
            return False
        return True
    
    def create_embed(self, card: dict):
        lastUpdatedDate = datetime.datetime.fromtimestamp(card.get('lastUpdated', 0)).strftime('%m-%d-%y')
        tcgPlayerURL = TCGPLAYER_BASE_URL + card.get('tcgplayerId')
        cardImageURL = TCGPLAYER_IMG_BASE_URL + card.get('tcgplayerId') + "_in_1000x1000.jpg"
        embed = discord.Embed(title=card.get('name'), color=discord.Color.blue(), url=tcgPlayerURL)
        
        embed.add_field(name="Condition", value=card.get('condition'), inline=True)
        
        embed.add_field(name="Current Price", value=f"${card.get('currentPrice')}", inline=True)
        
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.add_field(name="Daily Change", value=f"{card.get('priceChange24hr')}%")
        if card.get('priceChange30d') != 0:
            embed.add_field(name="Monthly Change", value=f"{card.get('priceChange30d')}%", inline=True)
            
        embed.add_field(name="Monthly Trend", value=f"{card.get('trendSlope30d'):.2f}", inline=True)
        
        embed.set_image(url=cardImageURL)
        embed.set_footer(text=f"Last Updated {lastUpdatedDate}")
        
        view = FollowView(api=self.tcg_api, card=card)
        return embed, view
 
    async def sendUserCards(self):
        userFollowingCards = await self.tcg_api.getFollowCards()
        userFollowingCards = sorted(userFollowingCards, key = lambda x: x.get("discUserId"))
        discId = userFollowingCards[0].get("discUserId")
        user = await self.bot.fetch_user(discId)
        for i in range(len(userFollowingCards)):
            if discId != userFollowingCards[i].get("discUserId"):
                discId = userFollowingCards[i].get("discUserId")
                user = await self.bot.fetch_user(discId)
            card = await self.tcg_api.findCardById(userFollowingCards[i].get("cardId"))
            if abs(card.get("priceChange24hr")) >= 5:
                try:
                    embed, view = self.create_embed(card)
                    await user.send(embed=embed, view=view)
                except discord.Forbidden:
                    print("DMs are closed")
            
    @commands.Cog.listener()
    async def on_ready(self):
        if self.tcg_api is None:
            print("Connecting to TCG API and Supabase...")
            
            self.loop = asyncio.get_running_loop()  
            
            self.tcg_api = api.TCG_API(
                api_key=TCG_KEY,
                supabase_key=SUPABASE_KEY,
                loop=self.loop
            )
            await self.tcg_api.connect()
            if not self.daily_data_pull.is_running():
                self.daily_data_pull.start()
            print("Connected to TCG API and Supabase.")
            
    @commands.slash_command(name="summary", description="Get a summary of the current market. IE. top gainers/losers.", guild_ids=[TEST_GUILD_ID, TEST_GUILD_ID2] if DEBUG else None)
    async def summary(self, ctx, timeframe: str = "day"):
        await ctx.defer()

        try:
            summary = await self.tcg_api.getSummary(timeframe)
        except Exception as e:
            await ctx.followup.send("Erorr with the timeframe input. Acceptable timeframes are day, week, and month")
            return

        cards = []

        for bucket in summary.values():
            if bucket.get("gainer"):
                cards.append(bucket["gainer"])
            if bucket.get("loser"):
                cards.append(bucket["loser"])

        for card in cards:
            embed, view = self.create_embed(card)
            await ctx.followup.send(embed=embed, view=view)
        
    @commands.slash_command(name="update_cards", description="Get list of cards", guild_ids=[TEST_GUILD_ID, TEST_GUILD_ID2])
    async def update_cards(self, ctx):
        if ctx.author.id != 163118769307254784:
            await ctx.respond("❌ You do not have permission to use this command.", ephemeral=True)
            return
        if not await self.is_ready(ctx):
            return

        await ctx.defer(ephemeral=True)

        message = await ctx.followup.send(
            "🔄 Loading cards...",
            ephemeral=True,
            wait=True
        )
        
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.tcg_api.update_cards)
        await message.edit(content="✅ Finished!")
        
    @commands.slash_command(name="find", description="Find a card and show its price changes", guild_ids=[TEST_GUILD_ID, TEST_GUILD_ID2] if DEBUG else None)
    async def find(self, ctx, card_name: str, condition: str = "Near Mint"):
        if not await self.is_ready(ctx):
            return

        await ctx.defer()
        card_data = await self.tcg_api.find_card(card_name, condition)
        
        if card_data:
            for card in card_data:
                embed, view = self.create_embed(card)
                await ctx.followup.send(embed=embed, view=view)
        else:
            await ctx.followup.send("Card not found.")
    
    @commands.slash_command(name="test", description="Testing specific features", guild_ids=[TEST_GUILD_ID, TEST_GUILD_ID2])
    async def testing(self, ctx):
        await ctx.defer()
        await self.sendUserCards()
        await ctx.send("Testing command executed.")
        
    @commands.slash_command(name="unfollow_all", descrption="Unfollow all follwed cards", guild_ids=[TEST_GUILD_ID, TEST_GUILD_ID2] if DEBUG else None)
    async def unfollow_all(self, ctx):
        await ctx.defer()
        await self.tcg_api.unfollowAll(ctx.author.id)
        await ctx.followup.send("Finished unfollowing all cards.")
        
    @tasks.loop(time=datetime.time(hour=6, minute=0, tzinfo=pytz.timezone("US/Pacific")))
    async def daily_data_pull(self):
        print("Running daily API pull")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.tcg_api.update_cards)
        print("Finished Updating cards")
        
        print("Sending card updates to users...")
        await self.sendUserCards()
        print("Finished sending updates")
    
    
def setup(bot):
    bot.add_cog(Economy(bot))
    
    