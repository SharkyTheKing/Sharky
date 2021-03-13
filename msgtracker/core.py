import asyncio
from math import ceil
from typing import Awaitable, Literal

import discord
from discord.ext import tasks
from redbot.core import Config, checks, commands
from redbot.core.utils.chat_formatting import box, pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, close_menu, menu
from redbot.core.utils.mod import is_mod_or_superior
from redbot.core.utils.predicates import MessagePredicate

from .dev_commands import MessageTrackerDev
from .mod_commands import ModCommands

# from redbot.core.i18n import Translator, cog_i18n


BASECOG = getattr(commands, "Cog", object)

GUILD_CONFIG = {
    "ignored_channels": [],
    "ignored_users": [],
    "enabled_system": False,
    "ignore_staff": False,
}

GLOBAL_CONFIG = {"disable_block_commands": False}

MEMBER_CONFIG = {"counter": 0}

# @cog_i18n(_)

# Possibly create a task to sync changes to config.

# TODO
# # Look into red_data_deletions


def customcheck():
    async def is_config_active(ctx: commands.Context):
        config = ctx.bot.get_cog("MsgTracker").config
        enable_config = await config.disable_block_commands()
        return True if not enable_config else False

    return commands.check(is_config_active)


class MsgTracker(BASECOG, MessageTrackerDev, ModCommands):
    """
    Tracks how many messages people send.

    Idea prompted by ShinJuri Discord, specifically Frostyy#1313 (526672641701183509)
    """

    def __init__(self, bot):
        self.bot = bot
        self.counted_message = {}
        self.config = Config.get_conf(self, identifier=252140347403141120, force_registration=True)
        self.config.register_guild(**GUILD_CONFIG)
        self.config.register_member(**MEMBER_CONFIG)
        self.config.register_global(**GLOBAL_CONFIG)
        self.task_update_config.start()

    def cog_unload(self):
        self.task_update_config.cancel()

    async def _return_yes_or_no(self, ctx):
        """
        Function for confirming changes.
        """
        confirm_yes_no = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=confirm_yes_no, timeout=50)
        except asyncio.TimeoutError:
            return False, await ctx.send("Took to long to reply, canceling process.")

        if confirm_yes_no.result is False:
            return False, None

        return True, None

    @commands.guild_only()
    @commands.command()
    @customcheck()
    async def trackignore(self, ctx):
        """
        Ignore yourself from message tracking.

        If you want to be tracked for your message count, you will need to contact the staff of the current server.
        """

        if ctx.author.id in await self.config.guild(ctx.guild).ignored_users():
            return await ctx.send(
                "You are already being ignored from tracking.\n\n"
                "If you'd like your messaged to be tracked, please contact the staff of this server."
            )

        status = "**ERROR: FAILED TO ADD YOU TO IGNORE LIST. CONTACT STAFF / BOT OWNER**"
        status_message = ""

        async with self.config.guild(ctx.guild).ignored_users() as blocked_user:
            blocked_user.append(ctx.author.id)
            status = "Added to ignore list."

        status_message += "Done. {}".format(status)

        await self.config.member(ctx.author).clear()  # clears this guild only.

        try:
            del self.counted_message[ctx.guild.id][ctx.author.id]
        except KeyError:
            pass

        await ctx.send(status_message)

    @commands.guild_only()
    @commands.command(name="msgleaderboard", aliases=["msglb"])
    async def message_leaderboard(self, ctx):
        """
        Message Tracker Leaderboard, displays all the members.

        [Credit to Core Economy](https://github.com/Cog-Creators/Red-DiscordBot/blob/dc68bc5d373c69aa1307ecef8118da14379ac67a/redbot/cogs/economy/economy.py#L545-L663)
        """
        try:
            self.counted_message[ctx.guild.id]
            update_config = await self.update_guild_config_from_cache(
                ctx.guild
            )  # updates from cache
            await self.remove_non_members_from_config()  # clears non_members

            if update_config is False:
                return await ctx.send("Something happened with updating. Please try again.")
        except KeyError:  # If it fails to have anything, we may assume that no messages have been sent.
            pass
        config_info = await self.config.all_members(ctx.guild)

        if not config_info:
            return await ctx.send("There is no tracked messages for this server.")

        if await self.config.guild(ctx.guild).enabled_system() is False:
            await ctx.send(
                "This server does not have this system enabled. We won't be tracking any new messages."
            )
            # Even if it's turned off, we should still allow it to be shown.

        async with ctx.typing():

            sorting_list = sorted(config_info.items(), key=lambda x: x[1]["counter"], reverse=True)

            pound_len = len(str(len(sorting_list)))
            top_message_len = len(str(sorting_list[0][1]["counter"]))

            embed_message = ""
            embed_header = "{pound:{pound_len}}{score:{bal_len}}{name:2}\n".format(
                pound="#",
                name="Name",
                score="Messages",
                bal_len=top_message_len + 8,
                pound_len=pound_len + 2,
            )
            footer_message = "Page {page_num}/{page_len}."  # Work this in somehow.

            base = discord.Embed(
                title="{guild}'s leaderboard".format(guild=ctx.guild.name), description=""
            )
            embed_list = []
            pos = 1
            new_embed = base.copy()
            embed_message = embed_header

            for user_id, counter in sorting_list:
                user = ctx.guild.get_member(user_id).display_name
                if user is None:
                    user = user_id

                if user_id != ctx.author.id:
                    embed_message += (
                        f"{f'{pos}.': <{pound_len+2}} "
                        f"{counter['counter']: <{top_message_len + 6}} {user}\n"
                    )
                else:
                    embed_message += (
                        f"{f'{pos}.': <{pound_len+2}} "
                        f"{counter['counter']: <{top_message_len + 6}} <<{ctx.author.display_name}>>\n"
                    )

                if pos % 10 == 0:
                    new_embed = base.copy()
                    new_embed.description = box(embed_message, lang="md")
                    new_embed.set_footer(
                        text=footer_message.format(
                            page_num=ceil(len(embed_list) + 1),
                            page_len=ceil(len(sorting_list) / 10),
                        )
                    )
                    embed_list.append(new_embed)
                    embed_message = embed_header

                pos += 1

            if embed_message != embed_header:
                new_embed = base.copy()
                new_embed.description = box(embed_message, lang="md")
                new_embed.set_footer(
                    text=footer_message.format(
                        page_num=ceil(len(embed_list) + 1), page_len=ceil(len(sorting_list) / 10)
                    )
                )
                embed_list.append(new_embed)

        if not embed_list:
            return await ctx.send("Sorry, no leaderboard to display.")

        await menu(
            ctx,
            embed_list,
            DEFAULT_CONTROLS if len(embed_list) > 1 else {"\N{CROSS MARK}": close_menu},
        )

    @tasks.loop(minutes=5)
    async def task_update_config(self):
        await self.bot.wait_until_red_ready()
        await self.update_config_from_cache()
        await self.remove_non_members_from_config()

    async def update_guild_config_from_cache(self, guild: discord.Guild) -> bool:
        """
        Updates from a single guild when leaderboard is used.

        To make sure there isn't that much config calls when not needed.
        """
        if not self.counted_message:
            return False

        try:
            user_messages = self.counted_message[guild.id]
        except KeyError:
            return False

        sorted_list = sorted(user_messages.items(), key=lambda x: x[1]["message"], reverse=True)
        for userid, counter in sorted_list:
            member = guild.get_member(userid)
            if not member:
                try:
                    member = await guild.fetch_member(userid)
                except discord.NotFound:
                    get_non_member_config = self.config.member_from_ids(guild.id, userid)
                    await get_non_member_config.clear()
                    try:
                        del self.counted_message[guild.id][userid]
                    except KeyError:
                        pass

                    continue

            current_points = self.config.member(member).counter
            adding_points = await current_points() + counter["message"]

            await current_points.set(adding_points)
        self.counted_message[guild.id] = {}

    async def remove_non_members_from_config(self):
        config_info = await self.config.all_members()
        for guild in config_info:
            for user in config_info[guild]:
                guild_ob = self.bot.get_guild(guild)
                if not guild_ob:
                    guild_ob = await self.bot.fetch_guild(guild)
                member = guild_ob.get_member(user)
                if not member:
                    try:
                        member = await guild_ob.fetch_member(user)
                    except discord.NotFound:
                        member_from_config = self.config.member_from_ids(guild_ob.id, user)
                        await member_from_config.clear()
                        try:
                            del self.counted_message[guild][user]
                        except KeyError:
                            pass

    async def update_config_from_cache(self):
        if not self.counted_message:  # No point attempting all of this if cache is nothing
            return False

        cache = self.counted_message
        guilds = await self.config.all_guilds()
        list_of_ids = []
        for guild in guilds:
            if guilds[guild]["enabled_system"]:
                list_of_ids.append(guild)

        for guild_id in list_of_ids:
            guild = self.bot.get_guild(guild_id)  # something errored out here
            if not guild:
                guild = await self.bot.fetch_guild(guild_id)
            try:
                user_messages = cache[guild.id]
            except KeyError:
                continue

            sorted_list = sorted(
                user_messages.items(), key=lambda x: x[1]["message"], reverse=True
            )

            for userid, counter in sorted_list:
                member = guild.get_member(userid)
                if not member:
                    try:
                        member = await guild.fetch_member(userid)
                    except discord.NotFound:
                        get_non_member_config = self.config.member_from_ids(guild.id, userid)
                        await get_non_member_config.clear()
                        try:
                            del self.counted_message[guild.id][userid]
                        except KeyError:
                            pass

                        continue

                current_points = self.config.member(member).counter
                adding_points = await current_points() + counter["message"]

                await current_points.set(adding_points)
        self.counted_message = {}
        return True

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        if not message.guild:
            return False

        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return False

        if message.author.bot:
            return False

        config_data = await self.config.guild(message.guild).all()

        if config_data["enabled_system"] is False:
            return False

        if message.author.id in config_data["ignored_users"]:
            return False

        if message.channel.id in config_data["ignored_channels"]:
            return False

        if config_data["ignore_staff"] is True:
            if await self.bot.is_mod_or_superior(message.author):
                return False

        try:
            self.counted_message[message.guild.id]
        except KeyError:
            self.counted_message.update({message.guild.id: {message.author.id: {"message": 1}}})
            return  # to prevent double message recording

        try:
            self.counted_message[message.guild.id][message.author.id]["message"] += 1
        except KeyError:
            self.counted_message[message.guild.id].update({message.author.id: {"message": 1}})
