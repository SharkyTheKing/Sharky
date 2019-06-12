import discord
from redbot.core import commands, checks, modlog, Config
from redbot.core.bot import Red


class Silence(commands.Cog):
    """
    Mutes people with designated roles.

    Don't forget to setup your muted roles first with silenceset
    If you have any suggestions please hit me up on my [repo](https://github.com/SharkyTheKing/Sharky/issues/new)
    """

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=12343221)

        def_guilds = {"mrole": 69696969, "vcrole": 68686868}
        self.config.register_guild(**def_guilds)

    @commands.group(aliases=["scs"])
    @commands.bot_has_permissions(manage_roles=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def silenceset(self, ctx):
        """Adjust mute role for Text and Voice"""
        pass

    @silenceset.command()
    @commands.bot_has_permissions(manage_roles=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def text(self, ctx, role: discord.Role = None):
        """ Set's the muted role"""
        if role is None:
            await self.config.guild(ctx.guild).mrole.set(None)
            await ctx.send(f"Cleared the muted role")
        else:
            await self.config.guild(ctx.guild).mrole.set(role.id)
            await ctx.send(f"Set the muted role to {role.mention}")

    @silenceset.command()
    @commands.bot_has_permissions(manage_roles=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def vc(self, ctx, role: discord.Role = None):
        """ Set's the VC muted role"""
        if role is None:
            await self.config.guild(ctx.guild).vcrole.set(None)
            await ctx.send(f"Cleared the muted role")
        else:
            await self.config.guild(ctx.guild).vcrole.set(role.id)
            await ctx.send(f"Set the muted role to {role.mention}")

    @silenceset.command()
    @commands.bot_has_permissions(manage_roles=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def list(self, ctx):
        """Get the list of all roles"""
        mmrole = await self.config.guild(ctx.guild).mrole()
        vvcrole = await self.config.guild(ctx.guild).vcrole()
        mrole = "e"
        vcrole = "e"
        if mmrole is None:
            mrole = "No Text Role set yet"
        else:
            mrole = discord.utils.get(ctx.guild.roles, id=int(mmrole))
        if vvcrole is None:
            vcrole = "No Voice Role set yet"
        else:
            vcrole = discord.utils.get(ctx.guild.roles, id=int(vvcrole))
        e = discord.Embed(color=int("0xEE2222", 16))
        e.title = f"Moderation settings for {ctx.guild.name}"
        e.description = f"**Text Role**: {mrole}\n **Voice Role**: {vcrole}"
        await ctx.send(embed=e)

    @commands.command(aliases=["scr"])
    @commands.bot_has_permissions(manage_roles=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def silencerole(self, ctx):
        """
        Gets the list of users in the roles

        Alias: scr
        """
        guild = ctx.guild
        get_text = await self.config.guild(ctx.guild).mrole()
        asf = guild.get_role(get_text)
        get_vc = await self.config.guild(ctx.guild).vcrole()
        avf = guild.get_role(get_vc)
        msg = ""
        msgs = ""
        try:
            for member in asf.members:
                msg += f"{member.mention}\n"
            for members in avf.members:
                msgs += f"{members.mention}\n"
            e = discord.Embed(color=int("0xEE2222", 16))
            e.title = "People in Text role:"
            e.description = f"\n{msg}\n **People in Voice Role:**\n{msgs}"
            await ctx.send(embed=e)
        except AttributeError:
            await ctx.send("You should prob make sure you have roles set")

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def silence(self, ctx, user: discord.Member, *, reason=None):
        """Mutes the user from Text Channels"""
        bot = ctx.bot
        guild = ctx.guild
        if reason is None:
            reason = f"No reason provided"
        role_id = await self.config.guild(ctx.guild).mrole()
        if role_id is None:
            role = discord.utils.get(ctx.guild.roles, id=int(1))
        else:
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
        try:
            await user.add_roles(role, reason=f"[{ctx.author}] {reason}")
            await ctx.send(f"Muted {user.name}")
            await modlog.create_case(
                bot,
                guild,
                ctx.message.created_at,
                "cmute",
                user,
                ctx.message.author,
                reason,
                until=None,
                channel=None,
            )
        except AttributeError:
            await ctx.send(
                "Yeah, you need to setup the roles with {}silenceset".format(ctx.prefix)
            )
        except discord.Forbidden:
            await ctx.send("wot")

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def vsilence(self, ctx, user: discord.Member, *, reason=None):
        """ Mutes the user from Voice Call"""
        bot = ctx.bot
        guild = ctx.guild
        if reason is None:
            reason = "No reason provided"
        role_id = await self.config.guild(ctx.guild).vcrole()
        if role_id is None:
            role = discord.utils.get(ctx.guild.roles, id=int(1))
        else:
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
        try:
            await user.add_roles(role, reason=f"[{ctx.author}] {reason}")
            await ctx.send(f"Muted {user.name}")
            await modlog.create_case(
                bot,
                guild,
                ctx.message.created_at,
                "vmute",
                user,
                ctx.message.author,
                reason,
                until=None,
                channel=None,
            )
        except AttributeError:
            await ctx.send(
                "Yeah, you need to setup the roles with {}silenceset".format(ctx.prefix)
            )
        except discord.Forbidden:
            await ctx.send("wot")

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def unsilence(self, ctx, user: discord.Member, *, reason=None):
        """Unmutes the User from Text Channels"""
        bot = ctx.bot
        guild = ctx.guild
        if reason is None:
            reason = "No reason provided"
        role_id = await self.config.guild(ctx.guild).mrole()
        if role_id is None:
            role = discord.utils.get(ctx.guild.roles, id=int(1))
        else:
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
        try:
            await user.remove_roles(role, reason=f"[{ctx.author}] {reason}")
            await ctx.send(f"Unmuted {user.name}")
            await modlog.create_case(
                bot,
                guild,
                ctx.message.created_at,
                "cunmute",
                user,
                ctx.message.author,
                reason,
                until=None,
                channel=None,
            )
        except AttributeError:
            await ctx.send(
                "Yeah, you need to setup the roles with {}silenceset".format(ctx.prefix)
            )
        except discord.Forbidden:
            await ctx.send("wot")

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def unvsilence(self, ctx, user: discord.Member, *, reason=None):
        """Unmutes the User from Voice Calls"""
        bot = ctx.bot
        guild = ctx.guild
        if reason is None:
            reason = "No reason provided"
        role_id = await self.config.guild(ctx.guild).vcrole()
        if role_id is None:
            role = discord.utils.get(ctx.guild.roles, id=int(1))
        else:
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
        try:
            await user.remove_roles(role, reason=f"[{ctx.author}] {reason}")
            await ctx.send(f"Unmuted {user.name}")
            await modlog.create_case(
                bot,
                guild,
                ctx.message.created_at,
                "vunmute",
                user,
                ctx.message.author,
                reason,
                until=None,
                channel=None,
            )
        except AttributeError:
            await ctx.send(
                "Yeah, you need to setup the roles with {}silenceset".format(ctx.prefix)
            )
        except discord.Forbidden:
            await ctx.send("wot")

    @commands.command(aliases=["mutes"])
    @commands.bot_has_permissions(manage_roles=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def silences(self, ctx, user: discord.Member, *, reason=None):
        """
        Uses both Text and Voice mutes on the User

        Alias: mutes
        """
        bot = ctx.bot
        guild = ctx.guild
        if reason is None:
            reason = "No reason provided"
        role_id1 = await self.config.guild(ctx.guild).mrole()
        role_id2 = await self.config.guild(ctx.guild).vcrole()
        if role_id1 is None:
            role1 = discord.utils.get(ctx.guild.roles, id=int(1))
        else:
            role1 = discord.utils.get(ctx.guild.roles, id=int(role_id1))
        if role_id2 is None:
            role2 = discord.utils.get(ctx.guild.roles, id=int(2))
        else:
            role2 = discord.utils.get(ctx.guild.roles, id=int(role_id2))
        try:
            await user.add_roles(role1, role2, reason=f"[{ctx.author}] {reason}")
            await ctx.send(f"Muted {user.name}")
            await modlog.create_case(
                bot,
                guild,
                ctx.message.created_at,
                "cmute",
                user,
                ctx.message.author,
                "Voice muted and Channel muted:\n" + reason,
                until=None,
                channel=None,
            )
        except AttributeError:
            await ctx.send(
                "Yeah, you need to setup the roles with {}silenceset".format(ctx.prefix)
            )
        except discord.Forbidden:
            await ctx.send("wot")

    @commands.command(aliases=["unmutes"])
    @commands.bot_has_permissions(manage_roles=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def unsilences(self, ctx, user: discord.Member, *, reason=None):
        """
        Uses both Text and Voice unmutes on the User

        Alias: unmutes
        """
        bot = ctx.bot
        guild = ctx.guild
        if reason is None:
            reason = "No reason provided"
        role_id1 = await self.config.guild(ctx.guild).mrole()
        role_id2 = await self.config.guild(ctx.guild).vcrole()
        if role_id1 is None:
            role1 = discord.utils.get(ctx.guild.roles, id=int(1))
        else:
            role1 = discord.utils.get(ctx.guild.roles, id=int(role_id1))
        if role_id2 is None:
            role2 = discord.utils.get(ctx.guild.roles, id=int(2))
        else:
            role2 = discord.utils.get(ctx.guild.roles, id=int(role_id2))
        try:
            await user.remove_roles(role1, role2, reason=f"[{ctx.author}] {reason}")
            await ctx.send(f"Unmuted {user.name}")
            await modlog.create_case(
                bot,
                guild,
                ctx.message.created_at,
                "cunmute",
                user,
                ctx.message.author,
                "Voice unmute and Channel unmute:\n" + reason,
                until=None,
                channel=None,
            )
        except AttributeError:
            await ctx.send(
                "Yeah, you need to setup the roles with {}silenceset".format(ctx.prefix)
            )
        except discord.Forbidden:
            await ctx.send("wot")

