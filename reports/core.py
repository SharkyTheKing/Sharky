import logging
from typing import Optional

import discord
from redbot.core import Config, checks, commands

BASECOG = getattr(commands, "Cog", object)
DEF_GUILD = {
    "report_channel": None,
    "emote_reactions": False,
    "claim_reports": False,
    "recieve_dms": [],
}

# TODO Add reportdm command to disable dms on reports. To avoid annoyed members.


class Reports(BASECOG):
    """
    Report system

    Members can type `[p]report <user> <reason>` and it'll show up in your selected channel!
    """

    __author__ = ["SharkyTheKing"]
    __version__ = "1.1.1"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2233914253021)
        self.config.register_guild(**DEF_GUILD)

        self.log = logging.getLogger("red.cogs.reports")

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    @commands.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(usage="")
    async def reportdm(self, ctx):
        """
        Enables/Disables the messages the bot sends on report

        By default this changes depending on your current setting.
        """
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        status = None
        async with self.config.guild(ctx.guild).recieve_dms() as dmreport:
            if ctx.author.id not in dmreport:
                dmreport.append(ctx.author.id)
                status = True
            else:
                dmreport.remove(ctx.author.id)
                status = False

        message = "Done. You will {status} receive DMs when you report".format(
            status="not" if status else "now"
        )

        try:
            await ctx.author.send(message)
        except discord.HTTPException:
            await ctx.send(message)

    @commands.guild_only()
    @commands.cooldown(2, 15, commands.BucketType.user)
    @commands.command(usage="<member> <reason>")
    async def report(self, ctx, member: Optional[discord.Member], *, reason: str):
        """
        Report a member

        Example: !report @SharkyTheKing#0001 Not being fishy enough.

        Arguments:
        `member`: The Discord member you want to report
        `reason`: The reason for the report
        """
        report_channel = await self.config.guild(ctx.guild).report_channel()
        if report_channel is None:
            try:
                return await ctx.author.send(
                    "We're sorry! The Moderation team on this server hasn't setup a report "
                    "channel yet. Please reach out to the moderation team and ask if they could "
                    "set one up!"
                )
            except (discord.Forbidden, discord.NotFound):
                pass

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException):
            self.log.info("Unable to delete message in {}".format(ctx.channel.name))

        await self.build_report_embeds(ctx, member, reason, report_channel)

    async def build_report_embeds(self, ctx, member, reason, report_channel):
        """
        Builds embeds for report

        If member is None. Default to no user
        """
        embed = discord.Embed()
        embed.description = "**Reason**:\n{}".format(reason)
        embed.timestamp = ctx.message.created_at

        if member is None:
            embed.add_field(name="User", value="No user detected.")
        else:
            embed.add_field(name="User", value="{}\n**ID**: {}".format(member.mention, member.id))

        if member is None or member.voice is None:
            embed.add_field(name="Channel", value=ctx.channel.mention)
        else:
            embed.add_field(
                name="Channel",
                value="{}\n**VC**: {}".format(ctx.channel.mention, member.voice.channel.mention),
            )

        if ctx.author is None:
            embed.add_field(name="Author", value="No Author Found")
        else:
            embed.add_field(name="Author", value=ctx.author.mention)

        await self.send_report_to_mods(ctx, embed, report_channel)

    async def send_report_to_mods(self, ctx, embed, report_channel):
        """
        Sending to channel
        """
        channel_report = self.bot.get_channel(report_channel)
        try:
            await channel_report.send(embed=embed)
        except discord.Forbidden:
            self.log.warning("Unable to send message in {}".format(channel_report))
        except discord.HTTPException as e:
            self.log.warning("HTTPException {} - {}".format(e.code, e.status))

        if ctx.author.id in await self.config.guild(ctx.guild).recieve_dms():
            return

        try:
            await ctx.author.send(
                "Thank you for your report. The moderation team has received your report."
            )
        except (discord.Forbidden, discord.HTTPException):
            self.log.info(
                "Unable to send message to {} - {}".format(ctx.author.name, ctx.author.id)
            )

    @report.error
    async def _report_error_handler(self, ctx, error):
        """Error handler for the report command"""
        if isinstance(error, commands.CommandOnCooldown):
            try:
                await ctx.message.delete()
            except (discord.errors.Forbidden, discord.errors.HTTPException):
                pass
            try:
                return await ctx.author.send(
                    "Your report has been rate limited. Please do not mass report."
                )
            except (discord.errors.Forbidden, discord.errors.HTTPException):
                pass
        else:
            await ctx.bot.on_command_error(ctx, error, unhandled_by_cog=True)

    @checks.mod_or_permissions(kick_members=True)
    @commands.group()
    async def reportset(self, ctx):
        """
        Manage reports system
        """
        pass

    @reportset.command(name="list")
    async def show_settings(self, ctx):
        """
        Displays report settings
        """
        guild_config = await self.config.guild(ctx.guild).all()
        report_channel = guild_config["report_channel"]
        emotes_toggle = guild_config["emote_reactions"]
        claim_toggle = guild_config["claim_reports"]

        embed = discord.Embed()
        embed.title = "{}'s Report Settings".format(ctx.guild.name)
        embed.add_field(
            name="Report Channel",
            value="<#{}>".format(report_channel) if report_channel else "No channel set",
            inline=False,
        )
        embed.add_field(
            name="Auto Emote Reaction", value="enabled" if emotes_toggle else "disabled"
        )
        embed.add_field(name="Moderation Claim", value="enabled" if claim_toggle else "disabled")

        await ctx.send(embed=embed)

    @reportset.command(name="reportclaim")
    async def report_claim(self, ctx, toggle: Optional[bool]):
        """
        Toggle report to be claimed.

        If this is toggled on, any reaction on any reports is immediately claimed by the moderator.
        """
        report_toggle = self.config.guild(ctx.guild).claim_reports
        if toggle is None:
            return await ctx.send(
                "Report claim are {}".format("enabled" if await report_toggle() else "disabled")
            )
        elif toggle is True:
            await report_toggle.set(True)
            return await ctx.send("The setting is now enabled.")
        elif toggle is False:
            await report_toggle.set(False)
            return await ctx.send("The setting is now disabled.")

    @reportset.command()
    async def channel(self, ctx, channel: Optional[discord.TextChannel]):
        """
        Sets the channel where reports will be posted into
        """
        if channel is None:
            await self.config.guild(ctx.guild).report_channel.set(None)
            return await ctx.send("Done. Cleared the report channel.")

        await self.config.guild(ctx.guild).report_channel.set(channel.id)
        await ctx.send("Done. Set {} to be the report channel.".format(channel.mention))

    @reportset.command()
    async def emotes(self, ctx, toggle: Optional[bool]):
        """
        Sets it whether the bot automatically puts reactions for each report sent

        Up is confirming it's a valid report
        Down is confirming it's not a valid report
        Question means you're unsure of the report or are in question of it
        X means it's been too long to look into
        """
        emotes_toggle = self.config.guild(ctx.guild).emote_reactions
        if toggle is None:
            return await ctx.send(
                "Emotes are {}".format("enabled" if await emotes_toggle() else "disabled")
            )
        elif toggle is True:
            await self.config.guild(ctx.guild).emote_reactions.set(True)
            return await ctx.send("The setting is now enabled")
        elif toggle is False:
            await self.config.guild(ctx.guild).emote_reactions.set(False)
            return await ctx.send("The setting is now disabled")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Auto-add reactions
        """
        if not message.guild:
            return

        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return

        report_channel = await self.config.guild(message.guild).report_channel()

        if await self.config.guild(message.guild).emote_reactions() is False:
            return False

        if report_channel is None:
            return False

        if message.author == self.bot.user:
            emote_channel = discord.utils.get(message.guild.channels, id=int(report_channel))
            if message.channel != emote_channel:
                return False

            reaction_emotes = ["👋", "👍", "👎", "❓", "❌"]
            for emotes in reaction_emotes:
                try:
                    await message.add_reaction(emotes)
                except discord.NotFound:
                    return  # No need to log if message was removed
                except (discord.Forbidden, discord.HTTPException):
                    self.log.info("Unable to react in {}".format(emote_channel))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """
        Detects for when someone adds reaction
        """
        if not reaction.message.guild:
            return

        if await self.bot.cog_disabled_in_guild(self, reaction.message.guild):
            return False

        if user.id == self.bot.user.id:
            return

        config_info = await self.config.guild(reaction.message.guild).all()
        if config_info["report_channel"] is None:
            return

        if config_info["claim_reports"] is False:
            return

        report_channel = discord.utils.get(
            reaction.message.guild.channels, id=int(config_info["report_channel"])
        )
        if reaction.message.channel != report_channel:
            return

        if (
            reaction.message.embeds
            and "Moderator Claimed:" in str(reaction.message.embeds[0].fields)
            or "has claimed this." in reaction.message.content
            or not reaction.message.embeds
        ):
            return

        message = reaction.message
        if message.author.id != self.bot.user.id:
            return

        try:
            embed = message.embeds[0]
            embed.add_field(
                name="Moderator Claimed:", value="{} ({})".format(user.mention, user.id)
            )
            await message.edit(embed=embed)
        except IndexError:
            await message.edit("{} ({}) has claimed this.".format(user.mention, user.id))

    # Reason for no try on editing is because we check if it's the bot's message before editing
