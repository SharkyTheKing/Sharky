import discord
from redbot.core import commands, checks, modlog
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core.utils.mod import get_audit_reason


class SharkyMod(commands.Cog):
    """Sharky Moderation Tools"""

    __author__ = "Sharky The King"
    __version__ = "2.0.1"

    #  Sharky's Userinfo twist
    @commands.command(name="sharkinfo", aliases=["pinfo"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def sharkinfo(self, ctx, *, member: discord.Member = None):
        """
        User information with Sharky's twist
        """
        author = ctx.author
        if not member:
            member = author
        guild = ctx.guild
        member_mention = member.mention
        member_disc = member.discriminator
        member_name = member.name
        member_id = member.id
        member_avatar = member.avatar_url_as(static_format="png")
        member_voice = member.voice
        member_bot = member.bot

        member_role = sorted(member.roles, reverse=True)[:-1]
        if member_role:
            member_role = ", ".join([x.mention for x in member_role])
        joined_at = member.joined_at
        member_joined = member.joined_at.strftime("%d %b %Y %H:%M")
        since_joined = (ctx.message.created_at - joined_at).days
        member_created = member.created_at.strftime("%d %b %Y %H:%M")
        since_created = (ctx.message.created_at - member.created_at).days
        created_on = ("{}\n({} days ago)").format(member_created, since_created)
        joined_on = ("{}\n({} days ago)").format(member_joined, since_joined)
        member_number = (
            sorted(guild.members, key=lambda m: m.joined_at or ctx.message.created_at).index(
                member
            )
            + 1
        )
        notice = f"Member #{member_number}"
        embed = discord.Embed(color=0xEE2222, title=f"{member_name}'s information")
        embed.add_field(
            name="Name:", value=f"{member_mention}\n{member_name}#{member_disc}", inline=True
        )
        embed.add_field(name="ID:", value=f"{member_id}", inline=True)
        if member_bot is True:
            embed.add_field(name="Bot:", value=f"{member_mention} is a bot", inline=False)
        embed.add_field(name="Account Creation:", value=f"{created_on}", inline=True)
        embed.add_field(name="Joined Date:", value=f"{joined_on}", inline=True)
        embed.add_field(name="Roles:", value=f"{member_role}", inline=False)
        if member_voice and member_voice.channel:
            embed.add_field(
                name="Current voice channel",
                value="<#{0.id}> (ID: {0.id})".format(member_voice.channel),
                inline=False,
            )
        embed.set_footer(text=f"{notice}")
        embed.set_thumbnail(url=member_avatar)
        embed.set_author(name=f"{member_name}#{member_disc}", icon_url=f"{member_avatar}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(ban_members=True, embed_links=True)
    @checks.mod_or_permissions(ban_members=True)
    @commands.guild_only()
    async def findban(self, ctx, *, banneduser: int):
        """
        Find if a user is banned on the server or not

        If you don't know how to grab a userid, please click [here](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)
        """
        guild, bot = ctx.guild, ctx.bot
        embed = discord.Embed(color=0xEE2222)
        x_emote = "https://i.imgur.com/rBWVEUu.png"
        ban_hammer = "https://i.imgur.com/Gp2bamf.png"
        try:
            member = await bot.fetch_user(banneduser)
        except discord.NotFound:  # Not a valid user
            embed.set_thumbnail(url=x_emote)
            embed.title = "Unknown User"
            embed.description = f"{banneduser} is not a valid user.\n\nPlease make sure you're using a correct [UserID.](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)"
            return await ctx.send(embed=embed)
        case_amount = await modlog.get_cases_for_member(
            bot=ctx.bot, guild=ctx.guild, member=member
        )
        try:
            ban_info = await guild.fetch_ban(member)
            embed.set_thumbnail(url=ban_hammer)
            embed.add_field(name="User Found:", value=f"{member}\n({member.id})")
            embed.add_field(name="Case Amount:", value=len(case_amount))
            embed.add_field(name="Ban Reason:", value=ban_info[0], inline=False)
        except discord.NotFound:  # Not Banned
            embed.set_thumbnail(url=x_emote)
            embed.title = "Ban **NOT** Found"
            embed.add_field(
                name=f"{member} - ({member.id})", value="They are **NOT** banned from the server."
            )
        await ctx.send(embed=embed)

    #   User Avatar
    @commands.command(name="avatar", aliases=["av", "picture"])
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    @commands.guild_only()
    async def _avatar(self, ctx, *, user: discord.Member = None):
        """A user's avatar"""
        author = ctx.author
        if not user:
            user = author
        user_mention = user.mention
        user_disc = user.discriminator
        user_name = user.name
        user_id = user.id
        user_av = user.avatar_url_as(static_format="png")
        joined_at = user.joined_at
        user_joined = user.joined_at.strftime("%d %b %Y %H:%M")
        since_joined = (ctx.message.created_at - joined_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        since_created = (ctx.message.created_at - user.created_at).days

        created_on = ("{}\n({} days ago)").format(user_created, since_created)
        joined_on = ("{}\n({} days ago)").format(user_joined, since_joined)

        embed = discord.Embed(color=0xEE2222, title=f"Avatar Info")
        embed.add_field(name=f"User Info:", value=f"{user_mention}\n({user_id})")
        embed.add_field(name=f"Discord Name:", value=f"{user_name}#{user_disc}")
        embed.add_field(name=f"Account Age:", value=f"{created_on}")
        embed.add_field(name=f"Join Date:", value=f"{joined_on}")
        embed.set_image(url=user_av)
        await ctx.send(embed=embed)

    #   Display Roles
    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx):
        """
        Get the roles of the server\n\nCredit goes to
        [Trusty's ServerStats](https://github.com/TrustyJAID/Trusty-cogs)
        for the code
        """
        guild = ctx.guild
        msg = ""
        for role in sorted(guild.roles, reverse=True):
            msg += f"{role.mention} ({len(role.members)})\n"
            msg_list = []
        for page in pagify(msg, ["\n"]):
            if ctx.channel.permissions_for(ctx.me).embed_links:
                embed = discord.Embed(color=0xEE2222)
                embed.description = page
                embed.set_author(name=guild.name + ("Roles"), icon_url=guild.icon_url)
                msg_list.append(embed)
        await menu(ctx, msg_list, DEFAULT_CONTROLS)

    #   inroles command
    @commands.command()
    @commands.guild_only()
    async def inroles(self, ctx, *, role: discord.Role):
        """
        Curious?

        Well use this to find out who's in what role
        """
        member = discord.Member
        from redbot.core.utils.chat_formatting import pagify
        from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

        guild = ctx.guild
        msg = ""
        for member in role.members:
            msg += f"{member.mention} - {member.name}#{member.discriminator}\n"
            msg_list = []
        for page in pagify(msg, ["\n"]):
            embed = discord.Embed(color=0xEE2222)
            embed.description = page
            embed.set_author(name=guild.name + (f" Users in {role}"), icon_url=guild.icon_url)
            msg_list.append(embed)
        await menu(ctx, msg_list, DEFAULT_CONTROLS)

    @commands.group(pass_context=True, no_pm=True, invoke_without_command=True)
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    async def membercheck(self, ctx, *, param: str):
        """
        Checks who joined the server with that name
        """
        if ctx.invoked_subcommand is None:
            message = ""
            for x in ctx.guild.members:
                if param.lower() in x.display_name.lower() and x.joined_at.date() == date.today():
                    message += f"{x.display_name} - {x.id}\n"
            try:
                await ctx.send_interactive(
                    pagify(message if message else "No one joined with that name today")
                )
            except discord.HTTPException:
                pass
        else:
            pass

    @membercheck.command(pass_context=True, no_pm=True, name="ids")
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    async def ids(self, ctx, *, param: str):
        """
        Checks who joined the server with that name, but with IDs
        """
        if ctx.invoked_subcommand is None:
            message = ""
            for x in ctx.guild.members:
                if param.lower() in x.display_name.lower() and x.joined_at.date() == date.today():
                    message += f"{x.id}\n"
            try:
                await ctx.send_interactive(
                    pagify(message if message else "No one joined with that name today")
                )
            except discord.HTTPException:
                pass
        else:
            pass

    @membercheck.command(pass_context=True, no_pm=True, name="settime")
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    async def settime(
        self, ctx, param: str, day: Optional[int], month: Optional[int], year: Optional[int]
    ):
        """
        testing this out
        """
        if ctx.invoked_subcommand is None:
            dates = datetime.today()
            message = ""
            currentMonth = datetime.now().month
            currentYear = datetime.now().year
            currentDay = datetime.now().day
            time = date(
                year if year else currentYear,
                month if month else currentMonth,
                day if day else currentDay,
            )
            for x in ctx.guild.members:
                if param.lower() in x.display_name.lower() and x.joined_at.date() == time:
                    message += f"{x.display_name} - {x.id}\n"
            if dates is not None:
                try:
                    await ctx.send(message)
                except discord.HTTPException:
                    await ctx.send("No one joined with that name on {}".format(time))
            else:
                await ctx.send("Something happened, didn't properly do dates right.")
        else:
            pass
