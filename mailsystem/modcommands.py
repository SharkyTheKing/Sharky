from typing import Optional

import discord
from redbot.core import checks, commands
from redbot.core.utils.chat_formatting import box, pagify

from .mail_logic import MailLogic
from .mixins import MailSystemMixin


class ModCommands(MailSystemMixin):
    """
    Mod commands for guild staffs
    """

    @commands.group(name="mailset")
    async def mailsystem_settings(self, ctx: commands.Context):
        pass

    @checks.mod_or_permissions(manage_channels=True)
    @mailsystem_settings.group(name="mod")
    async def moderator_commands(self, ctx: commands.Context):
        """
        Moderator commands for Mailset
        """
        pass

    async def handle_user_config(self, ctx, user: int):
        check_tied = MailLogic.check_tied_for_user(self, user)
        if not check_tied:
            return False

        channel_obj = await self._return_channel_object(ctx, check_tied)

        if not channel_obj:
            return False

        if channel_obj.id not in ctx.guild.channels:
            return False

        await self.config.channel(channel_obj).user.clear()

    @moderator_commands.command(usage="<users>")
    async def blockuser(self, ctx: commands.Context, users: commands.Greedy[discord.User] = None):
        """
        Blocks/Unblocks the user from sending modmail tickets to your server.

        This will wipe their previous history assuming it's tied to your server.

        **Arguments:**
        - ``Users``: The user(s) you're wanting to block.
        """
        confirm_block = await self._return_guild_block(ctx.guild)
        if confirm_block:
            return await ctx.send(
                "Sorry, this guild is blocked from accessing the MailSystem commands."
            )

        if users is None:
            return await ctx.send_help()

        status = "Error"
        status_list = []

        async with self.config.guild(ctx.guild).ignore_users() as blocked_user:
            for user in users:
                if user.id not in blocked_user:
                    blocked_user.append(user.id)
                    status = "Added"
                    status_list.append("{} {}".format(user.mention, status))
                    await ModCommands.handle_user_config(self, ctx, user.id)
                    # need to handle logging if it does wipe the config...plan for the future.
                else:
                    blocked_user.remove(user.id)
                    status = "Removed"
                    status_list.append("{} {}".format(user.mention, status))

        status_message = ""
        if not status_list:
            return await ctx.send("Uh oh...Something happened. Unable to process user(s)")

        for status in status_list:
            status_message += "{}\n".format(status)

        message = "New status for listed users:\n{}".format(status_message)

        for page in pagify(message):
            await ctx.send(page, allowed_mentions=discord.AllowedMentions(users=False))

    @moderator_commands.command()
    async def userlist(self, ctx: commands.Context):
        """
        Displays all users blocked for mailsystem.

        This will display all users who are blocked from making a mailsystem ticket.
        """
        confirm_block = await self._return_guild_block(ctx.guild)
        if confirm_block:
            return await ctx.send(
                "Sorry, this guild is blocked from accessing the MailSystem commands."
            )

        ignore_config = await self.config.guild(ctx.guild).ignore_users()

        if not ignore_config:
            return await ctx.send("No one is being ignored.")

        if len(ignore_config) > 1:
            message = "Users on ignorelist:"
        else:
            message = "User on ignorelist:"

        for user in ignore_config:
            message += "\n\t- {}".format(user)

        for page in pagify(message):
            await ctx.send(box(page))
