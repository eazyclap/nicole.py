import discord
import os
from discord.ext import commands
from general_commands import General, BaseEvents
from help_command import Help
from lockdown import Lockdown
from private_channels import PrivateChannels
from keep_alive import keep_alive


# CONSTANTS AND PARAMETERS
# TODO RESET TO DS_TOKEN
TOKEN = os.environ["TESTING_TOKEN"]
intents = discord.Intents.all()
help_command = commands.DefaultHelpCommand(no_category='Non sorted commands')

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('\\'),
    case_insensitive=True,
    intents=intents,
    help_command=help_command
)


# Default help command is replaced with a more fancy one (check "help_command.py")
bot.remove_command("help")


# START
@bot.event
async def on_ready():
    await bot.add_cog(General(bot))
    await bot.add_cog(Help(bot))
    await bot.add_cog(Lockdown(bot))
    await bot.add_cog(BaseEvents(bot))
    await bot.add_cog(PrivateChannels(bot))
    await bot.tree.sync()
    await bot.wait_until_ready()
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')


@bot.hybrid_command(
        name="connect"
)
async def connect(ctx):
    if ctx.author.voice is None:
        await ctx.send("You're not connected to a voice channel!")
        return
    await ctx.author.voice.channel.connect()
    await ctx.send("Connected")


@bot.hybrid_command(
        name="disconnect"
)
async def disconnect(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send("Disconnected")


@bot.hybrid_command(
        name="test"
)
async def test(ctx: commands.Context):
    test_messages_id = []
    message = await ctx.reply(f"Test")
    await message.edit(content=f"Test! Message id: {message.id}")
    await message.add_reaction("🦄")
    await message.add_reaction("👍")
    test_messages_id.append(message.id)

    @bot.event
    async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
        if reaction.message.id in test_messages_id and (reaction.emoji == "🦄" or reaction.emoji == "👍"):
            await message.edit(content=f"Reacted with {reaction.emoji} by {user.mention}")

    @bot.event
    async def on_reaction_remove(reaction: discord.Reaction, user: discord.Member):
        if reaction.message.id in test_messages_id and (reaction.emoji == "🦄" or reaction.emoji == "👍"):
            await message.edit(content=f"Removed reaction {reaction.emoji} by {user.mention}")

if __name__ == "__main__":
    keep_alive()
    try:
        bot.run(TOKEN)
    except discord.errors.HTTPException:
      print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
      os.system('kill 1')
      os.system("python restarter.py")
