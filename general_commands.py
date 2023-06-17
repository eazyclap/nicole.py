import random
import time
import discord
import string
from discord.ext import commands

ROCK = ["https://tenor.com/view/rock-one-eyebrow-raised-rock-staring-the-rock-gif-22113367",
        "https://media.tenor.com/RP_qoKH85xgAAAAM/the-rock-sus-the-rock-meme.gif",
        "https://media.tenor.com/GkY0BS3F0R4AAAAM/the-rock-just-bring-it.gif",
        "https://media.tenor.com/jghhCHOmFMEAAAAC/the-rock.gif",
        "https://media.tenor.com/Y2b7jWqgpvEAAAAM/the-rock.gif",
        "https://media.tenor.com/FATkmhFxRfEAAAAM/the-rock-understands-the-rock.gif",
        "https://media.tenor.com/4921KsgMSvkAAAAM/the-rock.gif",
        "https://media.tenor.com/9Is9S2r9_wwAAAAM/the-rock.gif",
        "https://media.tenor.com/-gFILep13xcAAAAM/rock.gif"]


def get_rock():
    return random.choice(ROCK)


# SLAP CONVERTER
class Slap(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        to_slap = random.choice(ctx.channel.members)
        return f"{ctx.author.mention} slapped {to_slap.mention} {argument}!"


# THIS IS THE GENERAL COMMANDS SECTION CLASS, IMPORTED IN THE MAIN "main.py" FILE
class General(commands.Cog, name="General"):
    """
    General purpose commands
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Private class functions
    @staticmethod
    def _get_flip():
        return random.randint(0, 1)

    @staticmethod
    def _get_average_ping(current_ping: int) -> float:
        """Keeps the ping log table up to date with the latest ping result and return the average scored ping"""

        filepath = "./ping_list.txt"

        def average(nums: list) -> float:
            num_sum = 0
            nums_len = len(nums)
            for num in nums:
                num_sum += int(num)
            return float(num_sum / nums_len)

        # This is just to prevent a FileNotFound error
        try:
            with open(filepath, mode="r"):
                pass
        except FileNotFoundError:
            with open(filepath, mode="w"):
                pass
        finally:
            # Gets the last ping results and puts them in a list
            with open(filepath, mode="r") as file:
                ping_lists = []
                for line in file:
                    stripped_line = line.strip()
                    ping_lists.append(stripped_line)

                ping_lists.append(current_ping)

                result = round(average(ping_lists), 2)

                # Keep only the last 30 ping results to prevent an endless log file
                ping_lists = ping_lists[-20:]

            # Put these results back into the log file
            with open(filepath, mode="w") as file:
                to_log = ""
                for log in ping_lists:
                    to_log += f"{log}\n"
                file.write(to_log)

            return result

    # flip command
    @commands.hybrid_command(
        name="flip",
        help="\tFlips a coin for you!"
    )
    async def flip(self, ctx: commands.Context):
        message = ":coin: Coin flip result is: "
        result = self._get_flip()
        if result == 0:
            message += "**Heads!** :coin:"
        elif result == 1:
            message += "**Tails!** :coin:"
        else:
            message = ""
            message += ":coin: **Seems like there's been an error flipping your coin :smiling_face_with_tear:** :coin:"

        await ctx.send(message)

    # ping command
    @commands.hybrid_command(
        name="ping",
        aliases=["png"],
        help="\tSuper secret! Joking it's just a ping command."
    )
    async def ping(self, ctx: commands.Context):
        before = time.monotonic()
        message = await ctx.send("**Pinging...**")
        ping = (time.monotonic() - before) * 1000
        await message.edit(
            content=f":ice_cube: **Pong! Ping is {int(ping)}ms "
                    f"(average ping is {self._get_average_ping(int(ping))})** "
                    f":ice_cube:"
        )

    # clear command
    @commands.hybrid_command(
        name="clear",
        aliases=["cls", "delete", "del", "clean", "purge"],
        help="\tClears the defined amount of messages.\n"
             "Command arguments:\n"
             "`amount`: **Optional** | Default: 1 | Description: the number of messages to purge"
    )
    async def clear(self, ctx: commands.Context, amount: int = 1):
        if amount > 100:
            await ctx.reply(":warning: **Error! Cannot purge more than 100 messages in a single command!** :warning:")
            return
        elif amount < 0:
            await ctx.reply(f":warning: **Error! Cannot purge {amount} messages!** :warning:")
            return
        await ctx.send("On it!")
        await ctx.channel.purge(limit=amount + 1)

    @clear.error
    async def handle_error(self, ctx, error):
        if isinstance(error, discord.errors.NotFound):
            pass

    # checkrole command
    @commands.hybrid_command(
        name="checkrole",
        help="\tReturns a list of roles and ID of the selected user.\n"
             "Command arguments:\n"
             "`person:` **Optional** | Default: command caller | Description: the user designated for the role check\n"
             "`match`: **Optional** | Default: None | Description: role to check, if no role is specified it returns "
             "a list of the person roles "
    )
    async def check_role(self, ctx: commands.Context, person: discord.Member = commands.Author,
                         match: discord.Role = None):
        role_list = []
        message = ""

        # Get the roles of the designated person
        for role in person.roles:
            role_list.append(role)

        if match is None:
            # Get the information and construct the message
            if person == ctx.author:
                message += "Your roles are:"
            else:
                message += f"{person.display_name} roles are:"

            message += "\n"

            for role in role_list:
                if role.name == "@everyone":
                    continue
                message += f"\t{role.name.capitalize()}\t\tID: {role.id}"
        # If argument was given
        elif isinstance(match, discord.Role):
            # Check for role
            has_role = False
            for role in role_list:
                if role.id == match.id:
                    has_role = True

            # Construct the message
            if has_role:
                if person == ctx.author:
                    message += "Yes! You have that role"
                else:
                    message += f"Yes! {person.display_name} has that role"
            else:
                if person == ctx.author:
                    message += "No! You don't have that role"
                else:
                    message += f"No! {person.display_name} doesn't have that role"

        await ctx.send(f"{message}")

    @check_role.error
    async def handle_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MemberNotFound):
            await ctx.send(f":warning: **{error}** :warning:")

    # slap command
    @commands.hybrid_command(
        name="slap",
        help="\tSlaps a random user for the specified argument.\n"
             "Command arguments:\n"
             "`argument`: **Required** | Description: the reason of such an aggressive act!"
    )
    async def slap(self, ctx, *, argument: Slap):
        await ctx.send(argument)

    # rock command
    @commands.hybrid_command(
        name="rock",
        help="\nMake the rock stare at any message!"
    )
    async def rock(self, ctx: commands.Context):
        rock = get_rock()
        if ctx.message.reference is None:
            await ctx.send(rock)
        else:
            message = await ctx.fetch_message(ctx.message.reference.message_id)
            await ctx.message.delete()
            await message.reply(rock)

    @commands.hybrid_command(
        name="say",
        help="Lemme say something!"
    )
    async def say(self, ctx: commands.Context, reply: str = "Hello!", amount: int = 1):
        if ctx.message.reference is None:
            for _ in range(amount):
                await ctx.send(reply)
            return
        message = await ctx.fetch_message(ctx.message.reference.message_id)
        await ctx.message.delete()
        for _ in range(amount):
            await message.reply(reply)


class BaseEvents(commands.Cog, name="BaseEvents"):
    """
    Basic chat events. Nothing to see really.
    """

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        def normalize(msg: str):
            try:
                if msg[0] in f"{string.punctuation} ":
                    msg = msg.replace(msg[0], "")
                    return normalize(msg)
                else:
                    return msg
            except IndexError:
                return msg

        if message.author == self.bot.user:
            return

        nicole_id = 911001450958708746
        if message.author.id == nicole_id:
            await message.add_reaction("🧁")
        if normalize(message.content.lower()).startswith("oho"):
            await message.channel.send(message.content)
