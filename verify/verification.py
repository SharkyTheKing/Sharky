import discord
from redbot.core import commands, checks, Config
from typing import Optional

BaseCog = getattr(commands, "Cog", object)


class Verify(BaseCog):
    """
    Verification process for members

    Setting up a verification process so members have to verify they read or accept the rules
    """

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=123532432623423)

        def_guild = {"toggle": False, "role": None, "logs": None}
        self.config.register_guild(**def_guild)

    # TODO Secondly, setup list command to show what role, what channel is active, if the server is set to active

    #   Set group
    @commands.bot_has_permissions(
        manage_messages=True, send_messages=True, manage_roles=True, embed_links=True
    )
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.group()
    async def verifyset(self, ctx):
        """
        Manages the settings for the guild

        Please use `[p]verifyset list` to see the current settings
        """
        pass

    @verifyset.command()
    async def active(self, ctx, toggle: Optional[bool]):
        """
        Activates or Deactivates the verification process

        Default is `False`, to activate type `[p]verifyset activate True`
        """
        guild = ctx.guild
        tog = self.config.guild(guild)
        if toggle is None:
            if await tog.toggle() is False:
                await ctx.send("The Verification settings is set to False")
            elif await tog.toggle() is True:
                await ctx.send("The Verification settings is set to True")
        elif toggle is True:
            await tog.toggle.set(True)
            await ctx.send("Verification settings is now set to True")
        elif toggle is False:
            await tog.toggle.set(False)
            await ctx.send("Verification settings is now set to False")

    @verifyset.command()
    async def log(self, ctx, *, channel: Optional[discord.TextChannel]):
        """
        Sets the channel you wish to log to

        This will log whenever someone accepts the verification
        """
        guild = ctx.guild
        log = self.config.guild(guild)
        if channel is None:
            await log.logs.clear()
            await ctx.send("The bot will no longer log actions done.")
        else:
            await log.logs.set(channel.id)
            await ctx.send(f"Logging channel is now set to {channel.mention}")

    @verifyset.command()
    async def role(self, ctx, *, role: Optional[discord.Role]):
        """
        Sets what role is placed on users when they join the guild

        Please make sure you setup the role correctly in so they can only access your rules and/or verification channel
        """
        guild = ctx.guild
        ro = self.config.guild(guild)
        if role is None:
            await ro.role.set(None)
            await ctx.send("Cleared the role being used")
        else:
            await ro.role.set(role.id)
            await ctx.send(f"Set the role to {role.mention}")

    @verifyset.command()
    async def list(self, ctx):
        """
        Shows the entire settings
        """
        guild = ctx.guild
        color = await ctx.embed_color()
        ro = await self.config.guild(guild).role()
        logs = await self.config.guild(guild).logs()
        toggle = await self.config.guild(guild).toggle()
        ro_info = ""
        log_info = ""
        if ro is None:
            ro_info = "There is no role set yet"
        else:
            ro_info = discord.utils.get(ctx.guild.roles, id=int(ro))
        if logs is None:
            log_info = "No channel has been set yet"
        else:
            log_info = discord.utils.get(ctx.guild.text_channels, id=int(logs))
        embed = discord.Embed(color=color)
        embed.title = f"{guild.name}'s Settings"
        embed.description = "Please make sure you setup the Verification Channel and Selected Role.\nOnce that's done, make sure to set the Active to True or else this won't work"
        embed.add_field(name="Active:", value=toggle, inline=False)
        embed.add_field(name="Selected Role:", value=ro_info, inline=True)
        embed.add_field(name="Logging Channel:", value=log_info, inline=True)
        await ctx.send(embed=embed)

    #   Accept command
    @commands.command()
    @commands.bot_has_permissions(
        manage_messages=True, send_messages=True, manage_roles=True, embed_links=True
    )
    @commands.guild_only()
    async def accept(self, ctx):
        """
        Accepting this means you understand the rules of the server
        """
        color = await ctx.embed_color()
        bot = ctx.bot
        guild = ctx.guild
        author = ctx.author
        joined_at = author.joined_at
        member_joined = author.joined_at.strftime("%d %b %Y %H:%M")
        since_joined = (ctx.message.created_at - joined_at).days
        member_created = author.created_at.strftime("%d %b %Y %H:%M")
        since_created = (ctx.message.created_at - author.created_at).days
        created_on = ("{}\n({} days ago)").format(member_created, since_created)
        joined_on = ("{}\n({} days ago)").format(member_joined, since_joined)
        author_avatar = author.avatar_url_as(static_format="png")
        log = await self.config.guild(guild).logs()
        ro = await self.config.guild(ctx.guild).role()
        role = guild.get_role(ro)
        if role is None:
            pass
        else:
            if author not in role.members:
                pass
            else:
                await author.remove_roles(role, reason="Member has verified themselves")
                await ctx.message.delete()
                if log is not None:
                    embed = discord.Embed(color=color)
                    embed.title = f"{author.name}#{author.discriminator} - Verified"
                    embed.set_thumbnail(url=author_avatar)
                    embed.set_footer(text=f"User ID: {author.id}")
                    embed.add_field(name="Account Creation:", value=f"{created_on}", inline=True)
                    embed.add_field(name="Joined Date:", value=f"{joined_on}", inline=True)
                    await bot.get_channel(log).send(embed=embed)
                else:
                    pass

    #   On Join
    @commands.Cog.listener()
    async def on_member_join(self, member):
        toggle = await self.config.guild(member.guild).toggle()
        ro = await self.config.guild(member.guild).role()
        if toggle is True:
            if ro is not None:
                role = discord.utils.get(member.guild.roles, id=int(ro))
                await member.add_roles(role, reason="New Member, Needs to Verify")
            else:
                pass
        elif toggle is False:
            pass
