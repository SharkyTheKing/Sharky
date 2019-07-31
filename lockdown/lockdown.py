import discord
from redbot.core import commands, Config, checks


BaseCog = getattr(commands, "Cog", object)


class Lockdown(BaseCog):
    """
    Locks down the current guild or specific channels

    Make sure you use `[p]lockdownset` to adjust your settings first!
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=8675309)

        def_guilds = {"channels": [], "voices": [], "lockmsg": None, "unlockmsg": None}
        self.config.register_guild(**def_guilds)

    #   Full Lockdown
    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def lockdown(self, ctx, guild: int = None):
        """
        Toggles the lockdown mode

        If you do `[p]lockdown` it'll default to the current guild/server
        If you do `[p]lockdown 133049272517001216` it'll lockdown that specific guild if you have `Manage_Channels` permissions there
        """
        if guild is None:
            role = ctx.guild.default_role
            msg = await self.config.guild(ctx.guild).lockmsg()
            channel_ids = await self.config.guild(ctx.guild).channels()
            voice_ids = await self.config.guild(ctx.guild).voices()
            for guild_channel in ctx.guild.channels:
                if guild_channel.id in channel_ids:
                    overwrite = guild_channel.overwrites_for(role)
                    overwrite.update(send_messages=False)
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown in effect. Requested by {} ({})".format(
                            ctx.author.name, ctx.author.id
                        ),
                    )
                    if msg is None:
                        pass
                    else:
                        await guild_channel.send(msg)
                if guild_channel.id in voice_ids:
                    overwrite = guild_channel.overwrites_for(role)
                    overwrite.update(connect=False)
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown in effect. Requested by {} ({})".format(
                            ctx.author.name, ctx.author.id
                        ),
                    )
        else:
            guild = ctx.bot.get_guild(guild)
            if guild is None:
                return await ctx.send("Server not found. Please double check your ID.")
            author_targeted_guild = guild.get_member(ctx.author.id)
            if author_targeted_guild.guild_permissions.manage_channels is False:
                return await ctx.send(
                    "Yeah...You don't have correct perms in that Discord Server."
                )

            role = guild.default_role
            msg = await self.config.guild(guild).lockmsg()
            channel_ids = await self.config.guild(guild).channels()
            voice_ids = await self.config.guild(guild).voices()
            for guild_channel in guild.channels:
                if guild_channel.id in channel_ids:
                    overwrite = guild_channel.overwrites_for(role)
                    overwrite.update(send_messages=False)
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown in effect. Requested by {} ({})".format(
                            ctx.author, ctx.author.id
                        ),
                    )
                    if msg is None:
                        pass
                    else:
                        await guild_channel.send(msg)
                if guild_channel.id in voice_ids:
                    overwrite = guild_channel.overwrites_for(role)
                    overwrite.update(connect=False)
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown in effect. Requested by {} ({})".format(
                            ctx.author.name, ctx.author.id
                        ),
                    )
        await ctx.send(
            "Server is locked down. You can unlock the server by doing {}unlockdown".format(
                ctx.prefix
            )
        )

    #   Full Unlockdown
    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def unlockdown(self, ctx, guild: int = None):
        """
        Ends the lockdown for this server

        If you do `[p]unlockdown` it'll default to the current guild/server
        If you do `[p]unlockdown 133049272517001216` it'll unlock that specific guild if you have `Manage_Channels` permissions there
        """
        if guild is None:
            role = ctx.guild.default_role
            msg = await self.config.guild(ctx.guild).unlockmsg()
            channel_ids = await self.config.guild(ctx.guild).channels()
            voice_ids = await self.config.guild(ctx.guild).voices()
            for guild_channel in ctx.guild.channels:
                if guild_channel.id in channel_ids:
                    overwrite = guild_channel.overwrites_for(role)
                    overwrite.update(send_messages=None)
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown ended. Requested by {} ({})".format(
                            ctx.author.name, ctx.author.id
                        ),
                    )
                    if msg is None:
                        pass
                    else:
                        await guild_channel.send(msg)
                if guild_channel.id in voice_ids:
                    overwrite = guild_channel.overwrites_for(role)
                    overwrite.update(connect=None)
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown over. Requested by {} ({})".format(
                            ctx.author.name, ctx.author.id
                        ),
                    )
        else:
            guild = ctx.bot.get_guild(guild)
            if guild is None:
                return await ctx.send("Server not found. Please double check your ID.")
            author_targeted_guild = guild.get_member(ctx.author.id)
            if author_targeted_guild.guild_permissions.manage_channels is False:
                return await ctx.send(
                    "Yeah...You don't have correct perms in that Discord Server."
                )

            role = guild.default_role
            msg = await self.config.guild(guild).unlockmsg()
            channel_ids = await self.config.guild(guild).channels()
            voice_ids = await self.config.guild(guild).voices()
            for guild_channel in guild.channels:
                if guild_channel.id in channel_ids:
                    overwrite = guild_channel.overwrites_for(role)
                    overwrite.update(send_messages=None)
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown ended. Requested by {} ({})".format(
                            ctx.author.name, ctx.author.id
                        ),
                    )
                    if msg is None:
                        pass
                    else:
                        await guild_channel.send(msg)
                if guild_channel.id in voice_ids:
                    overwrite = guild_channel.overwrites_for(role)
                    overwrite.update(connect=None)
                    await guild_channel.set_permissions(
                        role,
                        overwrite=overwrite,
                        reason="Lockdown over. Requested by {} ({})".format(
                            ctx.author.name, ctx.author.id
                        ),
                    )
        await ctx.send("Server has been unlocked!")

    #   Lockdownset group
    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_guild=True)
    async def lockdownset(self, ctx):
        """Settings for lockdown"""
        pass

    #   Adding channel to config
    @lockdownset.command(pass_context=True, no_pm=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        """
        Toggles lockdown status for a particular channel

        Doing this will also remove the channel from the list as well
        `Example: [p]lockdownset channel #general`
        """
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

    #   Adding voice channel to config
    @lockdownset.command(pass_context=True, no_pm=True)
    async def voice(self, ctx, channel: discord.VoiceChannel):
        """
        Toggles lockdown status for a particular channel

        Doing this will also remove the channel form the list as well
        `Example: [p]lockdownset voice Gaming` or you can use a channel ID
        """
        guild = ctx.message.guild
        status = "Error"
        if channel.id not in await self.config.guild(guild).voices():
            async with self.config.guild(guild).voices() as voice:
                voice.append(channel.id)
                status = "Added"
        else:
            async with self.config.guild(guild).voices() as voice:
                voice.remove(channel.id)
                status = "Removed"

        await ctx.send("New status for {} set! - {}".format(channel.mention, status))

    #   Setting Lockdown message
    @lockdownset.command(pass_context=True, no_pm=True)
    async def lock(self, ctx, *, text=None):
        """
        The message you want the bot to send when it locks

        `Example: [p]lockdownset lock Server Locked for the time being, sorry for the inconvience!`
        """
        guild = ctx.guild
        if text is None:
            await self.config.guild(guild).lockmsg.set(None)
            await ctx.send("Cleared the text")
        else:
            await self.config.guild(guild).lockmsg.set(text)
            await ctx.send(f"Done! The lock message is now: {text}")

    #   Setting Unlockdown message
    @lockdownset.command(pass_context=True, no_pm=True)
    async def unlock(self, ctx, *, text=None):
        """
        The message you want the bot to send when it unlocks

        `Example: [p]lockdownset unlock Server Unlocked! Thank you for waiting.`
        """
        guild = ctx.guild
        if text is None:
            await self.config.guild(guild).unlockmsg.set(None)
            await ctx.send("Cleared the text")
        else:
            await self.config.guild(guild).unlockmsg.set(text)
            await ctx.send(f"Done! The unlock message is now: {text}")

    #   List of all channels in config
    @lockdownset.command(pass_context=True, no_pm=True)
    async def list(self, ctx):
        """Displays the list of everything in settings"""
        guild = ctx.guild
        get_channel = await self.config.guild(guild).channels()
        get_voice = await self.config.guild(guild).voices()
        get_lock = await self.config.guild(guild).lockmsg()
        get_unlock = await self.config.guild(guild).unlockmsg()
        chan = ""
        voi = ""
        for channel in get_channel:
            chan += f"<#{channel}> - {channel}\n"
        for voice in get_voice:
            voi += f"<#{voice}> - {voice}\n"
        e = discord.Embed(color=await ctx.embed_color())
        e.title = "Current channels:"
        e.add_field(name="Text Channels:", value=chan if chan else "None")
        e.add_field(name="Voice Channels:", value=voi if voi else "None")
        e.add_field(name="Lock Message:", value=get_lock, inline=False)
        e.add_field(name="Unlock Message:", value=get_unlock, inline=False)
        await ctx.send(embed=e)

    #   Locking Text Channel
    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def locktext(self, ctx, text: discord.TextChannel):
        """
        Locking down selected text channel

        `Example: [p]locktext #general`
        """
        role = ctx.guild.default_role
        guild_channel = text
        overwrite = guild_channel.overwrites_for(role)
        overwrite.update(send_messages=False)
        await guild_channel.set_permissions(
            role,
            overwrite=overwrite,
            reason="Lockdown in effect. Requested by {} ({})".format(
                ctx.author.name, ctx.author.id
            ),
        )
        await ctx.send("Locked {}".format(text.mention))

    #   Unlocking Text Channel
    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def unlocktext(self, ctx, text: discord.TextChannel):
        """
        Unlocks selected text channel

        `Example: [p]unlocktext #general`
        """
        role = ctx.guild.default_role
        guild_channel = text
        overwrite = guild_channel.overwrites_for(role)
        overwrite.update(send_messages=None)
        await guild_channel.set_permissions(
            role,
            overwrite=overwrite,
            reason="Lockdown over. Requested by {} ({})".format(ctx.author.name, ctx.author.id),
        )
        await ctx.send("Unlocked {}".format(text.mention))

    #   Locking Voice Channel
    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def lockvoice(self, ctx, *, voice: discord.VoiceChannel):
        """
        Locking down selected voice channel

        `Example: [p]lockvoice Gaming Voice Call` or you can use a channel ID
        """
        role = ctx.guild.default_role
        guild_channel = voice
        overwrite = guild_channel.overwrites_for(role)
        overwrite.update(connect=False)
        await guild_channel.set_permissions(
            role,
            overwrite=overwrite,
            reason="Lockdown in effect. Requested by {} ({})".format(
                ctx.author.name, ctx.author.id
            ),
        )
        await ctx.send("Locked {}".format(voice.mention))

    #   Unlocking Voice Channel
    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def unlockvoice(self, ctx, *, voice: discord.VoiceChannel):
        """
        Unlocking down selected voice channel

        `Example: [p]unlockvoice Gaming Voice Call` or you can use a channel ID
        """
        role = ctx.guild.default_role
        guild_channel = voice
        overwrite = guild_channel.overwrites_for(role)
        overwrite.update(connect=None)
        await guild_channel.set_permissions(
            role,
            overwrite=overwrite,
            reason="Lockdown over. Requested by {} ({})".format(ctx.author.name, ctx.author.id),
        )
        await ctx.send("Unlocked {}".format(voice.mention))
