import datetime

import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate

from typing import Union

BaseCog = getattr(commands, "Cog", object)


class Lockdown(BaseCog):
    """Locks down the current server"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=8675309)
        self.locked_channels = {"Channels": {}}

        def_guilds = {"channels": [], "lockmsg": None, "unlockmsg": None}
        self.config.register_guild(**def_guilds)

    async def yes_or_no(self, ctx, message) -> bool:
        msg = await ctx.send(message)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)

        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        await ctx.bot.wait_for("reaction_add", check=pred)
        await msg.delete()
        return pred.result

    #   Full Lockdown
    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def lockdown(self, ctx, guild: int = None):
        """
        Toggles the lockdown mode
        """
        if guild is not None:
            guild = ctx.bot.get_guild(guild)
            if guild is None:
                return await ctx.send("Server not found. Please double check your ID.")
            author_targeted_guild = guild.get_member(ctx.author.id)
            if author_targeted_guild.guild_permissions.manage_channels is False:
                return
        else:
            guild = ctx.guild

        really_lockdown = await self.yes_or_no(
            ctx, f"🔐 Are you sure you want to lockdown the server?\n**Yes or no?**"
        )
        if not really_lockdown:
            return await ctx.send("🍪 Phew. That was a close one. Server is **not** locked.")

        role = guild.default_role
        msg = await self.config.guild(guild).lockmsg()
        channel_ids = await self.config.guild(guild).channels()

        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                overwrite = guild_channel.overwrites_for(role)
                overwrite.update(send_messages=False)
                author = ctx.author
                try:
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason=f"Lockdown in effect. Requested by {author.name} ({author.id})",
                    )
                except discord.Forbidden:
                    pass
                try:
                    self.locked_channels["Channels"].add(guild_channel.id)
                except AttributeError:
                    self.locked_channels.update({"Channels": {guild_channel.id}})
                if msg:
                    try:
                        await guild_channel.send(msg)
                    except discord.Forbidden:
                        pass

        await ctx.send(
            f"Server is locked down. You can unlock the server by doing `{ctx.prefix}unlockdown`"
        )

    #   Full Unlockdown
    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def unlockdown(self, ctx, guild: int = None):
        """Ends the lockdown for this server"""
        if guild is None:
            guild = ctx.guild
        else:
            guild = ctx.bot.get_guild(guild)
            if guild is None:
                return await ctx.send("Server not found. Please double check your ID.")
            author_targeted_guild = guild.get_member(ctx.author.id)
            if author_targeted_guild.guild_permissions.manage_channels is False:
                return
        confirm_unlockdown = await self.yes_or_no(
            ctx, f"🔐 Are you sure you want to unlock the server?\n**Yes or no?**"
        )
        if not confirm_unlockdown:
            return await ctx.send("🍪 Phew. The server is still locked.")

        role = guild.default_role
        msg = await self.config.guild(guild).unlockmsg()
        channel_ids = await self.config.guild(guild).channels()
        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                overwrite = guild_channel.overwrites_for(role)
                overwrite.update(send_messages=None)
                author = ctx.author
                try:
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason=f"Lockdown ended. Requested by {author.name} ({author.id})",
                    )
                except discord.Forbidden:
                    pass
                try:
                    self.locked_channels["Channels"].remove(guild_channel.id)
                except AttributeError:
                    pass
                if msg:
                    try:
                        await guild_channel.send(msg)
                    except discord.Forbidden:
                        pass

        await ctx.send(f"Server is now unlocked.")

    #   Lockdownset group
    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_guild=True)
    async def lockdownset(self, ctx):
        """Settings for lockdown"""
        pass

    #   Adding channel to config
    @lockdownset.command(pass_context=True, no_pm=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        """Toggles lockdown status for a particular channel"""
        guild = ctx.message.guild
        status = "Error"
        if channel.id not in await self.config.guild(guild).channels():
            async with self.config.guild(guild).channels() as chan:
                chan.append(channel.id)
                status = "Added"
        else:
            async with self.config.guild(guild).channels() as chan:
                chan.remove(channel.id)
                status = "Removed"

        await ctx.send("New status for {} set! - {}".format(channel.mention, status))

    #   Setting Lockdown message
    @lockdownset.command(pass_context=True, no_pm=True)
    async def lockmsg(self, ctx, *, text=None):
        """What lockdown message you want to put"""
        guild = ctx.guild
        if text is None:
            await self.config.guild(guild).lockmsg.set(None)
            response = "Cleared the text"
        else:
            await self.config.guild(guild).lockmsg.set(text)
            response = f"Done! The lock message is now: {text}"

        await ctx.send(response)

    #   Setting Unlockdown message
    @lockdownset.command(pass_context=True, no_pm=True)
    async def unlockmsg(self, ctx, *, text=None):
        """What unlockdown message you want to put"""
        guild = ctx.guild
        if text is None:
            await self.config.guild(guild).unlockmsg.set(None)
            response = "Cleared the text"
        else:
            await self.config.guild(guild).unlockmsg.set(text)
            response = f"Done! The unlock message is now: {text}"

        await ctx.send(response)

    #   List of all channels in config
    @lockdownset.command(pass_context=True, no_pm=True)
    async def list(self, ctx):
        """Lists what channel is under the settings"""
        guild = ctx.guild
        get_channel = await self.config.guild(guild).channels()
        get_lock = await self.config.guild(guild).lockmsg()
        get_unlock = await self.config.guild(guild).unlockmsg()
        chan = ""
        for channel in get_channel:
            chan += f"<#{channel}> - {channel}\n"

        e = discord.Embed(
            color=await ctx.embed_color(), title="Current channels:", description=chan
        )

        e.add_field(name="Lock Message:", value=get_lock, inline=False)

        e.add_field(name="Unlock Message:", value=get_unlock, inline=False)

        await ctx.send(embed=e)

    #   Locking Text Channel
    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def channellock(self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel]):
        """Locking down selected text/voice channel"""

        should_lock = await self.yes_or_no(
            ctx, f"🔐 Do you want to lockdown {channel.mention}\n**Yes or no?**"
        )
        if not should_lock:
            return await ctx.send(f"🚀 Okay. {channel.mention} is **not** locked.")

        role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        #   Checking channel type
        if channel in ctx.guild.text_channels:
            if overwrite.send_messages is False:
                return await ctx.send(
                    f"{channel.mention} is already locked. To unlock, please use `{ctx.prefix}channelunlock {channel.id}`"
                )
            overwrite.update(send_messages=False)
        elif channel in ctx.guild.voice_channels:
            if overwrite.connect is False:
                return await ctx.send(
                    f"{channel.mention} is already locked. To unlock, please use `{ctx.prefix}channelunlock {channel.id}`"
                )
            overwrite.update(connect=False)
        try:
            await channel.set_permissions(
                role,
                overwrite=overwrite,
                reason="Lockdown in effect. Requested by {} ({})".format(
                    ctx.author.name, ctx.author.id
                ),
            )
        except discord.Forbidden:
            return await ctx.send("Error: Bot doesn't have perms to adjust that channel.")
        try:
            self.locked_channels["Channels"].add(channel.id)
        except AttributeError:
            self.locked_channels.update({"Channels": {channel.id}})
        await ctx.send("🔐 Locked {}".format(channel.mention))

    #   Unlocking Text Channel
    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def channelunlock(self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel]):
        """Unlocking down selected text/voice channel"""

        should_unlock = await self.yes_or_no(
            ctx, f"🔓 Do you want to unlock {channel.mention}\n**Yes or no?**"
        )
        if not should_unlock:
            return await ctx.send(f"🚀 Okay. {channel.mention} is **not** unlocked.")

        role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        #   Checking channel type
        if channel in ctx.guild.text_channels:
            if overwrite.send_messages is None:
                return await ctx.send(
                    f"{channel.mention} is already unlocked. To lock, please use `{ctx.prefix}lock {channel.id}`"
                )
            overwrite.update(send_messages=None)
        elif channel in ctx.guild.voice_channels:
            if overwrite.connect is None:
                return await ctx.send(
                    f"{channel.mention} is already unlocked. To lock, please use `{ctx.prefix}lock {channel.id}`"
                )
            overwrite.update(connect=None)

        author = ctx.author
        try:
            await channel.set_permissions(
                role,
                overwrite=overwrite,
                reason=f"Lockdown over. Requested by {author.name} ({author.id})",
            )
        except discord.Forbidden:
            return await ctx.send("Error: Bot doesn't have perms to adjust that channel.")
        try:
            self.locked_channels["Channels"].remove(channel.id)
        except AttributeError:
            pass
        await ctx.send(f"🔓 Unlocked {channel.mention}")

    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def viewlock(self, ctx):
        """
        Views what channels are locked

        It will only register channels that are in `[p]lockdownset list`!
        """
        guild = ctx.guild
        role = ctx.guild.default_role
        channel_lists = []
        channel_ids = await self.config.guild(guild).channels()
        for guild_channel in guild.channels:
            if guild_channel.id in channel_ids:
                overwrite = guild_channel.overwrites_for(role)
                if overwrite.send_messages is False:
                    channel_lists.append(guild_channel.id)
        channel_preview = ""
        if channel_lists:
            for channel in channel_lists:
                channel_preview += f"<#{channel}> is locked.\n"
        embed = discord.Embed(color=discord.Color.gold())
        embed.title = "Currently Locked Channels"
        embed.description = channel_preview if channel_lists else "No channels added"
        await ctx.send(embed=embed)

    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def testinglock(self, ctx):
        info = self.locked_channels
        guild = ctx.guild
        role = guild.default_role
        channel_lists = []
        if len(info["Channels"]) > 0:
            for guild_channel in guild.channels:
                if guild_channel.id in info["Channels"]:
                    overwrite = guild_channel.overwrites_for(role)
                    if overwrite.send_messages is False:
                        channel_lists.append(guild_channel.id)
            channel_preview = ""
            if channel_lists:
                for channel in channel_lists:
                    channel_preview += f"<#{channel}> is locked.\n"
            embed = discord.Embed(color=discord.Color.gold())
            embed.title = "Currently Locked Channels"
            embed.description = channel_preview if channel_lists else "No channels added"
            await ctx.send(embed=embed)
        else:
            await ctx.send("There is nothing in the dictionary.")
