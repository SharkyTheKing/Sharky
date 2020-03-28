import discord
from typing import Optional
from redbot.core import Config, checks, commands
from typing import Union
import re

BaseCog = getattr(commands, "Cog", object)


class ReportSystem(BaseCog):
    """
    Report System

    Members can type `[p]report <user> <reason>` and it'll show up in your selected channel!
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=923485973)
        def_guilds = {"report": None, "emote": False, "verified_roles": []}
        self.config.register_guild(**def_guilds)

    #   Report command
    @commands.guild_only()
    @commands.cooldown(2, 15, commands.BucketType.user)
    @commands.command()
    async def report(self, ctx, member: Optional[discord.Member], *, reason: str):
        """
        Report a member to the moderation team!

        Examples:
        `[p]report @Sharky The King#0001 For being a shark`
        `[p]report 223391425302102016 for being a shark`
        `[p]report "Sharky The King" for being a shark`
        """
        author = ctx.author
        bot = ctx.bot
        guild = ctx.guild
        color = await ctx.embed_color()
        log = await self.config.guild(guild).report()
        roles = await self.config.guild(guild).verified_roles()
        role_list = []
        r = ""
        rm = ""
        mem = ""
        if member is None:
            mem = "No users detected"
        else:
            if member.nick is not None:
                mem += f"{member.mention}\n**Nick**: {member.nick}\n**ID**: {member.id}"
            else:
                mem += f"{member.mention}\n**ID**: {member.id}"
        for role in author.roles:
            role_list.append(role)
            if role_list in roles:
                if author in rm.members:
                    color = rm.color
                else:
                    pass
            else:
                rm = None
        try:
            await ctx.message.delete()
        except (discord.HTTPException, discord.Forbidden):
            pass
        embed = discord.Embed(color=color)
        embed.description = f"**Reason**:\n{reason}"
        embed.timestamp = ctx.message.created_at
        embed.add_field(name="User", value=mem)
        if member is None or member.voice is None:
            embed.add_field(name="Channel", value=f"{ctx.channel.mention}")
        else:
            embed.add_field(
                name="Channel",
                value=f"{ctx.channel.mention}\n**VC**: {member.voice.channel.mention}",
            )
        embed.add_field(name="Author", value=f"{ctx.author.mention}")
        if member is not None:
            member_avatar = member.avatar_url_as(static_format="png")
            embed.set_thumbnail(url=member_avatar)
        else:
            pass
        try:
            if log is None:
                await ctx.author.send(
                    "Sorry, but it appears no one has setup a report channel. Please notify the moderators of the server!"
                )
            else:
                await bot.get_channel(log).send(embed=embed)
                await ctx.author.send(
                    "Thank you for your report. The moderation team has received this."
                )
        except (discord.HTTPException, discord.Forbidden):
            pass

    @commands.command()
    @checks.mod()
    async def check(self, ctx, member: discord.Member):
        """
        Sends a message to the user that you have verified/checked the report

        A unique way of sending a message back to the members to let them know, you checked the reports
        """
        embed = discord.Embed(color=await ctx.embed_color())
        embed.title = "Report checked!"
        embed.timestamp = ctx.message.created_at
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/575846797709279262/616887240101986344/OS-Fundraising-ChocolateChipTop_whitespace.png"
        )
        embed.description = "Your report has been checked by a moderator! Thank you for sending it in. Have a cookie! \N{COOKIE}"
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def reportset(self, ctx):
        """Manage reports"""
        pass

    @reportset.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def channel(self, ctx, channel: Optional[discord.TextChannel]):
        """Set a channel to be the channel reports get posted into"""
        if channel is not None:
            await self.config.guild(ctx.guild).report.set(channel.id)
            await ctx.send(f"Made {channel.mention} the reporting channel.")
        else:
            await self.config.guild(ctx.guild).report.set(None)
            await ctx.send(f"Disabled the report command and removed the reporting channel.")

    @reportset.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def emote(self, ctx, toggle: Optional[bool]):
        """
        Sets it whether the bot automatically puts reactions for each report sent

        Up is confirming it's a valid report
        Down is confirming it's not a valid report
        Question means you're unsure of the report or are in question of it
        X means it's been too long to look into
        """
        emote = self.config.guild(ctx.guild).emote
        if toggle is None:
            await ctx.send("The current settings is set to {}".format(await emote()))
        elif toggle is True:
            await emote.set(True)
            await ctx.send("The setting is now set to {}".format(await emote()))
        elif toggle is False:
            await emote.set(False)
            await ctx.send("The setting is now set to {}".format(await emote()))

    @reportset.command()
    async def role(self, ctx, *, role: discord.Role):
        """
        Selects what roles you want to be seen as priority in reports

        These roles will have a different color report and will look like the role color
        """
        guild = ctx.guild
        status = "Something borked, blame fish"
        if role.id in await self.config.guild(guild).verified_roles():
            async with self.config.guild(guild).verified_roles() as rol:
                rol.remove(role.id)
                status = "Removed"
                status = "Added"
        else:
            async with self.config.guild(guild).verified_roles() as rol:
                rol.append(role.id)
                status = "Added"
        await ctx.send("New status for {} set! - {}".format(role.mention, status))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user):
        """
        Detects for when someone adds reaction
        """
        if reaction.message.guild is not None:
            report = await self.config.guild(reaction.message.guild).report()
            emote = self.config.guild(reaction.message.guild).emote()
            if report is None:
                pass
            else:
                chan = discord.utils.get(reaction.message.guild.channels, id=int(report))
                if reaction.message.channel != chan:
                    return False
                elif reaction.message.channel == chan:
                    if user == self.bot.user:
                        return False
                    else:
                        if (
                            reaction.message.embeds
                            and "Moderator Claimed:" in str(reaction.message.embeds[0].fields)
                            or "has claimed this." in reaction.message.content
                            or not reaction.message.embeds
                        ):
                            return False
                        else:
                            try:
                                react = reaction.message
                                em = react.embeds[0]
                                em.add_field(
                                    name="Moderator Claimed:",
                                    value="{} ({}) has claimed this.".format(
                                        user.display_name, user.id
                                    ),
                                )
                                await react.edit(embed=em)
                                if await emote is True:
                                    await react.clear_reactions()
                                else:
                                    pass
                            except IndexError:
                                try:
                                    react = reaction.message
                                    await react.edit(
                                        content="{} has claimed this.".format(user.display_name)
                                    )
                                    if await emote is True:
                                        await react.clear_reactions()
                                    else:
                                        pass
                                except:
                                    pass
                            except discord.Forbidden:
                                pass
        else:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        On Message system
        """
        await self._build_reactions(message)

    #        await self._build_report_explination(message)

    #    async def _build_report_explination(self, message):
    #        author = message.author
    #        regex = re.compile(r"(?i)(how (do i|to|do you) report)").search(message.content)
    #        if regex is not None:
    #            if (
    #                author == self.bot.user
    #                or message.channel.permissions_for(message.author).manage_messages is True
    #            ):
    #                pass
    #            else:
    #                try:
    #                    await author.send(
    #                        'Hello {},\nNoticed you were asking how to report people. To report someone **in Discord** Please read the following examples:\n`{}report @Sharky The King#0001 For being a shark`\n`{}report 223391425302102016 for being a shark`\n`{}report "Sharky The King" for being a shark`\n\nTo report someone in-game: Please do not report players here. Abusive players should be reported in-game (Esc -> Report Player) or using the instructions on this page <https://epicgames.helpshift.com/a/fortnite/?b_id=9729&p=all&s=battle-royale&f=how-do-i-report-bad-player-behavior-in-fortnite&l=en>'.format(
    #                            author.mention
    #                        )
    #                    )
    #                except:
    #                    pass
    #        else:
    #            pass

    async def _build_reactions(self, message):
        author = message.author
        if message.guild is not None:
            report = await self.config.guild(message.guild).report()
            emote = self.config.guild(message.guild).emote
            if report is None:
                return False
            else:
                if await emote() is True:
                    if author == self.bot.user:
                        if (
                            message.embeds
                            and "Reason:" in str(message.embeds[0].descriptions)
                            or "Author" in message.content
                        ):
                            chan = discord.utils.get(message.guild.channels, id=int(report))
                            if message.channel == chan:
                                react = ["👋", "👍", "👎", "❓", "❌"]
                                for emotes in react:
                                    await message.add_reaction(emotes)
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
        else:
            return False
