from redbot.core import commands, checks, Config
from typing import Optional, Union
import logging
import discord
import asyncio

DEF_GUILD = {"channels": [], "lockdown_message": None, "unlockdown_message": None}

BaseCog = getattr(commands, "Cog", object)


class Lockdown(BaseCog):
    """
    Lockdown the entire server / other servers you're mod of
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=548498634843)

        self.config.register_guild(**DEF_GUILD)
        self.log = logging.getLogger("red.cogs.lockdown")

    @commands.command()
    @checks.mod_or_permissions(manage_channels=True)
    async def lockdown(self, ctx, guild: Optional[discord.Guild]):
        """
        Lockdown a server

        Guild is optional, if none is given it'll default to current.
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        guild = guild if guild else ctx.guild
        author_targeted_guild = guild.get_member(ctx.author.id)
        if author_targeted_guild.guild_permissions.manage_channels is False:
            return await ctx.send("You don't have `manage_channels` permissions in this guild.")

        await ctx.send(
            "Are you sure you want to lockdown the guild? If so, please type `yes`, otherwise type `no`."
        )
        try:
            confirm_lockdown = await ctx.bot.wait_for("message", check=check, timeout=30)
            if confirm_lockdown.content.lower() != "yes":
                return await ctx.send("Okay. Won't lockdown the guild.")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply!")

        author = ctx.author
        role = guild.default_role
        message = await self.config.guild(guild).lockdown_message()
        channel_ids = await self.config.guild(guild).channels()

        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                overwrite = guild_channel.overwrites_for(role)
                overwrite.update(send_messages=False)
                try:
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown in effect. Requested by {} ({})".format(
                            author.name, author.id
                        ),
                    )
                except discord.Forbidden:
                    self.log.info("Could not lockdown {}".format(guild_channel.name))
                if message:
                    try:
                        await guild_channel.send(message)
                    except discord.Forbidden:
                        self.log.info("Could not send message to {}".format(guild_channel.name))

        await ctx.send(
            "Guild is locked down. You can unlock the guild by doing `{}unlockdown`".format(
                ctx.prefix
            )
        )

    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def unlockdown(self, ctx, guild: Optional[discord.Guild]):
        """
        Ends the lockdown for the guild
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        guild = guild if guild else ctx.guild

        author_targeted_guild = guild.get_member(ctx.author.id)
        if author_targeted_guild.guild_permissions.manage_channels is False:
            return await ctx.send("You don't have manage_channels in this server.")

        await ctx.send(
            "Are you sure you want to unlock the guild? If so, please type `yes`, otherwise type `no`."
        )
        try:
            confirm_unlockdown = await ctx.bot.wait_for("message", check=check, timeout=30)
            if confirm_unlockdown.content.lower() != "yes":
                return await ctx.send("Okay. Won't unlock the guild.")
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply!")

        author = ctx.author
        role = guild.default_role
        message = await self.config.guild(guild).unlockdown_message()
        channel_ids = await self.config.guild(guild).channels()
        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                overwrite = guild_channel.overwrite_for(role)
                overwrite.update(send_messages=None)
                try:
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown ended. Requested by {} ({})".format(
                            author.name, author.id
                        ),
                    )
                except discord.Forbidden:
                    self.log.info("Couldn't unlock {}".format(guild_channel.mention))
                if message:
                    try:
                        await guild_channel.send(message)
                    except discord.Forbidden:
                        self.log.info("Could not send message to {}".format(guild_channel.name))

        await ctx.send("Guild is now unlocked.")

    @commands.group()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def lockdownset(self, ctx):
        """
        Settings for lockdown
        """
        if ctx.invoked_subcommand is None:
            guild = ctx.guild
            get_channel = await self.config.guild(guild).channels()
            get_lock = await self.config.guild(guild).lockmsg()
            get_unlock = await self.config.guild(guild).unlockmsg()
            chan = ""
            for channel in get_channel:
                chan += "<#{}> - {}\n".format(channel, channel)

            embed = discord.Embed(
                color=await ctx.embed_color(), title="Current channels:", description=chan
            )

            embed.add_field(name="Lock Message:", value=get_lock, inline=False)

            embed.add_field(name="Unlock Message:", value=get_unlock, inline=False)

            await ctx.send(embed=embed)

    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def channellock(self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel]):
        """Locking down selected text/voice channel"""

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("Do you want to lockdown {}\n**Yes or No?**".format(channel.mention))
        should_lock = await ctx.bot.wait_for("message", check=check, timeout=30)
        try:
            should_lock = await ctx.bot.wait_for("message", check=check, timeout=30)
            if should_lock.content.lower() != "yes":
                return await ctx.send("Okay. Won't lock {}.".format(channel.mention))
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply!")

        author = ctx.author
        role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        #   Checking channel type
        if channel.type == discord.ChannelType.text:
            if overwrite.send_messages is False:
                return await ctx.send(
                    "{} is already locked. To unlock, please use `{}channelunlock {}`".format(
                        channel.mention, ctx.prefix, channel.id
                    )
                )
            overwrite.update(send_messages=False)
        elif channel.type == discord.ChannelType.voice:
            if overwrite.connect is False:
                return await ctx.send(
                    "{} is already locked. To unlock, please use `{}channelunlock {}`".format(
                        channel.mention, ctx.prefix, channel.id
                    )
                )
            overwrite.update(connect=False)
        try:
            await channel.set_permissions(
                role,
                overwrite=overwrite,
                reason="Lockdown in effect. Requested by {} ({})".format(
                    author.name, author.id
                ),
            )
        except discord.Forbidden:
            return await ctx.send("Error: Bot doesn't have perms to adjust that channel.")
        await ctx.send("Done. Locked {}".format(channel.mention))

    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def channelunlock(self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel]):
        """Unlocking down selected text/voice channel"""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("Do you want to unlock {}\n**Yes or No?**".format(channel.mention))
        should_unlock = await ctx.bot.wait_for("message", check=check, timeout=30)
        try:
            should_unlock = await ctx.bot.wait_for("message", check=check, timeout=30)
            if should_unlock.content.lower() != "yes":
                return await ctx.send("Okay. Won't unlock {}.".format(channel.mention))
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to reply!")

        author = ctx.author
        role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        #   Checking channel type
        if channel.type == discord.ChannelType.text:
            if overwrite.send_messages is None:
                return await ctx.send(
                    "{} is already unlocked. To lock, please use `{}channellock {}`".format(
                        channel.mention, ctx.prefix, channel.id
                    )
                )
            overwrite.update(send_messages=None)
        elif channel.type == discord.ChannelType.voice:
            if overwrite.connect is None:
                return await ctx.send(
                    "{} is already unlocked. To lock, please use `{}channellock {}`".format(
                        channel.mention, ctx.prefix, channel.id
                    )
                )
            overwrite.update(connect=None)

        try:
            await channel.set_permissions(
                role,
                overwrite=overwrite,
                reason="Lockdown over. Requested by {} ({})".format(author.name, author.id),
            )
        except discord.Forbidden:
            return await ctx.send("Error: Bot doesn't have perms to adjust that channel.")
        await ctx.send("Unlocked {}".format(channel.mention))
