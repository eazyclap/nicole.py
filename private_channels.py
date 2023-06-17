import discord
import json
from discord.ext import commands


general_database = {}
private_channels_database = {}


def save_private_voice_channels(server_id: int):
    global general_database
    with open("./private_channels.json", mode="r") as file:
        general_database = json.load(file)

    general_database[f"{server_id}"] = private_channels_database

    with open("./private_channels.json", mode="w") as file:
        json.dump(general_database, file, indent=4)


def get_private_voice_channels(server_id: int):
    global private_channels_database
    with open("./private_channels.json", mode="r") as file:
        private_channels_database = json.load(file)[f"{server_id}"]


def user_has_private_channel(ctx: commands.Context):
    global private_channels_database
    get_private_voice_channels(ctx.guild.id)

    return str(ctx.author.id) in private_channels_database.keys()


class PrivateChannels(commands.Cog):
    """
    Commands for private channels.
    Includes commands to request access to user's private channels.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="request",
        help="\nRequest access to an user's private channel. Types accepted: JOIN or ROLE."
    )
    async def request(self, ctx: commands.Context, channel_owner: discord.Member, request_type: str = "JOIN",
                      knock: bool = False):
        # Get data
        get_private_voice_channels(ctx.guild.id)
        monitor_reaction = []

        async def stop_monitoring(delete_msg: discord.Message):
            await delete_msg.delete()
            for index, msg_id in enumerate(monitor_reaction):
                if msg_id == delete_msg.id:
                    monitor_reaction.pop(index)

        # Owner has a private channel?
        if str(channel_owner.id) not in private_channels_database.keys():
            await ctx.send(f"Sorry, the user {channel_owner.display_name} does not have a private channel!")
            return

        # Fetch data
        data = private_channels_database[str(channel_owner.id)]

        private_channel_id = data["private_channel_id"]
        contact_channel_id = data["contact_channel_id"]
        role_id = data["role_id"]
        restricted_users = data["restricted_users"]
        channel_status = data["status"]

        # User is restricted?
        if ctx.author.id in restricted_users:
            await ctx.send(
                f"Sorry, you have been restricted from requesting access to {channel_owner.display_name} channel!")
            return

        # User not in any waiting room? (Cannot be moved)
        if ctx.author.voice is None and request_type == "JOIN":
            await ctx.send(f"Sorry, it seems you are not connected to any voice channel in this server!")
            return

        # User wants to join? Channel open? Closed? Invisible?
        # Office is empty? Owner not in? Owner in another channel?
        if request_type == "JOIN":
            if channel_status == "open":
                await ctx.author.move_to(self.bot.get_channel(private_channel_id))
                await ctx.send("Office open, moving you in!")
                return
            elif channel_status == "closed":
                await ctx.send("Sorry, the channel you're trying to access is closed and does not accept requests!")
                return
            elif channel_status == "invisible":
                await ctx.send(f"Sorry, the user {channel_owner.display_name} is currently not in the channel!")
                return

            if channel_owner.voice is None or len(self.bot.get_channel(private_channel_id).members) == 0:
                # User not connected to voice chat
                await ctx.send(f"Sorry, the user {channel_owner.display_name} is currently not in the channel!")
                return
            elif not channel_owner.voice.channel.id == private_channel_id:
                # User is not in his channel
                await ctx.send(f"Sorry, the user {channel_owner.display_name} is currently in another channel!")
                return

        # Request carried
        response = await ctx.send("Request sent!")
        if knock and request_type == "JOIN":
            channel = self.bot.get_channel(private_channel_id)
            await channel.connect()
            await ctx.voice_client.disconnect(force=False)

        request_type = request_type.upper()

        # Request correct?
        if not (request_type == "JOIN" or request_type == "ROLE"):
            await ctx.send("Sorry, your request is not type **join** or **role**, please check your input!")
            return
        else:
            request_channel = self.bot.get_channel(contact_channel_id)
            message = await request_channel.send(
                f"{channel_owner.mention}\n"
                f"**{request_type} REQUEST:**\n"
                f"*User:* {ctx.author.mention}\n"
                f"*Channel:* {self.bot.get_channel(private_channel_id)}\n\n"
                f"👍: Accept\n\n"
                f"👎: Deny\n\n"
                f"🟨: Restrict new requests from {ctx.author.mention}\n\n"
                f"⚫: Deny and put channel on invisible"
            )
            await message.add_reaction("👍")
            await message.add_reaction("👎")
            await message.add_reaction("🟨")
            await message.add_reaction("⚫")
            monitor_reaction.append(message.id)

            @self.bot.event
            async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
                if reaction.message.id in monitor_reaction and reaction.emoji in ["👍", "👎", "🟨", "⚫"]:
                    request_processed = False
                    order = reaction.emoji

                    # Request accepted? Denied? Other options?
                    if order == "👍":
                        if request_type == "JOIN":
                            await ctx.author.move_to(self.bot.get_channel(private_channel_id))
                            await response.edit(content="Your request has been accepted!")
                            request_processed = True
                        elif request_type == "ROLE":
                            role = ctx.guild.get_role(role_id)
                            await ctx.author.add_roles(role)
                            await response.edit(content="Your request has been accepted!")
                            request_processed = True
                    elif order == "👎":
                        await response.edit(content="Your request has been denied.")
                        request_processed = True
                    elif order == "🟨":
                        # Edit database instead of local data
                        private_channels_database[str(channel_owner.id)]["restricted_users"].append(ctx.author.id)
                        await response.edit(content="Your request has been denied.")
                        request_processed = True
                    elif order == "⚫":
                        # Edit database instead of local data
                        private_channels_database[str(channel_owner.id)]["status"] = "invisible"
                        await response.edit(content="Your request has been denied.")
                        request_processed = True

                    # Request processed?
                    if request_processed:
                        await reaction.message.channel.send(
                            f"{request_type} request from {ctx.author.mention}: {order}")
                        await stop_monitoring(message)
                        # Save data
                        save_private_voice_channels(ctx.guild.id)
                        return

    @commands.hybrid_command(
        name="restrict",
        help="\nRestrict a user from making requests to your channel"
    )
    @commands.check(user_has_private_channel)
    async def restrict(self, ctx: commands.Context, user: discord.Member):
        global private_channels_database
        get_private_voice_channels(ctx.guild.id)

        # User already restricted?
        if user.id in private_channels_database[str(ctx.author.id)]["restricted_users"]:
            await ctx.send(f"User {user.display_name} already restricted for this channel!")
            return

        # Carry the request
        private_channels_database[f"{ctx.author.id}"]["restricted_users"].append(user.id)
        await ctx.send(f"{user.display_name} restricted successfully!")
        save_private_voice_channels(ctx.guild.id)
        return

    @restrict.error
    async def handle_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Sorry! It looks like you don't have a private channel!")

    @commands.hybrid_command(
        name="unrestrict",
        help="\nAllow a user to make requests to your channel, works if the user was previously restricted."
    )
    @commands.check(user_has_private_channel)
    async def unrestrict(self, ctx: commands.Context, user: discord.Member):
        global private_channels_database
        get_private_voice_channels(ctx.guild.id)

        # User not restricted in the first place?
        if user.id not in private_channels_database[f"{ctx.author.id}"]["restricted_users"]:
            await ctx.send("The specified user has no restriction in this channel!")
            return

        # Carry request
        for index, restricted_id in enumerate(private_channels_database[f"{ctx.author.id}"]["restricted_users"]):
            if restricted_id == user.id:
                private_channels_database[f"{ctx.author.id}"]["restricted_users"].pop(index)
        await ctx.send(f"User {user.display_name} successfully unrestricted!")
        save_private_voice_channels(ctx.guild.id)
        return

    @unrestrict.error
    async def handle_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Sorry! It looks like you don't have a private channel!")

    @commands.hybrid_command(
        name="setstatus",
        help="Set a status for your private channel. Available statuses are OPEN, INVITE, CLOSED and INVISIBLE"
    )
    @commands.check(user_has_private_channel)
    async def setstatus(self, ctx: commands.Context, status: str):
        global private_channels_database
        if status.lower() not in ["open", "invite", "closed", "invisible"]:
            await ctx.send("Sorry, you can only set your channel as open, invite, closed or invisible!")
            return

        get_private_voice_channels(ctx.guild.id)
        private_channels_database[f"{ctx.author.id}"]["status"] = status.lower()
        save_private_voice_channels(ctx.guild.id)
        await ctx.send(f"Successfully changed the status of your channel to {status.capitalize()}!")
        return
