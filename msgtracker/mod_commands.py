import asyncio
from typing import Optional

import discord
from redbot.core import checks, commands
from redbot.core.utils.chat_formatting import box, pagify


class ModCommands:
    """
    Mod/Admin commands for Message Tracker.

    Where the settings are set.
    """

    @commands.guild_only()
    @checks.mod_or_permissions(manage_channels=True)
    @commands.group(name="mtset", aliases=["msgtset"])
    async def messagecounter_settings(self, ctx):
        """
        Message Count Settings.

        Members are allowed to deny permission from being tracked for privacy reasons unless the Bot Owner sets differently.
        """
        pass

    @checks.admin()
    @messagecounter_settings.group(name="admin")
    async def admin_control(self, ctx):
        """
        Administration commands.

        Allows you to nuke someone's history from record or adjust their count.
        """
        pass

    @checks.is_owner()
    @admin_control.command(name="nukeconfig")
    async def nuke_message_config(self, ctx):
        """
        [BOT OWNER] Nukes all recorded counters.

        This will nuke every messages that's been counted. Do so at your own risk.
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send(
            "Are you sure you want to nuke all member's config? This will reset counters for everyone on every server. (Yes/No)"
        )

        try:
            confirm_action = await ctx.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply...")
            return False

        if confirm_action.content.lower() != "yes":
            await ctx.send("Okay. Won't nuke config.")
            return

        await self.config.clear_all_members()
        await ctx.send("Done. Config has been nuked.")

    @checks.is_owner()
    @admin_control.command(name="blockignore")
    async def block_user_ignoring(self, ctx):
        """
        [BOT OWNER] Disables `[p]trackignore` command for users
        """
        current_setting = await self.config.disable_block_commands()

        if current_setting is False:
            await self.config.disable_block_commands.set(True)
            return await ctx.send("Members can no longer set the bot to ignore them.")
        else:
            await self.config.disable_block_commands.set(False)
            return await ctx.send("Members can set the bot to ignore them now.")

    @checks.is_owner()
    @admin_control.command(name="cache")
    async def message_track_cache(self, ctx, guild: Optional[discord.Guild]):
        """
        [BOT OWNER] Check cached messages counter for this server.
        """
        if not self.counted_message:
            return await ctx.send("No messages tracked.")

        list_words = []

        guild = guild or ctx.guild

        try:
            sorting_list = sorted(
                self.counted_message[guild.id].items(),
                key=lambda x: x[1]["message"],
                reverse=True,
            )
        except KeyError:
            return await ctx.send(
                "Sorry, there's currently no messages being tracked for this server."
            )
        except AttributeError:
            return await ctx.send("Sorry, there's currently no messages for that.")

        for userid, counter in sorting_list:
            list_words.append("{} {} messages".format(userid, counter["message"]))

        if not list_words:
            return False

        message_to_user = "Leaderboard:"

        for msg in list_words:
            message_to_user += "\n\t- {}".format(msg)

        for page in pagify(message_to_user):
            await ctx.send(box(page))

    @checks.is_owner()
    @admin_control.command(name="updateconfig")
    async def update_message_config(self, ctx):
        """
        [BOT OWNER] Updates to config manually
        """
        if not self.counted_message:
            return await ctx.send("Nothing to update")
        await self.update_config_from_cache()
        await ctx.send("Done. Config updated and cache reset.")

    @admin_control.command()
    async def counter(self, ctx, member: discord.Member, points: int):
        """
        Change a member's recorded message count.
        """
        await self.config.member(member).counter.set(points)
        await ctx.send(
            "Done. {} now has {} total messages counted.".format(member.mention, points)
        )

    @admin_control.command()
    async def deletecount(self, ctx, member: discord.Member):
        """
        Will delete the member's entire record.

        Will ask for confirmation if you want to do this.
        """
        await ctx.send("Are you sure you want to delete {}'s record?".format(member.display_name))

        confirm, message = await self._return_yes_or_no(ctx)

        if not confirm and message is not None:
            return False

        if not confirm and message is None:
            return await ctx.send("Okay, won't delete {}'s record.".format(member.display_name))
        await self.config.member(member).clear()
        await ctx.send("Done. Removed {}'s history".format(member.display_name))

    @admin_control.command()
    async def resetguild(self, ctx):
        """
        Will delete Guild's recorded members.

        Will ask for confirmation if you want to do this.
        """
        await ctx.send("Are you sure you want to delete the server's record?")
        confirm, message = await self._return_yes_or_no(ctx)

        if not confirm and message is not None:
            return False

        if not confirm and message is None:
            return await ctx.send("Okay, won't delete the server's record.")

        await self.config.clear_all_members(ctx.guild)

        await ctx.send("Done. Wiped guild's message history.")

    @messagecounter_settings.command(name="enable", usage="")
    async def enable_disable_system(self, ctx):
        """
        Enables / Disables system.

        This will do it automatically based on what the previous setting is.
        """
        enabled_config = await self.config.guild(ctx.guild).enabled_system()
        if enabled_config is False:
            await self.config.guild(ctx.guild).enabled_system.set(True)
            return await ctx.send("The system is now enabled.")
        else:
            await self.config.guild(ctx.guild).enabled_system.set(False)
            return await ctx.send("The system is now disabled.")

    @messagecounter_settings.group(name="ignore")
    async def ignore_group_setting(self, ctx):
        """
        Ignore users / channels from message tracking.
        """
        ...

    @ignore_group_setting.command(name="user", usage="<users>")
    async def block_user_tracking(self, ctx, users: commands.Greedy[discord.User] = None):
        """
        This blocks the user(s) from being tracked.

        To remove someone from the list, use the command again with the same user.

        Members will have access to a command that lets them do it themselves if they so choose.
        """
        if users is None:
            return await ctx.send_help()

        status = "Error"
        status_list = []

        async with self.config.guild(ctx.guild).ignored_users() as blocked_user:
            for user in users:
                if user.id not in blocked_user:
                    blocked_user.append(user.id)
                    status = "Added"
                    status_list.append("{} {}".format(user.mention, status))
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
            await ctx.send(page)

    @ignore_group_setting.command(name="channel", usage="<channel>")
    async def ignore_channel_tracking(
        self, ctx, channels: commands.Greedy[discord.TextChannel] = None
    ):
        """
        This will ignore/unignore a channel from message tracking.

        If a channel is added to the list, type it again to remove it.
        """
        if channels is None:
            return await ctx.send_help()
        status = "Error"
        status_list = []

        async with self.config.guild(ctx.guild).ignored_channels() as chan:
            for channel in channels:
                if channel.id not in chan:
                    chan.append(channel.id)
                    status = "Added"
                    status_list.append("{} {}".format(channel.mention, status))
                else:
                    chan.remove(channel.id)
                    status = "Removed"
                    status_list.append("{} {}".format(channel.mention, status))

        status_message = ""
        if not status_list:
            return await ctx.send("Uh oh...Something happened. Unable to process channel(s)\n")
        for stat in status_list:
            status_message += "{}\n".format(stat)

        msg = "New status for listed channels:\n{}".format(status_message)
        for page in pagify(msg):
            await ctx.send(page)

    @ignore_group_setting.command(name="mods", usage="")
    async def ignore_staff_tracking(self, ctx):
        """
        Ignores/Unignores staff of a server.

        This will do it automatically based on what the previous setting is.
        """
        ignore_staffs = await self.config.guild(ctx.guild).ignore_staff()
        if ignore_staffs is False:
            await self.config.guild(ctx.guild).ignore_staff.set(True)
            return await ctx.send(
                "Will now ignore staff members, as assigned by the bot in `{}set.`".format(
                    ctx.prefix
                )
            )
        else:
            await self.config.guild(ctx.guild).ignore_staff.set(False)
            return await ctx.send("Will now listen to staff members.")

    @messagecounter_settings.command(
        name="showsettings", aliases=["showsetting", "ss", "list"], usage=""
    )
    async def guild_showsettings(self, ctx):
        """
        Display guild specific settings.

        This will not display blocked users, please use `[p]mtset ignorelist`.
        This will not display ignored channels, please use `[p]mtset channellist`.
        """
        guild_config = await self.config.guild(ctx.guild).all()
        block_info = await self.config.disable_block_commands()
        embed = discord.Embed()
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.title = "{}'s Guild Settings".format(ctx.guild.name)

        embed.add_field(
            name="System:", value="is Enabled" if guild_config["enabled_system"] else "is Disabled"
        )
        embed.add_field(
            name="Ignore Staff:", value="True" if guild_config["ignore_staff"] else "False"
        )
        embed.add_field(
            name="Block Setting:",
            value="Users can disallow the bot from tracking."
            if block_info is False
            else "Users can not disallow the bot from tracking.",
            inline=False,
        )

        await ctx.send(embed=embed)

    @messagecounter_settings.command(name="userlist", usage="")
    async def display_ignorelist(self, ctx):
        """
        Displays users who are being ignored from tracking.

        [Thank you Core Red](https://github.com/Cog-Creators/Red-DiscordBot/blob/e24379973cc4373a20a528543d21b1194e788800/redbot/core/core_commands.py#L2880-L2898)
        """
        ignore_config = await self.config.guild(ctx.guild).ignored_users()

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

    @messagecounter_settings.command(name="channellist", usage="")
    async def display_ignoredchannel(self, ctx):
        """
        Displays channels that are being ignored from tracking.

        [Thank you Core Red](https://github.com/Cog-Creators/Red-DiscordBot/blob/e24379973cc4373a20a528543d21b1194e788800/redbot/core/core_commands.py#L2880-L2898)
        """
        ignore_channels = await self.config.guild(ctx.guild).ignored_channels()

        if not ignore_channels:
            return await ctx.send("No channels are being ignored.")

        if len(ignore_channels) > 1:
            message = "Channels on ignorelist:"
        else:
            message = "Channel on ignorelist:"

        for channel in ignore_channels:
            message += "\n\t- {}".format(channel)

        for page in pagify(message):
            await ctx.send(box(page))
