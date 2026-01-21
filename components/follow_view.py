import discord

from Data.api import TCG_API

class FollowView(discord.ui.View):
    def __init__(self, api: TCG_API, card: dict):
        super().__init__(timeout=None)  # persistent view
        self.api = api
        self.card = card
        
    @discord.ui.button(
        label="Follow",
        style=discord.ButtonStyle.primary
    )
    async def follow(
        self,
        button: discord.ui.Button,  # Button comes first
        interaction: discord.Interaction  # Interaction comes second
    ):
        await self.api.addCardToFollow(self.card, interaction.user.id)
        await interaction.response.send_message(
            "You will be notified for any price changes over 5\% for this card daily.",
            ephemeral=True
        )
    
    @discord.ui.button(
        label="Unfollow",
        style=discord.ButtonStyle.red
    )
    async def unfollow(
        self,
        button: discord.ui.Button,
        interaction: discord.Interaction
    ):
        await self.api.unfollowCard(self.card, interaction.user.id)
        await interaction.response.send_message(
            "You will be no longer be notified for any price changes for this card.",
            ephemeral=True
        )