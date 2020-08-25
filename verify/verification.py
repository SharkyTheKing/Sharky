import logging
from typing import Optional

import discord
from redbot.core import Config, checks, commands

BASECOG = getattr(commands, "Cog", object)


class Verify(BASECOG):
    """
    Verification process for members

    Setting up a verification process so members have to verify they read or accept the rules
    """

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("red.cogs.verify")
        self.config = Config.get_conf(self, identifier=123532432623423)

        def_guild = {"toggle": False, "role": None, "logs": None}
        self.config.register_guild(**def_guild)

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    @commands.bot_has_permissions(
        manage_messages=True, send_messages=True, manage_roles=True, embed_links=True
    )
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.group()
    async def verifyset(self, ctx):
        """
        Manages the settings for the guild
        """
        if ctx.invoked_subcommand is None:
            guild = ctx.guild
            color = await ctx.embed_color()
            role_config = await self.config.guild(guild).role()
            logs = await self.config.guild(guild).logs()
            toggle = await self.config.guild(guild).toggle()
            if role_config is None:
                role_info = "There is no role set yet"
            else:
                role_info = discord.utils.get(ctx.guild.roles, id=int(role_config))

            if logs is None:
                log_info = "No channel has been set yet"
            else:
                log_info = discord.utils.get(ctx.guild.text_channels, id=int(logs))

            embed = discord.Embed(color=color)
            embed.title = "{}'s Settings".format(guild.name)
            embed.description = "Please make sure you setup the Verification Channel and Selected Role.\nOnce that's done, make sure to set the Active to True or else this won't work"
            embed.add_field(name="Active:", value=toggle, inline=False)
            embed.add_field(name="Selected Role:", value=role_info, inline=True)
            embed.add_field(name="Logging Channel:", value=log_info, inline=True)
            await ctx.send(embed=embed)

    @verifyset.command()
    async def active(self, ctx, toggle: Optional[bool]):
        """
        Activates or Deactivates the verification process

        Default is `False`, to activate type `[p]verifyset activate True`
        """
        guild = ctx.guild
        tog = self.config.guild(guild)
        if toggle is None:
            return await ctx.send(
                "The Verification settings is set to {}".format(await tog.toggle())
            )

        if toggle is True:
            await tog.toggle.set(True)
            return await ctx.send("Verification settings is now set to True")
        elif toggle is False:
            await tog.toggle.set(False)
            return await ctx.send("Verification settings is now set to False")

    @verifyset.command()
    async def log(self, ctx, *, channel: Optional[discord.TextChannel]):
        """
        Sets the channel you wish to log to

        This will log whenever someone accepts the verification
        """
        guild = ctx.guild
        log_config = self.config.guild(guild)
        if channel is None:
            await log_config.logs.clear()
            return await ctx.send("The bot will no longer log actions done.")

        await log_config.logs.set(channel.id)
        await ctx.send("Logging channel is now set to {}".format(channel.mention))

    @verifyset.command()
    async def role(self, ctx, *, role: Optional[discord.Role]):
        """
        Sets what role is placed on users when they join the guild

        Please make sure you setup the role correctly in so they can only access your rules and/or verification channel
        """
        guild = ctx.guild
        role_config = self.config.guild(guild)
        if role is None:
            await role_config.role.set(None)
            return await ctx.send("Cleared the role being used")

        await role_config.role.set(role.id)
        await ctx.send("Set the role to {}".format(role.mention))

    @commands.command(name="agree")
    @commands.bot_has_permissions(manage_roles=True)
    async def verify_agree(self, ctx):
        """
        Agreeing to this means you understand the rules of the server
        """
        author = ctx.author
        joined_at = author.joined_at
        member_joined, since_joined = (
            author.joined_at.strftime("%d %b %Y %H:%M"),
            (ctx.message.created_at - joined_at).days,
        )
        member_created, since_created = (
            author.created_at.strftime("%d %b %Y %H:%M"),
            (ctx.message.created_at - author.created_at).days,
        )
        created_on = ("{}\n({} days ago)").format(member_created, since_created)
        joined_on = ("{}\n({} days ago)").format(member_joined, since_joined)
        author_avatar = author.avatar_url_as(static_format="png")

        log_config = await self.config.guild(ctx.guild).logs()
        role_config = await self.config.guild(ctx.guild).role()
        if role_config is None:
            return await ctx.send(
                "Sorry, there is no role set. Please contact the moderation team of this server."
            )
            self.log.warning("No role set. Unable to process verification.")

        role = ctx.guild.get_role(role_config)
        if author not in role.members:
            return

        try:
            await author.remove_roles(role, reason="Member has verified themselves")
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send(
                "Error: I am unable to remove your role, please contact the moderation team."
            )
            return self.log.warning("Error: No permissions to remove roles.")
        except discord.HTTPException as e:
            return self.log.warning("HTTPException: {} - {}".format(e.status, e.code))
        if log_config is None:
            return

        embed = discord.Embed(color=discord.Color.green())
        embed.title = "{}#{} - Verified".format(author.name, author.discriminator)
        embed.set_thumbnail(url=author_avatar)
        embed.set_footer(text="User ID: {}".format(author.id))
        embed.add_field(name="Account Creation:", value=created_on, inline=True)
        embed.add_field(name="Joined Date:", value=joined_on, inline=True)
        try:
            await ctx.bot.get_channel(log_config).send(embed=embed)
        except discord.Forbidden:
            return self.log.warning(
                "Error: Unable to send log message to {}".format(ctx.bot.get_channel(log_config))
            )
        except discord.HTTPException as e:
            return self.log.warning("HTTPException: {} - {}".format(e.status, e.code))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if await self.bot.cog_disabled_in_guild(self, member.guild):
            return False

        toggle = await self.config.guild(member.guild).toggle()
        role_config = await self.config.guild(member.guild).role()
        if toggle is False:
            return False

        if role_config is not None:
            role = discord.utils.get(member.guild.roles, id=int(role_config))
            try:
                await member.add_roles(role, reason="New Member, Needs to Verify")
            except discord.Forbidden:
                return self.log.warning("Unable to grant roles to new joiner.")
            except discord.HTTPException as e:
                return self.log.warning("HTTPException: {} - {}".format(e.status, e.code))
