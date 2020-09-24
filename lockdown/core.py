import asyncio
import logging
from typing import Union

import discord
from redbot.core import Config, checks, commands
from redbot.core.utils import menus
from redbot.core.utils.chat_formatting import box, pagify
from redbot.core.utils.predicates import MessagePredicate

DEF_GUILD = {
    "channels": [],
    "lockdown_message": None,
    "unlockdown_message": None,
    "confirmation_message": False,
}

BASECOG = getattr(commands, "Cog", object)

# TODO Figure out how to display which channels failed to locked/unlocked
# TODO Figure out how to display which channel failed to send messages
# TODO Possibly combine send_message and channel_lock/unlock to prevent posting when channel fails to lock/unlock
# TODO Custom role to overwrite, instead of default @everyone
# TODO Possibly look into standard message vs embed optionality
# ---- TODO if above is done, create dict and account for migration
# TODO Add proper logging to every failed task.
# TODO Pagify showsettings embeds
# TODO Change out commands.Greedy to *, look into possibility of doing this.
# TODO Look into pre-checking channel/channels perms

# ---- Doing ----
# TODO Pagify showsettings

# ---- Resolved ----
# Wipe config per guild: Locked to admin/owner only.
# Look into making confirmation_message a staticmethod/function?
# Look into Union for int removal or add another command specific for this.


class Lockdown(BASECOG):
    """
    Lockdown guilds or selective channels.

    Note: You must have permissions set properly for the bot for this to work properly.
    """

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("red.cogs.lockdown")

        self.config = Config.get_conf(self, identifier=548498634843)
        self.config.register_guild(**DEF_GUILD)

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    @staticmethod
    def retrieve_overwrite(
        channel: Union[discord.TextChannel, discord.VoiceChannel], overwrite, lock_or_unlock: str
    ):
        """
        Returns overwrite setting depending on channel type
        """
        if lock_or_unlock == "lock":
            if isinstance(channel, discord.TextChannel):  # verify channel type
                overwrite.update(send_messages=False)
            else:
                overwrite.update(connect=False)

        elif lock_or_unlock == "unlock":
            if isinstance(channel, discord.TextChannel):
                overwrite.update(send_messages=None)
            else:
                overwrite.update(connect=None)

        return overwrite

    async def confirm_action(self, message: str, ctx):
        """
        MessagePredicate.yes_or_no confirmation
        """
        await ctx.send(message)
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await self.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send("Responsed timed out. Won't complete process.")
            return False

        if pred.result is False:
            await ctx.send("Okay. Stopped process.")
            return False

        return True

    @commands.command()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)
    # Don't be stupid shark..make sure unlockdown has same perm check
    async def lockdown(self, ctx):
        """
        Lockdown the guild.

        Locks every channel that's in config.
        """
        if await self.config.guild(ctx.guild).confirmation_message() is True:
            confirm = await self.confirm_action(
                "Are you sure you want to lock the guild? If so, please type `yes`, otherwise type `no`.",
                ctx,
            )
            if confirm is False:
                return

        role = ctx.guild.default_role
        # Allow for customization of roles in the future...if I'm smart enough to

        # Gather config
        lock_message = await self.config.guild(ctx.guild).lockdown_message()
        channel_ids = await self.config.guild(ctx.guild).channels()

        if not channel_ids:
            return await ctx.send(
                "Error: There are no channels stored. Please add channels to be able to lockdown the guild."
            )

        for guild_channel in ctx.guild.channels:
            if guild_channel.id in channel_ids:
                overwrite = guild_channel.overwrites_for(role)
                overwrite = self.retrieve_overwrite(guild_channel, overwrite, "lock")
                try:
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown in effect. Requested by {} ({})".format(
                            ctx.author.name, ctx.author.id
                        ),
                    )
                except discord.Forbidden:
                    self.log.info(
                        "Could not lockdown {} ({}): Missing permissions".format(
                            guild_channel.name, guild_channel.id
                        )
                    )

                if lock_message:
                    try:
                        await guild_channel.send(lock_message)
                    except discord.Forbidden:
                        self.log.info(
                            "Could not send message to {} ({})".format(
                                guild_channel.name, guild_channel.id
                            )
                        )

        await ctx.send(
            "Guild is locked. You can unlock the guild by doing `{}unlockdown`\n".format(
                ctx.prefix
            )
        )

    @commands.command()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)  # good job shark. You did it right
    async def unlockdown(self, ctx):
        """
        Ends the lockdown for the guild
        """
        if await self.config.guild(ctx.guild).confirmation_message() is True:
            confirm = await self.confirm_action(
                "Are you sure you want to unlock the guild? If so, please type `yes`, otherwise type `no`.",
                ctx,
            )
            if confirm is False:
                return

        # Gather config
        lock_message = await self.config.guild(ctx.guild).lockdown_message()
        channel_ids = await self.config.guild(ctx.guild).channels()

        if not channel_ids:
            return await ctx.send(
                "Error: There are no channels stored. Please add channels to be able to unlock the guild."
            )

        role = ctx.guild.default_role

        for guild_channel in ctx.guild.channels:
            if guild_channel.id in channel_ids:
                overwrite = guild_channel.overwrites_for(role)
                overwrite = self.retrieve_overwrite(guild_channel, overwrite, "unlock")
                try:
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Unlock in effect. Requested by {} ({})".format(
                            ctx.author.name, ctx.author.id
                        ),
                    )
                except discord.Forbidden:
                    self.log.info(
                        "Could not unlock {} ({}): Missing permissions".format(
                            guild_channel.name, guild_channel.id
                        )
                    )

                if lock_message:
                    try:
                        await guild_channel.send(lock_message)
                    except discord.Forbidden:
                        self.log.info(
                            "Could not send message to {} ({})".format(
                                guild_channel.name, guild_channel.id
                            )
                        )

        await ctx.send(
            "Guild is unlocked. You can lock the guild by doing `{}lockdown`\n".format(ctx.prefix)
        )

    @commands.group(name="lockset", aliases=["lockdownset"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)
    async def lockdown_settings(self, ctx):
        """
        Settings for lockdown cog.
        """

    @lockdown_settings.command()
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def showsettings(self, ctx):
        """
        Displays guild's lockdown settings.
        """
        config_info = await self.config.guild(ctx.guild).all()
        channel_list = config_info["channels"]
        lock_message = config_info["lockdown_message"]
        unlock_message = config_info["unlockdown_message"]
        confirmation_message = config_info["confirmation_message"]

        chan = ""
        for channel in channel_list:
            chan += "<#{}> - {}\n".format(channel, channel)

        if not chan:
            embed = discord.Embed(
                color=await ctx.embed_color(),
                title="Lockdown Settings:",
                description="No channels added",
            )
            embed.add_field(
                name="Lock Message:", value=lock_message if lock_message else "None set"
            )
            embed.add_field(
                name="Unlock Message:", value=unlock_message if unlock_message else "None set"
            )
            embed.add_field(
                name="Confirmation:", value="enabled" if confirmation_message else "disabled"
            )
            await ctx.send(embed=embed)
            return

        # Embed information
        embed_list = []
        channel_embed = list(pagify(chan, page_length=1000))
        for idx, page in enumerate(channel_embed, start=1):
            embed = discord.Embed(
                color=await ctx.embed_color(), title="Lockdown Settings:", description=chan,
            )
            embed.add_field(
                name="Lock Message:", value=lock_message if lock_message else "None set"
            )
            embed.add_field(
                name="Unlock Message:", value=unlock_message if unlock_message else "None set"
            )
            embed.add_field(
                name="Confirmation:", value="enabled" if confirmation_message else "disabled"
            )
            embed.set_footer(text="Page {}/{}".format(idx, len(channel_embed)))
            embed_list.append(embed)

        await menus.menu(ctx, embed_list, menus.DEFAULT_CONTROLS)

    @lockdown_settings.command(name="int")
    async def remove_int(self, ctx, number: int):
        """
        Removes int from config if channel was removed.
        """
        if number not in await self.config.guild(ctx.guild).channels():
            return await ctx.send(
                "This number is not in the config. Please double check the number."
            )

        status = "Error"

        async with self.config.guild(ctx.guild).channels() as chan:
            chan.remove(number)
            status = "Removed"

        await ctx.send("Done. New status for {} - {}".format(number, status))

    @lockdown_settings.command(name="guildreset", usage="True")
    @checks.admin_or_permissions(administrator=True)
    async def clear_guild_config(self, ctx, toggle: bool):
        """
        Completely wipes guild's config.

        You must confirm this with a `True` argument. You will then be asked if you are sure. This is for safety.
        """
        if toggle is False:
            await ctx.send("You can't use any boolean except for True. Try again.")
            return await ctx.send_help()

        confirm = await self.confirm_action(
            "Are you sure you want to wipe the guild config? If so, please type `yes`, otherwise type `no`.",
            ctx,
        )
        if confirm is False:
            return

        await self.config.guild(ctx.guild).clear()
        await ctx.send("Done. Wiped guild's config. Thank you come again.")

    @lockdown_settings.command()
    async def channel(
        self,
        ctx,
        channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]] = None,
    ):
        """
        Toggles lockdown status for channels
        """
        if channels is None:
            return await ctx.send_help()
        status = "Error"
        status_list = []

        async with self.config.guild(ctx.guild).channels() as chan:
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

    @lockdown_settings.command(name="lockmessage", aliases=["lockmsg"])
    async def lockdown_message(self, ctx, *, message: str):
        """
        Message the bot sends when lockdown is triggered.

        To disable the message, type `None` or `Clear`.
        """
        if message.lower() == "none" or "clear":  # redo later
            await self.config.guild(ctx.guild).lockdown_message.set(None)
            return await ctx.send("Done. Cleared lockdown message.")

        if len(message) > 1500:
            return await ctx.send(
                "Please limit the amount of characters used. Don't go above 1,500 characters.\n\nYou currently have {}".format(
                    len(message)
                )
            )

        await self.config.guild(ctx.guild).lockdown_message.set(message)
        await ctx.send("Done. The lockdown message is now:\n\n{}".format(box(message)))

    @lockdown_settings.command(name="unlockmessage", aliases=["unlockmsg"])
    async def unlockdown_message(self, ctx, *, message: str):
        """
        Message the bot sends when unlockdown is triggered.

        To disable the message, type `None` or `Clear`.
        """
        if message.lower() == "none" or "clear":  # redo later
            await self.config.guild(ctx.guild).unlockdown_message.set(None)
            return await ctx.send("Done. Cleared unlockdown message.")

        if len(message) > 1500:
            return await ctx.send(
                "Please limit the amount of characters used. Don't go above 1,500 characters.\n\nYou currently have {}".format(
                    len(message)
                )
            )

        await self.config.guild(ctx.guild).unlockdown_message.set(message)
        await ctx.send("Done. The unlockdown message is now:\n\n{}".format(box(message)))

    @lockdown_settings.command(name="confirm")
    async def confirmation_toggle(self, ctx, toggle: bool):
        """
        Make the bot require confirmation message to lockdown.

        Default behavior is false. Type `true` or `false` to change settings
        """
        if toggle is True:
            await self.config.guild(ctx.guild).confirmation_message.set(True)
            await ctx.send("Done. Confirmation is now required.")
        else:
            await self.config.guild(ctx.guild).confirmation_message.set(False)
            await ctx.send("Done. Confirmation is not required anymore.")

    @commands.command(name="channellock")
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)  # gg shark
    async def channel_lockdown(
        self,
        ctx,
        channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]] = None,
    ):
        """
        Lockdown selected channels.
        """
        if channels is None:
            return await ctx.send(
                "Please provide a channel or multiple channels you want to lock."
            )

        if await self.config.guild(ctx.guild).confirmation_message() is True:
            confirm = await self.confirm_action(
                "Are you sure you want to lock those channels? If so, please type `yes`, otherwise type `no`.",
                ctx,
            )
            if confirm is False:
                return

        failed_channels = []
        confirmed_channels = []
        role = ctx.guild.default_role
        for channel in channels:
            overwrite = channel.overwrites_for(role)
            overwrite = self.retrieve_overwrite(channel, overwrite, "lock")
            try:
                await channel.set_permissions(
                    role,
                    overwrite=overwrite,
                    reason="Lockdown in effect. Requested by {} ({})".format(
                        ctx.author.name, ctx.author.id
                    ),
                )
                confirmed_channels.append(channel.mention)
            except discord.Forbidden:
                failed_channels.append("{} - {}".format(channel.mention, channel.id))

        if not confirmed_channels:
            return await ctx.send(
                "Uh oh. None of the channels were able to be locked. Check your permissions!"
            )

        confirmed_message = "Channels locked:\n"
        for chan in confirmed_channels:
            confirmed_message += "{}\n".format(chan)

        await ctx.send(confirmed_message)

        if not failed_channels:
            return

        failed_message = "Channels failed:\n"
        for chan in failed_channels:
            failed_message += "{}\n".format(chan)

        await ctx.send(failed_message)

    @commands.command(name="channelunlock")
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)  # gg shark
    async def channel_unlockdown(
        self,
        ctx,
        channels: commands.Greedy[Union[discord.TextChannel, discord.VoiceChannel]] = None,
    ):
        """
        Unlocks selected channels.
        """
        if channels is None:
            return await ctx.send(
                "Please provide a channel or multiple channels you want to unlock."
            )

        if await self.config.guild(ctx.guild).confirmation_message() is True:
            confirm = await self.confirm_action(
                "Are you sure you want to unlock those channels? If so, please type `yes`, otherwise type `no`.",
                ctx,
            )
            if confirm is False:
                return

        failed_channels = []
        confirmed_channels = []
        role = ctx.guild.default_role
        for channel in channels:
            overwrite = channel.overwrites_for(role)
            overwrite = self.retrieve_overwrite(channel, overwrite, "unlock")
            try:
                await channel.set_permissions(
                    role,
                    overwrite=overwrite,
                    reason="Unlockdown. Requested by {} ({})".format(
                        ctx.author.name, ctx.author.id
                    ),
                )
                confirmed_channels.append(channel.mention)
            except discord.Forbidden:
                failed_channels.append("{} - {}".format(channel.mention, channel.id))

        if not confirmed_channels:
            return await ctx.send(
                "Uh oh. None of the channels were able to be unlocked. Check your permissions!"
            )

        confirmed_message = "Channels unlocked:\n"
        for chan in confirmed_channels:
            confirmed_message += "{}\n".format(chan)

        await ctx.send(confirmed_message)

        if not failed_channels:
            return

        failed_message = "Channels failed:\n"
        for chan in failed_channels:
            failed_message += "{}\n".format(chan)

        await ctx.send(failed_message)
