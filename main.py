import discord
import os
from discord.ext import commands
from general_commands import General, BaseEvents
from help_command import Help
from lockdown import Lockdown
from private_channels import PrivateChannels
from keep_alive import keep_alive
from testing_commands import TestingCommands


# CONSTANTS AND PARAMETERS
TOKEN = os.environ["DS_TOKEN"]
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
    await bot.add_cog(TestingCommands(bot))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Francesco!"))
    await bot.tree.sync()
    await bot.wait_until_ready()
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')


if __name__ == "__main__":
    keep_alive()
    try:
        bot.run(TOKEN)
    except discord.errors.HTTPException:
      print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
      os.system('kill 1')
      os.system("python restarter.py")
