import asyncio
import logging
from typing import Optional

import discord
from redbot.core import Config, checks, commands
from redbot.core.utils.chat_formatting import humanize_list
from redbot.core.utils.predicates import MessagePredicate

from .embedmodel import EmbedModels
from .mail_logic import MailLogic
from .mixins import MetaClass
from .settings import MailSettings
from .usercommands import UserCommands

BASECOG = getattr(commands, "Cog", object)

CHANNEL_CONFIG = {"user": None}
GLOBAL_CONFIG = {"enable_commands": True}
GUILD_CONFIG = {
    "category": None,
    "activation": False,
    "mail_log_channel": None,
    "enable_embeds": True,
}

mixinargs = (MailSettings, UserCommands, BASECOG)


def customcheck():
    async def is_config_active(ctx: commands.Context):
        config = ctx.bot.get_cog("MailSystem").config
        enable_config = await config.enable_commands()
        return False if not enable_config else True

    return commands.check(is_config_active)


class MailSystem(*mixinargs, metaclass=MetaClass):
    """
    Mail System, members DM the bot to send mails for your staff.

    **This is currently in testing. Please review the warning message.** `[p]mailset warn`
    """

    __version__ = "0.0.5"
    __author__ = ["SharkyTheKing", "Kreusada"]

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2061809260515)
        self.config.register_guild(**GUILD_CONFIG)
        self.config.register_channel(**CHANNEL_CONFIG)
        self.config.register_global(**GLOBAL_CONFIG)
        self.start_system = self.bot.loop.create_task(self._update_cache())
        self.cache = {}
        self.sent_mail = discord.Color.green()
        self.received_mail = discord.Color.red()
        self.log = logging.getLogger("red.cogs.MailSystem")

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        authors = humanize_list(self.__author__)
        return f"{context}\n\nAuthors: {authors}\nVersion: {self.__version__}"

    async def returning_content(self, ctx: commands.Context, contents: str, anonymous: bool):
        """
        A regular message that get's sent to either staff or user
        """
        if anonymous:
            return f"**Anonymous Staff: {contents}**"
        else:
            return f"**{ctx.author.name}: {contents}**"

    async def _return_embed_or_content(self, ctx) -> bool:
        context = await self.config.guild(ctx.guild).embed_embeds()
        return True if context else False

    async def _return_yes_or_no(self, ctx: commands.Context):
        """
        Internal function for confirmation.
        """
        confirm_yes_no = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=confirm_yes_no, timeout=50)
        except asyncio.TimeoutError:
            await ctx.send("Took to long to reply, canceling process.")
            return False
        if not confirm_yes_no.result:
            await ctx.send("Okay, canceled process.")
            return False
        return True

    async def _return_channel_or_no(self, ctx: commands.Context):
        """
        Internal function to return a confirmed channel object.
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            message = await ctx.bot.wait_for("message", check=check, timeout=25)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply, canceling action.")
            return False
        return message

    async def _return_user_object(self, ctx: commands.Context, user_id):
        """
        Internal Function to return User Object

        Returns False if failed
        """
        user = ctx.bot.get_user(user_id)
        if not user:
            try:
                user = await ctx.bot.fetch_user(user_id)
            except discord.HTTPException:
                return False
        return user

    async def _return_channel_object(self, ctx: commands.Context, channel_id):
        """
        Internal function to return Channel Object

        Returns False if failed
        """
        channel = ctx.bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await ctx.bot.fetch_channel(channel_id)
            except discord.HTTPException:
                return False
        return channel

    async def _send_user_embed(self, user: discord.User, embed):
        """
        Internal function to send user an embed

        Returns False if failed
        """
        try:
            await user.send(embed=embed)
        except discord.HTTPException:
            return False
        return True

    async def _send_user_content(self, user: discord.User, content: str):
        """
        Internal function to send a user a message

        Return False if failed
        """
        try:
            await user.send(content)
        except discord.HTTPException:
            return False
        return True

    async def _send_channel_embed(self, channel: discord.TextChannel, embed):
        """
        Internal function to send a channel an embed

        Returns False if failed
        """
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            return False
        return True

    async def _send_channel_content(self, channel: discord.TextChannel, content: str):
        """
        Internal function to send a channel a message

        Returns False if failed
        """
        try:
            await channel.send(content)
        except discord.HTTPException:
            return False
        return True

    def _return_embed_to_user(self, ctx, contents, toggle):
        return EmbedModels.embed_to_user(self, ctx, contents, toggle)

    def _return_user_embed_for_mod(self, ctx, embed, toggle):
        return EmbedModels.user_embed_for_mods(self, ctx, embed, toggle)

    def _return_embed_to_mod(self, ctx, contents):
        return EmbedModels.embed_to_moderators(self=self, ctx=ctx, contents=contents)

    def _return_mod_embed_for_user(self, embed):
        return EmbedModels.mod_embed_for_user(self=self, embed=embed)

    def _return_channel_tied_to_user(self, author):
        return MailLogic.check_tied_for_user(self, author.id)

    def _return_user_tied_to_channel(self, channel):
        return MailLogic.check_tied_for_channel(self, channel.id)

    @commands.command(usage="[anonymous=False] <Message To User>")
    @commands.guild_only()
    async def reply(
        self, ctx: commands.Context, anonymous: Optional[bool] = False, *, contents: str
    ):
        """
        Sends a message back to the user.

        This will display the moderator's name back to the user.

        **Arguments:**
        - ``[anonymous]``: Whether to make the reply anonymous. Defaults to False.
        - ``<contents>``: The message to reply back to the user with.
        """
        channel_cache = MailLogic.check_tied_for_channel(self, ctx.channel.id)

        if not channel_cache:
            return await ctx.send("This channel is not tied to a user. Please delete channel.")
        user_embed = self._return_embed_to_user(ctx=ctx, contents=contents, toggle=anonymous)

        user = await self._return_user_object(ctx, channel_cache)
        if user is False:
            return await ctx.send(
                "Unable to find user. Either this is done in error or they went poof from Discord."
            )
        sent_mail = await self._send_user_embed(user, user_embed)
        if not sent_mail:
            return await ctx.send("Unable to send mesasge to user.")
        mod_embed = self._return_user_embed_for_mod(ctx=ctx, embed=user_embed, toggle=anonymous)

        await ctx.send(embed=mod_embed)

    @commands.command(usage="<reason to close>")
    @checks.mod_or_permissions(manage_channels=True)
    @commands.guild_only()
    async def closemail(self, ctx: commands.Context, *, reason: Optional[str]):
        """
        Closes the modmail between the channel and user.
        """
        guild_config = await self.config.guild(ctx.guild).all()
        if ctx.channel.category.id != guild_config["category"]:
            return await ctx.send("This channel is not in the MailSystem category.")
        if ctx.channel.id == guild_config["mail_log_channel"]:
            return await ctx.send("You can't close the log channel.")
        user_from_channel = self._return_user_tied_to_channel(ctx.channel)

        delete_channel = await MailLogic.delete_channel_for_user(self, ctx.channel)

        if not delete_channel:
            return await ctx.send("**Error: Unable to delete channel.**")
        if not user_from_channel:
            return await MailLogic._record_channel_deletion(self, ctx, reason)
        remove_config_cache_info = await MailLogic._remove_channel_info(self, ctx.channel)

        # keeping this for future idea

        await MailLogic._record_channel_deletion(self, ctx, reason, user_from_channel)

    async def _update_cache(self):
        """
        Update cache with config information
        """
        await self.bot.wait_until_red_ready()
        for guild in self.bot.guilds:
            category = await self.config.guild(guild).category()
            if category:
                chan = await self.bot.fetch_channel(category)
                for channel in chan.channels:
                    user = await self.config.channel(channel).user()
                    if user:
                        self.cache.update({channel.id: user})

    def cog_unload(self):
        self.start_system.cancel()


# TODO Work on on_message event handling.
#    @commands.Cog.listener()
#    async def on_message(self, message: discord.Message):
#        """
#        On_message event for mailsystem.
#
#        This will only be triggered if enable_commands is False
#        """
#        if message.guild:
#            return  # Don't participate in a guild message
#
#        if await self.config.enable_commands() is True:
#            return  # If command usage is on, don't use on_message.
#
#        user_cache = self._return_channel_tied_to_user(self, message.author.id)
#
#        ctx = await self.bot.get_context(message)
#
#        if not user_cache:
#            send_message = await self._send_user_content(message.author, "Do you want to create a mail ticket?")
#            if send_message is False:
#                return  # in case something fails, don't continue.
#
#            confirm = await self._return_yes_or_no(ctx)
#            if not confirm:
#                return False
#
#            new_ticket = await self._create_new_ticket(self, ctx)
#            if not new_ticket:
#                return False
#
#            embed = self._return_embed_to_mod(ctx, message.content)
#            if not embed:
#                ...
#
#            send = await self._send_channel_embed(new_ticket, embed)
#            if not send:
#                return await message.author.send("Error. Couldn't send ticket. Please contact the staff of the server.")
#
#        elif ...:
#            ...
