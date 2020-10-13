import logging

import discord
from redbot.core import Config, checks, commands
from redbot.core.utils import AsyncIter
from redbot.core.utils.chat_formatting import humanize_list, pagify


class Verify(commands.Cog):
    """
    Verification process for members

    Setting up a verification process so members have to verify they read or accept the rules
    """

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.log = logging.getLogger("red.cogs.verify")
        self.config = Config.get_conf(self, identifier=123532432623423)
        def_guild = {"toggle": False, "temprole": None, "logs": None, "autoroles": []}
        self.config.register_guild(**def_guild)

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    # Settings command, and output the settings.

    @commands.bot_has_permissions(
        manage_messages=True, send_messages=True, manage_roles=True, embed_links=True
    )
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.group()
    async def verifyset(self, ctx: commands.Context):
        """
        Manages the settings for the guild.
        """
        if ctx.invoked_subcommand is None:
            guild = ctx.guild
            data = await self.config.guild(guild).all()
            color = await ctx.embed_color()
            role_config = data["temprole"], data["autoroles"]
            logs, toggle = data["logs"], data["toggle"]
            temprole = "No temporary role set, use `[p]verifyset temprole` to use one."
            autoroles = "See `{prefix}verifyset autorole list` for a list of roles given.".format(
                prefix=ctx.prefix
            )
            if role_config[0]:
                temprole = discord.utils.get(ctx.guild.roles, id=role_config[0])

            if logs is None:
                log_info = (
                    "No channel for logging has been set, use `{prefix}verifyset log`"
                    "first.".format(prefix=ctx.prefix)
                )
            else:
                log_info = discord.utils.get(ctx.guild.text_channels, id=int(logs))

            embed = discord.Embed(color=color)
            embed.title = "{}'s Settings".format(guild.name)
            embed.description = (
                "Please make sure you setup the Verification Channel and Selected Role.\nOnce "
                "that's done, make sure to set the Active to True or else this won't work."
            )
            embed.add_field(name="Active:", value=toggle, inline=False)
            embed.add_field(name="Temporary Role:", value=temprole, inline=True)
            embed.add_field(name="Role to give after verification:", value=autoroles, inline=True)
            embed.add_field(name="Logging Channel:", value=log_info, inline=True)
            await ctx.send(embed=embed)

    # If verification must be activated.

    @verifyset.command()
    async def active(self, ctx: commands.Context, toggle: bool = None):
        """
        Activates or Deactivates the verification process.

        Default is `False`, to activate type `[p]verifyset activate True`.
        """
        guild = ctx.guild
        tog = self.config.guild(guild)
        role_config = [
            await tog.temprole(),
            await tog.autoroles(),
        ]
        if not role_config[1]:
            role_config[1] = None
        if toggle is None:
            message = "The Verification settings is set to {}.".format(await tog.toggle())
            if role_config.count(None) == 2 and await tog.toggle():
                await tog.toggle.set(False)
                message = (
                    "I have disabled verification since roles instructions has been "
                    "removed. Check settings for more informations"
                )
            return await ctx.send(message)

        if role_config.count(None) == 2:
            return await ctx.send(
                "I am missing informations; I don't know if I should either give a temprorary "
                "role while verifying or give a role after the verification."
            )
        await tog.toggle.set(toggle)
        await ctx.send("Verification settings is now set to {choice}.".format(choice=toggle))

    # Channel used for logs.

    @verifyset.command()
    async def log(self, ctx: commands.Context, *, channel: discord.TextChannel = None):
        """
        Sets the channel you wish to log to.

        This will log whenever someone accepts the verification.
        """
        guild = ctx.guild
        log_config = self.config.guild(guild)
        if channel is None:
            await log_config.logs.clear()
            return await ctx.send("The bot will no longer log actions done.")

        await log_config.logs.set(channel.id)
        await ctx.send("Logging channel is now set to {}.".format(channel.mention))

    # Temporary role, which is given after joining and removed after verification.

    @verifyset.command()
    async def temprole(self, ctx: commands.Context, *, role: discord.Role = None):
        """
        Sets what role is placed on users when they join the guild.

        Please make sure you setup the role correctly in so they can only access your rules and/or
        verification channel.
        """
        guild = ctx.guild
        role_config = self.config.guild(guild)
        role_set = await role_config.temprole()
        if role is None and role_set:
            await role_config.temprole.clear()
            return await ctx.send("Cleared the role being used.")
        if role:
            if role >= ctx.author.top_role:
                return await ctx.send("You can't set a role equal to or higher than your own.")

            if role >= ctx.guild.me.top_role:
                return await ctx.send(
                    "You can't set a role that's equal to or higher than the bot."
                )
            await role_config.temprole.set(role.id)
            await ctx.send(
                "Set the role to {}.".format(role.mention),
                allowed_mentions=discord.AllowedMentions(roles=False),
            )
        else:
            await ctx.send_help()

    # Autorole commands

    @verifyset.group()
    async def autorole(self, ctx: commands.Context):
        """
        Define roles to give when an user pass the verification.
        """

    @autorole.command(name="add")
    async def add_roles(self, ctx: commands.Context, *roles: discord.Role):
        """Add a role to give.

        You can give more than one role to add.
        """
        if not roles:
            return await ctx.send_help()
        errored = ""
        message = ""
        added = []
        already_added = []
        for role in roles:
            if role >= ctx.author.top_role:
                errored += "{role}: You can't set a role equal to or higher than your own.\n".format(
                    role=role.name
                )
                continue
            if role >= ctx.guild.me.top_role:
                errored += (
                    "{role}: You can't set a role that's equal to or higher than the "
                    "bot.\n".format(role=role.name)
                )
                continue
            async with self.config.guild(ctx.guild).autoroles() as roles_list:
                if role.id not in roles_list:
                    roles_list.append(role.id)
                    added.append(role.name)
                else:
                    already_added.append(role.name)
        message += errored
        if added:
            message += "\nAdded role(s): {roles}".format(roles=humanize_list(added))
        if already_added:
            message += "\nRole(s) already added: {roles}".format(
                roles=humanize_list(already_added)
            )
        if message:
            for line in pagify(message):
                await ctx.send(line)

    @autorole.command(name="remove")
    async def remove_roles(self, ctx: commands.Context, *roles: discord.Role):
        """Remove a role to give.

        You can give more than one role to add.
        """
        if not roles:
            return await ctx.send_help()
        message = ""
        removed = []
        not_found = []
        async with self.config.guild(ctx.guild).autoroles() as roles_list:
            for role in roles:
                if role.id in roles_list:
                    roles_list.remove(role.id)
                    removed.append(role.name)
                else:
                    not_found.append(role.name)
        if not_found:
            message += "\nRole(s) not found in autorole list: {roles}".format(
                roles=humanize_list(not_found)
            )
        if removed:
            message += "\nRole(s) remove from autorole list: {roles}".format(
                roles=humanize_list(removed)
            )
        if message:
            for line in pagify(message):
                await ctx.send(line)

    @autorole.command(name="list")
    async def list_roles(self, ctx: commands.Context):
        """List all roles that will be given."""
        all_roles = await self.config.guild(ctx.guild).autoroles()
        maybe_not_found = []
        message = ""
        for role in all_roles:
            fetched_role = ctx.guild.get_role(role)
            if not fetched_role:
                maybe_not_found.append(fetched_role.id)
                continue
            message += "- {name} (`{id}`).\n".format(name=fetched_role.name, id=fetched_role.id)
        if maybe_not_found:
            clean_list = list(set(all_roles) - set(maybe_not_found))
            await self.config.guild(ctx.guild).autoroles.set(clean_list)
            message += "\nSome roles has been removed since I was unable to find them."
        if message:
            for line in pagify(message):
                await ctx.send(line)
        else:
            await ctx.send("No role has been added.")

    # Agreeing command

    @commands.command(name="agree", aliases=["verify"])
    @commands.bot_has_permissions(manage_roles=True, manage_messages=True)
    async def verify_agree(self, ctx: commands.Context):
        """
        Agreeing to this means you understand the rules of the server.
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
        created_on = "{}\n({} days ago)".format(member_created, since_created)
        joined_on = "{}\n({} days ago)".format(member_joined, since_joined)
        author_avatar = author.avatar_url_as(static_format="png")

        data = await self.config.guild(ctx.guild).all()
        log_config = data["logs"]
        role_config = (data["temprole"], data["autoroles"])
        if role_config.count(None) == 2:
            await ctx.send(
                (
                    "Sorry, there is no role configuration set. Please contact the moderation "
                    "team of this server."
                ),
                delete_after=60,
            )
            self.log.warning("No role set. Unable to process verification.")
            return

        try:
            result = await self._handle_role(author)
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send(
                "Error: I am unable to remove your role, please contact the moderation team."
            )
            return self.log.warning("Error: No permissions to remove roles.")
        except discord.HTTPException as e:
            return self.log.warning("HTTPException: {} - {}".format(e.status, e.code))
        if log_config is not None:
            embed = discord.Embed(color=discord.Color.green())
            embed.title = "{}#{} - Verified".format(author.name, author.discriminator)
            embed.set_thumbnail(url=author_avatar)
            embed.set_footer(text="User ID: {}".format(author.id))
            embed.add_field(name="Account Creation:", value=created_on, inline=True)
            embed.add_field(name="Joined Date:", value=joined_on, inline=True)
            embed.add_field(name="Status:", value=result[1], inline=True)
            try:
                await ctx.bot.get_channel(log_config).send(embed=embed)
            except discord.Forbidden:
                return self.log.warning(
                    "Error: Unable to send log message to {}".format(
                        ctx.bot.get_channel(log_config)
                    )
                )
            except discord.HTTPException as e:
                return self.log.warning("HTTPException: {} - {}".format(e.status, e.code))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if await self.bot.cog_disabled_in_guild(self, member.guild):
            return False

        toggle = await self.config.guild(member.guild).toggle()
        role_config = await self.config.guild(member.guild).temprole()
        if toggle is False:
            return False

        if role_config is not None:
            role = discord.utils.get(member.guild.roles, id=int(role_config))
            try:
                await member.add_roles(role, reason="New Member, Needs to Verify.")
            except discord.Forbidden:
                return self.log.warning("Unable to grant roles to new joiner.")
            except discord.HTTPException as e:
                return self.log.warning("HTTPException: {} - {}".format(e.status, e.code))

    async def _handle_role(self, member: discord.Member) -> tuple:
        """Function to give and/or remove role from member.
        This will automatically grab roles from server's config.

        Parameters:
            member: discord.Member, The member we will act on.

        Returns:
            In a tuple:
            - bool: True if adding/remove role succeeded, else False.
            - str: A string to use for logs purpose.

        Raise:
            discord.Forbidden: Missing permissions to do role handling.
        """
        list_to_add = await self.config.guild(member.guild).autoroles()
        list_to_remove = await self.config.guild(member.guild).temprole()
        actions = []
        if list_to_add:
            for role in list_to_add:
                to_add = member.guild.get_role(role)
                await member.add_roles(to_add, reason="Adding auto role by Verify.")
            actions.append(
                "added automatically role{plural}".format(
                    plural="s" if len(list_to_add) > 1 else ""
                )
            )
        if list_to_remove:
            to_remove = member.guild.get_role(list_to_remove)
            if to_remove in member.roles:
                await member.remove_roles(to_remove, reason="Removing temporary role by Verify.")
                actions.append("removed temporary role")
        return (
            True,
            humanize_list(actions).capitalize() if actions else "No action taken.",
        )

    async def _maybe_update_config(self):
        if not await self.config.version():  # We never had a version before
            guild_dict = await self.config.all_guilds()
            async for guild_id, info in AsyncIter(guild_dict.items()):
                old_temporary_role = info.get("role", None)
                if old_temporary_role:
                    await self.config.guild_from_id(guild_id).temprole.set(old_temporary_role)
                    await self.config.guild_from_id(guild_id).role.clear()
            await self.config.version.set("1.0.0")
