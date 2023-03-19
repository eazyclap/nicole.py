import discord
import json
from discord.ext import commands


locked_voice_channels = []


def is_master(ctx: commands.Context):
    return ctx.author.id == 414379654728777729


class Lockdown(commands.Cog):
    """
    Commands to lock a channel, preventing users out of the whitelist to join
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def save_locked_voice_channels():
        with open("./lockdown_vc.json", mode="w") as file:
            json.dump({"lockdown": locked_voice_channels}, file, indent=4)

    @commands.hybrid_command(
        name="lock",
        help="\nLocks a channel down, preventing any other members to join."
    )
    @commands.check(is_master)
    async def lock(self, ctx: commands.Context, channel: discord.VoiceChannel):
        people_in_channel = [member.id for member in channel.members]
        global locked_voice_channels
        locked_voice_channels.append(
            {
                "id": channel.id,
                "except": people_in_channel
            }
        )
        self.save_locked_voice_channels()
        await ctx.send("Right away master!")

    @lock.error
    async def handle_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Seems like you don't have the permission to execute this command!")

    @commands.hybrid_command(
        name="unlock",
        help="\nUnlocks a locked channel."
    )
    @commands.check(is_master)
    async def unlock(self, ctx: commands.Context, channel: discord.VoiceChannel):
        global locked_voice_channels
        for index, vc in enumerate(locked_voice_channels):
            if vc["id"] == channel.id:
                locked_voice_channels.pop(index)
                break
        self.save_locked_voice_channels()
        await ctx.send("Right away master!")

    @unlock.error
    async def handle_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Seems like you don't have the permission to execute this command!")

    @commands.hybrid_command(
        name="whitelist",
        help="\nGrants permission to enter a specified locked channel to a user."
    )
    @commands.check(is_master)
    async def whitelist(self, ctx: commands.Context, channel: discord.VoiceChannel, member: discord.Member):
        global locked_voice_channels
        for blocked_channel in locked_voice_channels:
            if channel.id == blocked_channel["id"]:
                blocked_channel["except"].append(member.id)
                self.save_locked_voice_channels()
                await ctx.send(f"{member.mention} added to the whitelist for channel {channel.name}!")
                return
        else:
            await ctx.send("The channel is not locked!")

    @whitelist.error
    async def handle_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Seems like you don't have the permission to execute this command!")

    @commands.hybrid_command(
        name="unlist",
        help="\nRevokes permission to enter a specified locked channel to a user."
    )
    @commands.check(is_master)
    async def unlist(self, ctx: commands.Context, channel: discord.VoiceChannel, member: discord.Member):
        global locked_voice_channels

        if member in channel.members:
            await member.move_to(None)

        for blocked_channel in locked_voice_channels:
            if channel.id == blocked_channel["id"]:
                for index, excepted_id in enumerate(blocked_channel["except"]):
                    if excepted_id == member.id:
                        blocked_channel["except"].pop(index)
                self.save_locked_voice_channels()
                await ctx.send(f"{member.mention} removed from the whitelist for channel {channel.name}!")
                return
        else:
            await ctx.send("The channel is not locked!")

    @unlist.error
    async def handle_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("Seems like you don't have the permission to execute this command!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel is None or member.id is self.bot.user.id:
            return
        for blocked_channel in locked_voice_channels:
            if after.channel.id == blocked_channel["id"] and member.id not in blocked_channel["except"]:
                await member.move_to(None)
