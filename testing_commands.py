import discord
from discord.ext import commands

class TestingCommands(commands.Cog):
    """
    Testing commands
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="connect",
        help="Connect to the voice channel you're in! (Testing purpose, completely useless)"
    )
    async def connect(self, ctx: commands.Context):
        if ctx.author.voice is None:
            await ctx.send("You're not connected to a voice channel!")
            return
        await ctx.author.voice.channel.connect()
        await ctx.send("Connected")

    @commands.hybrid_command(
        name="disconnect",
        help="Disconnect from the voice channel. (Testing purpose, completely useless)"
    )
    async def disconnect(self, ctx: commands.Context):
        await ctx.voice_client.disconnect(force=True)
        await ctx.send("Disconnected")

    @commands.hybrid_command(
        name="test",
        help="Send a testing message"
    )
    async def test(self, ctx: commands.Context):
        test_messages_id = []
        message = await ctx.reply(f"Test")
        await message.edit(content=f"Test! Message id: {message.id}")
        await message.add_reaction("🦄")
        await message.add_reaction("👍")
        test_messages_id.append(message.id)

        @self.bot.event
        async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
            if reaction.message.id in test_messages_id and (reaction.emoji == "🦄" or reaction.emoji == "👍"):
                await message.edit(content=f"Reacted with {reaction.emoji} by {user.mention}")

        @self.bot.event
        async def on_reaction_remove(reaction: discord.Reaction, user: discord.Member):
            if reaction.message.id in test_messages_id and (reaction.emoji == "🦄" or reaction.emoji == "👍"):
                await message.edit(content=f"Removed reaction {reaction.emoji} by {user.mention}")
