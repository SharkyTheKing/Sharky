import discord
from redbot.core import checks, commands, modlog

BASECOG = getattr(commands, "Cog", object)

X_EMOTE = "https://i.imgur.com/rBWVEUu.png"
BAN_HAMMER = "https://i.imgur.com/Gp2bamf.png"


class SharkyTools(BASECOG):
    """
    Tools built by Sharky The King
    """

    __author__ = ["SharkyTheKing"]
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    @commands.command()
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def uav(self, ctx, *, user):
        """Get a user's avatar even if they aren't on the server"""
        try:
            user_acc = await ctx.bot.fetch_user(user)
            user_av, user_name, user_disc, = (
                user_acc.avatar_url_as(static_format="png"),
                user_acc.name,
                user_acc.discriminator,
            )
            embed = discord.Embed(
                color=await ctx.embed_color(), title=f"Avatar Info: {user_name}#{user_disc}"
            )
            embed.set_image(url=user_av)
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Please use a valid UserID")

    @commands.command(name="avatar", aliases=["av", "picture"])
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    async def _avatar(self, ctx, *, user: discord.Member = None):
        """A user's avatar"""
        if not user:
            user = ctx.author
        user_mention, user_disc, user_name, user_id, user_av = (
            user.mention,
            user.discriminator,
            user.name,
            user.id,
            user.avatar_url_as(static_format="png"),
        )
        joined_at = user.joined_at
        user_joined = user.joined_at.strftime("%d %b %Y %H:%M")
        since_joined = (ctx.message.created_at - joined_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        since_created = (ctx.message.created_at - user.created_at).days
        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        embed = discord.Embed(color=0xEE2222, title=f"Avatar Info")
        embed.add_field(name=f"User Info:", value=f"{user_mention}\n({user_id})")
        embed.add_field(name=f"Discord Name:", value=f"{user_name}#{user_disc}")
        embed.add_field(name=f"Account Age:", value=f"{created_on}")
        embed.add_field(name=f"Join Date:", value=f"{joined_on}")
        embed.set_image(url=user_av)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def age(self, ctx, *, user: discord.Member = None):
        """Find out the person's account age and join date!"""
        if not user:
            user = ctx.author
        user_mention, user_name, user_disc, user_av = (
            user.mention,
            user.name,
            user.discriminator,
            user.avatar_url_as(static_format="png"),
        )
        joined_at = user.joined_at
        user_joined = user.joined_at.strftime("%d %b %Y %H:%M")
        since_joined = (ctx.message.created_at - joined_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        since_created = (ctx.message.created_at - user.created_at).days
        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        bot_is = user.bot
        embed = discord.Embed(
            color=await ctx.embed_color(), title=f"{user_name}#{user_disc}'s Account Date:"
        )
        embed.add_field(name=f"Account Age:", value=f"{created_on}")
        embed.add_field(name=f"Join Date:", value=f"{joined_on}")
        if bot_is is True:
            embed.add_field(name=f"Bot Found:", value=f"{user_mention} is a bot")
        embed.set_thumbnail(url=user_av)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(ban_members=True, embed_links=True)
    @checks.mod_or_permissions(ban_members=True)
    @commands.guild_only()
    async def findban(self, ctx, *, banneduser: int):
        """
        Find if a user is banned on the server or not

        If you don't know how to grab a userid, please click
        [here](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)
        """
        guild, bot = ctx.guild, ctx.bot
        embed = discord.Embed(color=0xEE2222)
        member = ctx.bot.get_user(banneduser)  # look into more
        if not member:
            try:
                member = await bot.fetch_user(banneduser)
            except discord.NotFound:  # Not a valid user
                embed.set_thumbnail(url=X_EMOTE)
                embed.title = "Unknown User"
                embed.description = (
                    f"{banneduser} is not a valid user.\n\nPlease make sure you're using a "
                    "correct [UserID](https://support.discordapp.com/hc/en-us/articles/"
                    "206346498-Where-can-I-find-my-User-Server-Message-ID-)."
                )
                return await ctx.send(embed=embed)
        case_amount = await modlog.get_cases_for_member(
            bot=ctx.bot, guild=ctx.guild, member=member
        )
        try:
            ban_info = await guild.fetch_ban(member)
            embed.set_thumbnail(url=BAN_HAMMER)
            embed.add_field(name="User Found:", value=f"{member}\n({member.id})")
            embed.add_field(name="Case Amount:", value=str(len(case_amount)))
            embed.add_field(name="Ban Reason:", value=ban_info[0], inline=False)
        except discord.NotFound:  # Not Banned
            embed.set_thumbnail(url=X_EMOTE)
            embed.title = "Ban **NOT** Found"
            embed.add_field(
                name=f"{member} - ({member.id})", value="They are **NOT** banned from the server."
            )
        await ctx.send(embed=embed)
